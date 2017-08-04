from unittest import TestCase

import constants as TTT


class BasicTest(TestCase):
    def setUp(self):
        self.empty_board = TTT.emptystate()

    def testPrintBoard(self):
        TTT.print_board(self.empty_board)

    def testGameOver(self):
        board = self.empty_board
        verdict = TTT.gameover(board)
        print 'empty board: ', verdict
        self.assertEqual(verdict, TTT.EMPTY)

        for i in range(3):
            board[1][i] = TTT.PLAYER_O
        verdict = TTT.gameover(board)
        print 'second row all O:', verdict
        self.assertEqual(verdict, TTT.PLAYER_O)

    def testDiagonal(self):
        board = self.empty_board
        board[0][2] = TTT.PLAYER_X
        board[1][1] = TTT.PLAYER_X
        self.assertEqual(TTT.gameover(board), TTT.EMPTY)

        board[2][0] = TTT.PLAYER_X
        verdict = TTT.gameover(board)
        self.assertEqual(verdict, TTT.PLAYER_X)
