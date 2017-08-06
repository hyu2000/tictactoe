import random
import pickle
from strategies import Strategy
from utils import CellState, GameResult, Board


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

    def look_up(self, board):
        idx = self.representation(board)
        if self.v[idx] < 0:
            self.v[idx] = self.value_func(board)
        return self.v[idx]

    def look_up_by_rep(self, rep):
        return self.v[rep]

    def update(self, board_repr, val):
        self.v[board_repr] = val


class QTable(object):
    def __init__(self, value_func):
        self.v = {}
        self.value_func = value_func

        self.total_num_updates = 0

    def representation(self, board):
        board = board.board
        return tuple(board[0]), tuple(board[1]), tuple(board[2])

    def look_up(self, board):
        rep = self.representation(board)
        return self.look_up_by_rep(rep)

    def look_up_by_rep(self, rep):
        if rep in self.v:
            val, update_count = self.v[rep]
            return val, update_count
        val = self.value_func(rep)
        self.v[rep] = val, 0
        return val, 0

    def update(self, board_repr, val):
        _, count = self.v[board_repr]
        self.v[board_repr] = val, count + 1
        self.total_num_updates += 1

    def stats(self):
        return len(self.v), self.total_num_updates

    def save(self, filename):
        with open(filename, 'w') as f:
            pickle.dump(self.v, f)

    def load(self, filename):
        with open(filename, 'r') as f:
            self.v = pickle.load(f)


class RLStrat(Strategy):
    """ Reinforcement Learning
    """
    def __init__(self, role, learn_rate, explore_rate=0.1, debug=False):
        self.role = role
        self.learn_rate = learn_rate
        self.explore_rate = explore_rate
        self.debug = debug

        self.q_table = QTable(self.value_of)
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

    def value_of(self, board_rep):
        """ value function
        """
        board = Board(init_state=board_rep)
        verdict = board.evaluate()
        if verdict == self.role:
            return 1.0
        elif verdict == self.role.reverse_role():
            return 0
        elif verdict == GameResult.DRAW:
            return 0
        else:  # UNFINISHED
            return 0.5

    def next_move(self, board, role):
        assert role == self.role

        row, col = self._choose_next_move(board)

        # record the transition
        # Note we cannot change board state at this moment, wait for game controller to check our move and do it
        board.board[row][col] = role
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
            q, update_count = self.q_table.look_up(board)
            score_board[row][col] = '%.3f %3.1g' % (10 * q, update_count)
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

    def update(self, prev_board_rep, v_s_prime):
        """
        """
        v_s, _ = self.q_table.look_up_by_rep(prev_board_rep)
        delta = self.learn_rate * (v_s_prime - v_s)
        self.q_table.update(prev_board_rep, v_s + delta)