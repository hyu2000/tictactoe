from unittest import TestCase

from utils import Board, GameResult, CellState, QTable, StateCount


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

    def test_state_counts(self):
        self.assertEqual(StateCount.num_states_for_step(1), 9)
        print [StateCount.num_states_for_step(i) for i in xrange(1, 10)]
        # [9, 72, 252, 756, 1260, 1680, 1260, 630, 126]
        total_num_states_for_x = StateCount.total_num_states_for_X()
        total_num_states_for_o = StateCount.total_num_states_for_O()
        print 'total #states for X', total_num_states_for_x
        print 'total #states for O', total_num_states_for_o
        print '3**9 =', 3**9
        self.assertEqual(total_num_states_for_x, 2907)
        self.assertEqual(total_num_states_for_o, 3138)
