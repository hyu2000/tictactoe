import constants as TTT
from constants import GameResult, num_empty_squares, next_empty_square, kth_empty_square
import random
from game_play import Strategy, gameover


class RandomPlay(Strategy):
    """ baseline random strategy
    """
    def __init__(self):
        pass

    def name(self):
        return 'random'

    def next_move(self, board, role):
        num_empty_spots = num_empty_squares(board)
        pick = random.randint(0, num_empty_spots - 1)
        return kth_empty_square(board, pick)


def difloc(a, b):
    locs = [0,1,2]
    locs.remove(a)
    locs.remove(b)
    return locs[0]


def difloc2(a, b):
    return 3 - (a + b)


def count_stones_in_line(row, role):
    """
    :param row: a list in the board
    :return: number of my stones, number of total stones, index of an empty spot (if any)
    """
    num_my_stones = 0
    num_total_stones = 0
    idx_empty_spot = -1
    for i, x in enumerate(row):
        if x == role:
            num_my_stones += 1
            num_total_stones += 1
        elif x != TTT.EMPTY:
            num_total_stones += 1
        else:
            idx_empty_spot = i
    return num_my_stones, num_total_stones, idx_empty_spot


def empty_spot_in_row(row):
    """
    :param row: a list in the board
    :return: position of the 1st empty spot in the list
    """
    for i, val in enumerate(row):
        if val == TTT.EMPTY:
            return i
    raise 'No empty spot in row! %s' % row


class RobertStrat1(Strategy):
    def __init__(self, debug=False):
        self.baseline = RandomPlay()
        self.debug = debug

    def name(self):
        return 'RobertStrat'

    def next_move(self, board, role):
        for irow in range(3):
            row = board[irow]
            num_my_stones, total_stones, idx_empty_spot = count_stones_in_line(row, role)
            if total_stones == 2 and num_my_stones == 2:
                if self.debug:
                    print '>>>>>>>>>>>> Smart move right here!'
                return irow, idx_empty_spot

            # for icol in range(3):
            #     col = board[0][icol]
            #     num_my_stones, total_stones = count_stones_in_line(col, role)

        return self.baseline.next_move(board, role)


class MinMaxStrat(Strategy):
    """ the deep search strategy, assuming opponent plays optimally
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def name(self):
        return 'MinMax'

    def next_move(self, board, role):
        best_result, best_move = self.eval_board(board, role)
        if self.verbose:
            print 'MinMax predicts', GameResult.announce(best_result)
        return best_move

    def eval_board(self, board, role):
        next_role = TTT.reverse_role(role)
        best_possible_result = None
        best_move = None
        for (row, col) in next_empty_square(board):
            try:
                board[row][col] = role
                result = gameover(board)
                if result == GameResult.UNFINISHED:
                    result, _ = self.eval_board(board, next_role)
                if result == role:
                    return result, (row, col)
                elif result == GameResult.DRAW:
                    # this will pick the last draw move, if several leads to draw
                    best_possible_result = result
                    best_move = (row, col)
                elif best_move is None:
                    # so that we can return a valid move if cannot draw
                    best_possible_result = result
                    best_move = (row, col)
            finally:
                board[row][col] = TTT.EMPTY

        return best_possible_result, best_move


class DefensiveStrat1(Strategy):
    """ another hand-crafted strategy
    """
    def __init__(self, level=1, debug=False):
        self.baseline = RandomPlay()
        self.level = level
        self.debug = debug

    def name(self):
        return 'DefensiveStrat'

    def next_move(self, board, role):
        opponent = TTT.reverse_role(role)

        # defend each row
        for irow, row in enumerate(board):
            num_opp, total_stones, idx_empty_spot = count_stones_in_line(row, opponent)
            if total_stones == 2 and num_opp == 2:
                return irow, idx_empty_spot

        # defend each column
        row_empty, col_empty = 0, 0
        for icol in range(3):
            num_opp, total_stones, idx_empty_spot = count_stones_in_line(
                (board[0][icol], board[1][icol], board[2][icol]),
                opponent)
            if total_stones == 2 and num_opp == 2:
                return idx_empty_spot, icol

        # defend diagonal
        if self.level >= 2:
            num_opp, total_stones, idx_empty_spot = count_stones_in_line(
                (board[0][0], board[1][1], board[2][2]),
                opponent)
            if total_stones == 2 and num_opp == 2:
                return idx_empty_spot, idx_empty_spot

            num_opp, total_stones, idx_empty_spot = count_stones_in_line(
                (board[0][2], board[1][1], board[2][0]),
                opponent)
            if total_stones == 2 and num_opp == 2:
                return idx_empty_spot, 2 - idx_empty_spot

        return self.baseline.next_move(board, role)
