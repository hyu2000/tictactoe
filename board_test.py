from unittest import TestCase

from utils import Board, GameResult, CellState


class BasicTest(TestCase):
    def setUp(self):
        self.board = Board()

    def testPrintBoard(self):
        self.board.print_board()

    def testEvaluateGame(self):
        verdict = self.board.evaluate()
        print 'empty board: ', verdict
        self.assertEqual(verdict, GameResult.UNFINISHED)

        for i in range(3):
            self.board.board[1][i] = CellState.PLAYER_O
        verdict = self.board.evaluate()
        print 'second row all O:', verdict
        self.assertEqual(verdict, GameResult.O_WINS)

    def testDiagonal(self):
        self.board.board[0][2] = CellState.PLAYER_X
        self.board.board[1][1] = CellState.PLAYER_X
        self.assertEqual(self.board.evaluate(), GameResult.UNFINISHED)

        self.board.board[2][0] = CellState.PLAYER_X
        verdict = self.board.evaluate()
        self.assertEqual(verdict, GameResult.X_WINS)
