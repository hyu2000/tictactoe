from unittest import TestCase
from utils import Board, CellState, GameResult
from strategies import difloc, RobertStrat1, MinMaxStrat, MinMaxWithQTable


class SimpleTest(TestCase):

    def setUp(self):
        self.board = Board()
        self.board.board[0][0] = CellState.PLAYER_X
        self.board.board[0][1] = CellState.PLAYER_X
        # [1, 1, EMPTY],
        # [EMPTY, EMPTY, EMPTY],
        # [EMPTY, EMPTY, EMPTY]]

    def test_difloc(self):
        self.assertEqual(difloc(0, 2), 1)
        self.assertEqual(difloc(1, 2), 0)

    def test_Robert_Strat1(self):
        strat = RobertStrat1()
        strat.start_game(1)
        row, col = strat.next_move(self.board)
        self.assertEqual((row, col), (0, 2))

    def testIterateOverEmptySpots(self):
        print [(row, col) for (row, col) in self.board.next_empty_square()]


class MinMaxTest(TestCase):
    def setUp(self):
        self.strat = MinMaxStrat()
        # self.strat = MinMaxWithQTable()

    def test_end_game(self):
        board = Board([
            [1, 2, 2],
            [2, 2, 1],
            [1, 0, 0]])
        # defensive move
        result, move = self.strat.eval_board(board, 1)
        self.assertEqual(result, GameResult.DRAW)
        self.assertEqual(move, (2, 1))

        # offensive move
        result, move = self.strat.eval_board(board, 2)
        self.assertEqual(result, GameResult.O_WINS)
        self.assertEqual(move, (2, 1))

    def test_mid_game(self):
        board = Board([
            [1, 2, 2],
            [2, 0, 1],
            [1, 0, 0]])
        # X's move
        result, move = self.strat.eval_board(board, 1)
        self.assertEqual(result, GameResult.X_WINS)
        self.assertEqual(move, (2, 2))

        # O's move
        result, move = self.strat.eval_board(board, 2)
        self.assertEqual(result, GameResult.DRAW)

    def test_open_game(self):
        board = Board([
            [1, 2, 0],
            [0, 0, 0],
            [0, 0, 0]])
        # X's move
        result, move = self.strat.eval_board(board, 1)
        self.assertEqual(result, GameResult.X_WINS)
        # self.assertEqual(move, (1, 0))


class MinMaxQTTest(TestCase):
    def setUp(self):
        self.strat = MinMaxWithQTable()

    def test_qtable(self):
        board = Board()
        best_result, best_move = self.strat.eval_board(board, CellState.PLAYER_X)
        print best_result, best_move
        # 3964 states: once we find a win, no need to explore other branches
        print self.strat.q_table.stats()
        print self.strat.q_table.stats_by_num_stones().items()

        self.strat.q_table.save('/tmp/minmax.qtable')
