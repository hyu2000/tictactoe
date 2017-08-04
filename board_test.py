from unittest import TestCase

import utils
from utils import Board, GameResult


class BasicTest(TestCase):
    def setUp(self):
        self.board = Board()

    def testPrintBoard(self):
        self.board.print_board()

    def testGameOver(self):
        verdict = self.board.gameover()
        print 'empty board: ', verdict
        self.assertEqual(verdict, GameResult.UNFINISHED)

        for i in range(3):
            self.board.board[1][i] = utils.PLAYER_O
        verdict = self.board.gameover()
        print 'second row all O:', verdict
        self.assertEqual(verdict, GameResult.O_WINS)

    def testDiagonal(self):
        self.board.board[0][2] = utils.PLAYER_X
        self.board.board[1][1] = utils.PLAYER_X
        self.assertEqual(self.board.gameover(), GameResult.UNFINISHED)

        self.board.board[2][0] = utils.PLAYER_X
        verdict = self.board.gameover()
        self.assertEqual(verdict, GameResult.X_WINS)
