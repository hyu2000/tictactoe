from typing import List, Dict, Tuple, Any
import logging
import pickle
import enum
from collections import Counter


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# all ints
class CellState(enum.IntEnum):
    EMPTY = 0
    PLAYER_X = 1
    PLAYER_O = 2

    def reverse_role(self):
        if self == CellState.PLAYER_O:
            return CellState.PLAYER_X
        elif self == CellState.PLAYER_X:
            return CellState.PLAYER_O
        else:
            raise ValueError('Invalid role: ' + self)


# also ints, so that it's easy to compare with CellState
class GameResult(enum.IntEnum):
    """ constants of game result
    """
    UNFINISHED = 0
    X_WINS = CellState.PLAYER_X
    O_WINS = CellState.PLAYER_O
    DRAW = 3

    @staticmethod
    def from_role(role):
        if role == CellState.PLAYER_O:
            return GameResult.O_WINS
        elif role == CellState.PLAYER_X:
            return GameResult.X_WINS
        else:
            raise Exception('Invalid role: ' + role)

    def announce(self):
        return self.name


class StateCount(object):
    """ a utility class to count # game states
    """
    def __init__(self):
        pass

    @classmethod
    def P(cls, N, k):
        prod = 1
        for i in xrange(k):
            prod *= N - i
        return prod

    @classmethod
    def C(cls, N, k):
        return cls.P(N, k) / cls.P(k, k)

    @classmethod
    def num_states_for_step(self, i):
        num_O = i / 2
        num_X = i - num_O
        return self.C(9, num_X) * self.C(9 - num_X, num_O)

    @classmethod
    def total_num_states_for_X(self):
        return sum([self.num_states_for_step(i) for i in xrange(1, 10, 2)])

    @classmethod
    def total_num_states_for_O(self):
        return sum([self.num_states_for_step(i) for i in xrange(2, 10, 2)])


class Board(object):
    """
    Wrap a bunch helper functions around the actual board representation, which is a
      list of rows, each row a list of 3 ints.
    """

    BOARD_FORMAT_WITH_INDEX = '\n'.join([
        '----------------------------',
        '| {0} 0| {1} 1| {2} 2|',
        '|--------------------------|',
        '| {3} 3| {4} 4| {5} 5|',
        '|--------------------------|',
        '| {6} 6| {7} 7| {8} 8|',
        '----------------------------'])

    BOARD_FORMAT = '\n'.join([
        '----------------------------',
        '| {0} | {1} | {2} |',
        '|--------------------------|',
        '| {3} | {4} | {5} |',
        '|--------------------------|',
        '| {6} | {7} | {8} |',
        '----------------------------'])

    def __init__(self, init_state=None):
        if not init_state:
            EMPTY = CellState.EMPTY
            self.board = [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]
        else:
            self.board = init_state

    def print_board_with_last_move(self, row, col):
        NAMES = [' ', 'X', 'O']

        cells = []
        for irow in range(3):
            for icol in range(3):
                char = NAMES[self.board[irow][icol]]
                if irow == row and icol == col:
                    char = '(%s)' % char
                cells.append(char.center(5))

        print self.BOARD_FORMAT_WITH_INDEX.format(*cells)

    @staticmethod
    def empty_score_board():
        return [['', '', ''], ['', '', ''], ['', '', '']]

    @staticmethod
    def print_score_board_with_highlight(board, row, col):
        cells = []
        for irow in range(3):
            for icol in range(3):
                s = board[irow][icol]
                if irow == row and icol == col:
                    s = '(%s)' % s
                cells.append(s.center(10))

        print Board.BOARD_FORMAT.format(*cells)

    def print_board(self):
        self.print_board_with_last_move(-1, -1)

    def num_stones(self):
        return 9 - self.num_empty_squares()

    def num_empty_squares(self):
        num = sum([val == CellState.EMPTY for row in self.board for val in row])
        return num

    def next_empty_square(self):
        """ generator over all empty spots on board
        :return: row, col
        """
        for irow, row in enumerate(self.board):
            for icol, stone in enumerate(row):
                if stone == CellState.EMPTY:
                    yield irow, icol

    def kth_empty_square(self, k):
        for i, (row, col) in enumerate(self.next_empty_square()):
            if i == k:
                return row, col
        raise Exception('Invalid k=%d' % k)

    def evaluate(self):
        """evaluate board -> winning player, DRAW, or EMPTY
        :return:
        """
        board = self.board
        for i in range(3):
            if board[i][0] != CellState.EMPTY and board[i][0] == board[i][1] and board[i][0] == board[i][2]:
                return GameResult.from_role(board[i][0])
            if board[0][i] != CellState.EMPTY and board[0][i] == board[1][i] and board[0][i] == board[2][i]:
                return GameResult.from_role(board[0][i])
        if board[0][0] != CellState.EMPTY and board[0][0] == board[1][1] and board[0][0] == board[2][2]:
            return GameResult.from_role(board[0][0])
        if board[0][2] != CellState.EMPTY and board[0][2] == board[1][1] and board[0][2] == board[2][0]:
            return GameResult.from_role(board[0][2])
        for i in range(3):
            for j in range(3):
                if board[i][j] == CellState.EMPTY:
                    return GameResult.UNFINISHED
        return GameResult.DRAW


class QTable(object):
    """ Q-value table: maps board states to (val, update_count)

    mainly for RL, but we can pretty much store arbitrary values in it
    """

    def __init__(self):
        self.v = {}
        self.total_num_updates = 0

    def representation(self, board):
        # type: (Board) -> Tuple[Tuple, Tuple, Tuple]
        board = board.board
        return tuple(board[0]), tuple(board[1]), tuple(board[2])

    def lookup(self, board):
        rep = self.representation(board)
        return self.lookup_by_rep(rep)

    def lookup_by_rep(self, rep):
        if rep not in self.v:
            return None, None

        val, update_count = self.v[rep]
        return val, update_count

    def contains(self, board):
        rep = self.representation(board)
        return rep in self.v

    def set(self, board_repr, val):
        self.v[board_repr] = val, 0

    def update(self, board_repr, val):
        _, update_count = self.v[board_repr]
        self.v[board_repr] = val, update_count + 1
        self.total_num_updates += 1

    def save(self, filename):
        logger.info('saving qtable to %s', filename)
        with open(filename, 'w') as f:
            pickle.dump(self.v, f)

    def load(self, filename):
        logger.info('loading qtable from %s', filename)
        with open(filename, 'r') as f:
            self.v = pickle.load(f)

    def stats(self):
        return len(self.v), self.total_num_updates

    def _num_stones_in_rep(self, board_rep):
        return 9 - Board(init_state=board_rep).num_empty_squares()

    def stats_by_num_stones(self):
        counter = Counter()
        for board_rep, val in self.v.iteritems():
            num_stones = self._num_stones_in_rep(board_rep)
            counter[num_stones] += 1
        return counter