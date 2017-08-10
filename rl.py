from typing import List, Dict, Tuple, Any
import random
import logging
from strategies import Strategy
from utils import CellState, GameResult, Board, QTable


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
        self.role = None

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
        self.prev_board_rep = None

        # this (EnumMap) is to speed up value_of() computation
        self.reward_mapping = {
            GameResult.from_role(self.role): 1.0,
            GameResult.from_role(self.role.reverse_role()): -1.0,
            GameResult.DRAW: 0,
            GameResult.UNFINISHED: 0
        }

    def end_game(self, game_result):
        # this could be an important update (if RL plays O)
        # if RL plays X, we already performed the final update if we chose 'exploit' in the last step
        # if self.role == CellState.PLAYER_O:
        v_prime = self.reward_mapping[game_result]
        self.update(self.prev_board_rep, v_prime)

    def next_move(self, board):
        # type: (Board) -> Tuple[int, int]
        row, col = self._choose_next_move(board)

        # record the transition
        # Note we cannot change board state at this moment, wait for game controller to check our move and do it
        board.board[row][col] = self.role
        self.prev_board_rep, _, _ = self._lookup_qtable_or_init(board)
        board.board[row][col] = CellState.EMPTY
        self.prev_move = row, col
        return row, col

    def _choose_next_move(self, board):
        self.prev_action = 'exploit'
        if random.random() < self.explore_rate:
            # print '>>>>>> explore'
            # TODO we could do an update with some computation
            self.prev_action = 'explore'
            return self.explore(board)

        q_best, (row, col) = self.exploit(board)
        if self.prev_board_rep:  # so long as prev_board_rep exists
            self.update(self.prev_board_rep, q_best)
        return row, col

    def exploit(self, board):
        q_best = -1e10
        best_moves = []
        score_board = board.empty_score_board()
        for row, col in board.next_empty_square():
            board.board[row][col] = self.role
            _, q_val, update_count = self._lookup_qtable_or_init(board)
            score_board[row][col] = '%.1f %g' % (10 * q_val, update_count)
            if q_val > q_best:
                q_best = q_val
                best_moves = [(row, col)]
            elif q_val == q_best:  #
                best_moves.append((row, col))
            board.board[row][col] = CellState.EMPTY

        # randomize among best moves
        move = random.choice(best_moves)
        if self.debug:
            Board.print_score_board_with_highlight(score_board, move[0], move[1])
        return q_best, move

    def explore(self, board):
        num_choices = board.num_empty_squares()
        k = int(random.random() * num_choices)
        return board.kth_empty_square(k)

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
            update_count = 0
            self.q_table.set(board_rep, val)

        return board_rep, val, update_count

    def update(self, prev_board_rep, v_s_prime):
        """ TD update
        """
        v_s, _ = self.q_table.lookup_by_rep(prev_board_rep)
        delta = self.learn_rate * (v_s_prime - v_s)
        self.q_table.update(prev_board_rep, v_s + delta)
