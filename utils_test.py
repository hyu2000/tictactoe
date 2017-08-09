from unittest import TestCase

from utils import Board, GameResult, CellState, QTable


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

    def test_cmp_safety(self):
        self.assertEqual(GameResult.X_WINS, CellState.PLAYER_X)
        self.assertEqual(GameResult.O_WINS, CellState.PLAYER_O)
        self.assertNotEqual(GameResult.X_WINS, CellState.PLAYER_O)

    def test_board_rep(self):
        q_table = QTable()
        tpl1 = (1, 0, 2)
        tpl2 = (CellState.PLAYER_X, CellState.EMPTY, CellState.PLAYER_O)
        tpl3 = (1, 0, CellState.PLAYER_O)
        print hash(tpl1)
        self.assertEqual(hash(tpl1), hash(tpl2))
        self.assertEqual(hash(tpl1), hash(tpl3))