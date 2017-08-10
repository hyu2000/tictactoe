from typing import List, Dict, Tuple, Any
from utils import CellState, GameResult, Board, QTable
import random
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Strategy(object):
    def name(self):
        return 'abstract strategy'

    def next_move(self, board):
        # type: (Board, CellState) -> Tuple[int, int]
        """
        :param board:
        :param role: role == ttt.PLAYER_X or O
        :return: row, col
        """
        raise NotImplementedError

    def start_game(self, role):
        # type: (CellState) -> None
        """ override to reset states """
        self.role = role

    def end_game(self, game_result):
        # type: (GameResult) -> None
        """ override to learn outcome """
        pass


class Human(Strategy):
    def __init__(self):
        pass

    def name(self):
        return 'human'

    def next_move(self, board):
        while True:
            action = raw_input('Your move (row,col) or index (row-major)? ')
            elements = action.split(',')
            if len(elements) == 2:
                row, col = int(elements[0]), int(elements[1])
            elif len(elements) == 1:
                index = int(elements[0])
                row, col = index / 3, index % 3
            else:
                print 'invalid input, try again...'
                continue
            return row, col


class RandomPlay(Strategy):
    """ baseline random strategy
    """
    def __init__(self):
        pass

    def name(self):
        return 'random'

    def next_move(self, board):
        num_empty_spots = board.num_empty_squares()
        k = random.randint(0, num_empty_spots - 1)
        return board.kth_empty_square(k)


class MinMaxStrat(Strategy):
    """ the deep search strategy, assuming opponent plays optimally
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def name(self):
        return 'MinMax'

    def next_move(self, board):
        best_score, best_move = self.eval_board(board, self.role)
        if self.verbose:
            print 'MinMax predicts score= %d' % best_score
        return best_move

    def _calc_score(self, role, result, steps):
        """ role-specific score: the higher the better

        score: 0 == DRAW, negative: losing, positive: winning
        """
        assert result != GameResult.UNFINISHED
        if result is None:
            return -100
        if result == GameResult.DRAW:
            return 0
        if result == role:  # win
            return 10 - steps
        else:  # lose
            return steps - 10

    def eval_board(self, board, role):
        """ return: role-specific score, best_move
        """
        next_role = CellState(role).reverse_role()
        current_best_score, best_move = -100, None
        for (row, col) in board.next_empty_square():
            try:
                board.board[row][col] = role
                result, num_stones = board.evaluate(), board.num_stones()
                if result == GameResult.UNFINISHED:
                    # recurse
                    score, _ = self.eval_board(board, next_role)
                    score = -score
                else:
                    score = self._calc_score(role, result, num_stones)

                if score > current_best_score:
                    current_best_score = score
                    best_move = (row, col)
            finally:
                board.board[row][col] = CellState.EMPTY

        return current_best_score, best_move


class MinMaxWithQTable(Strategy):
    """
    this speeds up MinMax thru QTable caching;
    also allows us to produce MinMax variants easily
    """
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.q_table = QTable()

    def name(self):
        return 'MinMaxQT'

    def next_move(self, board):
        best_result, best_move = self.eval_board(board, self.role)
        return best_move

    def eval_board(self, board, role):
        val, _ = self.q_table.lookup(board)
        if val is not None:
            return val

        # calculate
        next_role = CellState(role).reverse_role()
        best_possible_result = None
        best_move = None
        for (row, col) in board.next_empty_square():
            try:
                board.board[row][col] = role
                result = board.evaluate()
                if result == GameResult.UNFINISHED:
                    result, _ = self.eval_board(board, next_role)
                if result == role:
                    best_possible_result, best_move = result, (row, col)
                    break
                elif result == GameResult.DRAW:
                    # this will pick the last draw move, if several leads to draw
                    best_possible_result = result
                    best_move = (row, col)
                elif best_move is None:
                    # so that we can return a valid move if cannot draw
                    best_possible_result = result
                    best_move = (row, col)
            finally:
                board.board[row][col] = CellState.EMPTY

        # cache
        board_rep = self.q_table.representation(board)
        self.q_table.set(board_rep, (best_possible_result, best_move))
        return best_possible_result, best_move


class WeakenedMinMax(Strategy):
    """
    1. MinMax is expensive. For tictactoe, just memorize its move
    2. for a particular board situation, weaken it (to see if opponent can exploit it)
    """
    def __init__(self):
        self.q_table = QTable()
        self.q_table.load('/tmp/minmax.qtable')
        self.hack_q_table()

        self.baseline = MinMaxStrat()

    def hack_q_table(self):
        logger.info('hacking qtable')
        board = Board()
        board.board[0][2] = CellState.PLAYER_X
        # minmax has to choose (1, 1)
        board_rep = self.q_table.representation(board)
        self.q_table.set(board_rep, (GameResult.DRAW, (0, 1)))

    def name(self):
        return 'MinMaxWeakened'

    def start_game(self, role):
        self.role = role
        self.baseline.start_game(role)

    def next_move(self, board):
        val, _ = self.q_table.lookup(board)
        if val is None:
            logger.info('backoff to minmax')
            return self.baseline.next_move(board)
        best_possible_result, best_move = val
        return best_move


class AntiMinMaxStrat(Strategy):
    """ memorized plays against MinMaxStrat (above), otherwise quite dumb

    This always ties against MinMax, but easily loses to RL
    """

    def __init__(self):
        self.baseline = DefensiveStrat1(level=10)

    def name(self):
        return 'AntiMinMax'

    def start_game(self, role):
        self.role = role
        self.baseline.start_game(role)

    def next_move(self, board):
        if self.role == CellState.PLAYER_X:
            # only acts as O for now
            raise NotImplementedError

        if board.num_empty_squares() == 8 and board.board[1][1] == CellState.EMPTY:
            return 1, 1

        return self.baseline.next_move(board)


# ------------------------------------------------------------------------------------------
# below are some hand-crafted strategy


def difloc(a, b):
    locs = [0,1,2]
    locs.remove(a)
    locs.remove(b)
    return locs[0]


def difloc2(a, b):
    return 3 - (a + b)


def count_stones_in_line(row, role):
    """
    :param row: a list in the board
    :return: number of my stones, number of total stones, index of an empty spot (if any)
    """
    num_my_stones = 0
    num_total_stones = 0
    idx_empty_spot = -1
    for i, x in enumerate(row):
        if x == role:
            num_my_stones += 1
            num_total_stones += 1
        elif x != CellState.EMPTY:
            num_total_stones += 1
        else:
            idx_empty_spot = i
    return num_my_stones, num_total_stones, idx_empty_spot


def empty_spot_in_row(row):
    """
    :param row: a list in the board
    :return: position of the 1st empty spot in the list
    """
    for i, val in enumerate(row):
        if val == CellState.EMPTY:
            return i
    raise 'No empty spot in row! %s' % row


class RobertStrat1(Strategy):
    def __init__(self, debug=False):
        self.baseline = RandomPlay()
        self.debug = debug

    def name(self):
        return 'RobertStrat'

    def start_game(self, role):
        self.role = role
        self.baseline.start_game(role)

    def next_move(self, board):
        for irow in range(3):
            row = board.board[irow]
            num_my_stones, total_stones, idx_empty_spot = count_stones_in_line(row, self.role)
            if total_stones == 2 and num_my_stones == 2:
                if self.debug:
                    print '>>>>>>>>>>>> Smart move right here!'
                return irow, idx_empty_spot

            # for icol in range(3):
            #     col = board[0][icol]
            #     num_my_stones, total_stones = count_stones_in_line(col, role)

        return self.baseline.next_move(board)


class DefensiveStrat1(Strategy):
    """ based on RandomPlay, but prioritized for defensive moves
    """
    def __init__(self, level=1, debug=False):
        self.baseline = RandomPlay()
        self.level = level
        self.debug = debug

    def name(self):
        return 'DefensiveStrat'

    def start_game(self, role):
        self.role = role
        self.baseline.start_game(role)

    def next_move(self, oboard):
        board = oboard.board
        opponent = self.role.reverse_role()

        # defend each row
        for irow, row in enumerate(board):
            num_opp, total_stones, idx_empty_spot = count_stones_in_line(row, opponent)
            if total_stones == 2 and num_opp == 2:
                return irow, idx_empty_spot

        # defend each column
        for icol in range(3):
            num_opp, total_stones, idx_empty_spot = count_stones_in_line(
                (board[0][icol], board[1][icol], board[2][icol]),
                opponent)
            if total_stones == 2 and num_opp == 2:
                return idx_empty_spot, icol

        # defend diagonal
        if self.level >= 2:
            num_opp, total_stones, idx_empty_spot = count_stones_in_line(
                (board[0][0], board[1][1], board[2][2]),
                opponent)
            if total_stones == 2 and num_opp == 2:
                return idx_empty_spot, idx_empty_spot

            num_opp, total_stones, idx_empty_spot = count_stones_in_line(
                (board[0][2], board[1][1], board[2][0]),
                opponent)
            if total_stones == 2 and num_opp == 2:
                return idx_empty_spot, 2 - idx_empty_spot

        return self.baseline.next_move(oboard)
