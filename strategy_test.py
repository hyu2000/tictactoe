from unittest import TestCase
import constants as TTT
from constants import GameResult
from strategies import difloc, RobertStrat1, MinMaxStrat


class SimpleTest(TestCase):

    def setUp(self):
        EMPTY = TTT.EMPTY
        self.board = [
            [1, 1, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

    def test_difloc(self):
        self.assertEqual(difloc(0, 2), 1)
        self.assertEqual(difloc(1, 2), 0)

    def test_Robert_Strat1(self):
        strat = RobertStrat1()
        row, col = strat.next_move(self.board, 1)
        self.assertEqual((row, col), (0, 2))

    def testIterateOverEmptySpots(self):
        from strategies import next_empty_square
        board = self.board
        print [(row, col) for (row, col) in next_empty_square(board)]

    def check_end_game(self, strat):
        board = [[1, 2, 2],
                 [2, 2, 1],
                 [1, 0, 0]]
        # defensive move
        result, move = strat.eval_board(board, 1)
        self.assertEqual(result, GameResult.DRAW)
        self.assertEqual(move, (2, 1))

        # offensive move
        result, move = strat.eval_board(board, 2)
        self.assertEqual(result, GameResult.O_WINS)
        self.assertEqual(move, (2, 1))

    def check_mid_game(self, strat):
        board = [[1, 2, 2],
                 [2, 0, 1],
                 [1, 0, 0]]
        # X's move
        result, move = strat.eval_board(board, 1)
        self.assertEqual(result, GameResult.X_WINS)
        self.assertEqual(move, (2, 2))

        # O's move
        result, move = strat.eval_board(board, 2)
        self.assertEqual(result, GameResult.DRAW)

    def testMinMax(self):
        strat = MinMaxStrat()
        self.check_end_game(strat)
        self.check_mid_game(strat)

    def check_open_game(self, strat):
        board = [[1, 2, 0],
                 [0, 0, 0],
                 [0, 0, 0]]
        # X's move
        result, move = strat.eval_board(board, 1)
        self.assertEqual(result, GameResult.X_WINS)
        # self.assertEqual(move, (1, 0))

    def testMoveAgainstMinMax(self):
        strat = MinMaxStrat()
        self.check_open_game(strat)