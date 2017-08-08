from typing import List, Dict, Tuple, Any
import random
import pickle
import logging
from strategies import Strategy
from utils import CellState, GameResult, Board


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class QTable0(object):
    """ encode every board configuration as an int (3**9, this over-estimates as it
    allows illegal cases)
    """
    def __init__(self, value_func):
        self.v = [-1 for i in range(3**9)]
        self.value_func = value_func

    def representation(self, board):
        """
        :return: a unique int for a board configuration
        """
        hash = 0
        for row in board:
            for val in row:
                hash = hash * 3 + val
        return hash

    def lookup(self, board):
        idx = self.representation(board)
        if self.v[idx] < 0:
            self.v[idx] = self.value_func(board)
        return self.v[idx]

    def lookup_by_rep(self, rep):
        return self.v[rep]

    def update(self, board_repr, val):
        self.v[board_repr] = val


class QTable(object):
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

    def set(self, board_repr, val):
        self.v[board_repr] = val, 0

    def update(self, board_repr, val):
        _, update_count = self.v[board_repr]
        self.v[board_repr] = val, update_count + 1
        self.total_num_updates += 1

    def stats(self):
        return len(self.v), self.total_num_updates

    def save(self, filename):
        logger.info('saving qtable to %s', filename)
        with open(filename, 'w') as f:
            pickle.dump(self.v, f)

    def load(self, filename):
        logger.info('loading qtable from %s', filename)
        with open(filename, 'r') as f:
            self.v = pickle.load(f)


class RLStrat(Strategy):
    """ Reinforcement Learning
    """
    def __init__(self, learn_rate, explore_rate=0.1, debug=False):
        self.learn_rate = learn_rate
        self.explore_rate = explore_rate
        self.debug = debug

        self.q_table = QTable()
        self.prev_move = None
        self.prev_board_rep = None

    def name(self):
        return 'RL'

    def set_debug(self, debug):
        self.debug = debug

    def set_explore_rate(self, rate):
        self.explore_rate = rate

    def set_learn_rate(self, rate):
        self.learn_rate = rate

    def start_game(self, role):
        self.role = role

        # this (EnumMap) is to speed up value_of() computation
        self.reward_mapping = {
            GameResult.from_role(self.role): 1.0,
            GameResult.from_role(self.role.reverse_role()): 0,
            GameResult.DRAW: 0,
            GameResult.UNFINISHED: 0.5
        }

    def end_game(self, game_result):
        # this could be an important update (if RL plays O)
        if self.prev_board_rep:
            self.update(self.prev_board_rep, game_result)

        self.prev_board_rep = None

    def next_move(self, board):
        # type: (Board, CellState) -> Tuple[int, int]
        row, col = self._choose_next_move(board)

        # record the transition
        # Note we cannot change board state at this moment, wait for game controller to check our move and do it
        board.board[row][col] = self.role
        self.prev_board_rep = self.q_table.representation(board)
        board.board[row][col] = CellState.EMPTY
        self.prev_move = row, col
        return row, col

    def _choose_next_move(self, board):
        if random.random() < self.explore_rate:
            # print '>>>>>> explore'
            # TODO we could do an update with some computation
            return self.explore(board)

        q_best, (row, col) = self.exploit(board)
        if self.prev_board_rep:
            self.update(self.prev_board_rep, q_best)
        return row, col

    def exploit(self, board):
        q_best = -2
        best_move = None
        score_board = board.empty_score_board()
        for row, col in board.next_empty_square():
            board.board[row][col] = self.role
            q, update_count = self._lookup_qtable_or_init(board)
            score_board[row][col] = '%.1f %g' % (10 * q, update_count)
            if q > q_best:
                q_best = q
                best_move = row, col
            board.board[row][col] = CellState.EMPTY
        if self.debug:
            Board.print_score_board_with_highlight(score_board, best_move[0], best_move[1])
        return q_best, best_move

    def explore(self, board):
        num_choices = board.num_empty_squares()
        k = int(random.random() * num_choices)
        for i, (row, col) in enumerate(board.next_empty_square()):
            if i == k:
                return row, col
        raise Exception('Should not reach here')

    def initial_value_of(self, board):
        """ value function
        """
        verdict = board.evaluate()
        return self.reward_mapping[verdict]

    def _lookup_qtable_or_init(self, board):
        board_rep = self.q_table.representation(board)
        val, update_count = self.q_table.lookup_by_rep(board_rep)
        if val is None:
            val = self.initial_value_of(board)
            self.q_table.set(board_rep, val)
            return val, 0

        return val, update_count

    def update(self, prev_board_rep, v_s_prime):
        """ TD update
        """
        v_s, _ = self.q_table.lookup_by_rep(prev_board_rep)
        delta = self.learn_rate * (v_s_prime - v_s)
        self.q_table.update(prev_board_rep, v_s + delta)