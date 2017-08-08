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

    def test_explore(self):
        self.check_explore_fairness(self.board)

        self.board.board[0][0] = CellState.PLAYER_X
        self.board.board[1][1] = CellState.PLAYER_O
        self.check_explore_fairness(self.board)

    def check_explore_fairness(self, board):
        # make sure explore() is fair
        counter = Counter()
        N = 10000
        for i in xrange(N):
            row, col = self.strat.explore(board)
            counter[(row, col)] += 1

        print counter.most_common()
        arr = np.array(counter.values(), np.float) / N
        print 'size', len(arr), 'spread', arr.max() - arr.min(), 'std', np.std(arr)
