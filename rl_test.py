from unittest import TestCase
from collections import Counter
import rl
from utils import Board, CellState
import numpy as np


class BasicTest(TestCase):
    def setUp(self):
        self.board = Board()
        self.strat = rl.RLStrat(0.01)
        self.strat.start_game(CellState.PLAYER_X)

    def test_state_counts(self):
        self.assertEqual(rl.StateCount.num_states_for_step(1), 9)
        print [rl.StateCount.num_states_for_step(i) for i in xrange(1, 10)]
        # [9, 72, 252, 756, 1260, 1680, 1260, 630, 126]
        total_num_states_for_x = rl.StateCount.total_num_states_for_X()
        total_num_states_for_o = rl.StateCount.total_num_states_for_O()
        print 'total #states for X', total_num_states_for_x
        print 'total #states for O', total_num_states_for_o
        print '3**9 =', 3**9
        self.assertEqual(total_num_states_for_x, 2907)
        self.assertEqual(total_num_states_for_o, 3138)

    def test_explore(self):
        # make sure explore() is fair
        self.check_explore_fairness(self.board)

        self.board.board[0][0] = CellState.PLAYER_X
        self.board.board[1][1] = CellState.PLAYER_O
        self.check_explore_fairness(self.board)

    def check_explore_fairness(self, board):
        counter = Counter()
        N = 10000
        for i in xrange(N):
            row, col = self.strat.explore(board)
            counter[(row, col)] += 1

        print counter.most_common()
        arr = np.array(counter.values(), np.float) / N
        print 'size', len(arr), 'spread', arr.max() - arr.min(), 'std', np.std(arr)
