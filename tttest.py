from unittest import TestCase

import utils


class BasicTest(TestCase):
    def setUp(self):
        self.empty_board = utils.emptystate()

    def testPrintBoard(self):
        utils.print_board(self.empty_board)

    def testGameOver(self):
        board = self.empty_board
        verdict = utils.gameover(board)
        print 'empty board: ', verdict
        self.assertEqual(verdict, utils.EMPTY)

        for i in range(3):
            board[1][i] = utils.PLAYER_O
        verdict = utils.gameover(board)
        print 'second row all O:', verdict
        self.assertEqual(verdict, utils.PLAYER_O)

    def testDiagonal(self):
        board = self.empty_board
        board[0][2] = utils.PLAYER_X
        board[1][1] = utils.PLAYER_X
        self.assertEqual(utils.gameover(board), utils.EMPTY)

        board[2][0] = utils.PLAYER_X
        verdict = utils.gameover(board)
        self.assertEqual(verdict, utils.PLAYER_X)
