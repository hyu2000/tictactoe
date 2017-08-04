from collections import namedtuple
import enum


# all ints
CellState = namedtuple('BoardState', ['EMPTY', 'PLAYER_X', 'PLAYER_O'])._make(range(3))


def reverse_role(role):
    if role == CellState.PLAYER_O:
        return CellState.PLAYER_X
    elif role == CellState.PLAYER_X:
        return CellState.PLAYER_O
    else:
        raise Exception('Invalid role: ' + role)


# also ints, so that it's easy to compare with CellState
GameResult = namedtuple('GameResult', 'UNFINISHED X_WINS O_WINS DRAW')._make(range(4))


def announce_result(result):
    if result == GameResult.X_WINS:
        return 'X wins! Game over.'
    elif result == GameResult.O_WINS:
        return 'O wins! Game over.'
    elif result == GameResult.DRAW:
        return 'Tie game, shake hands'
    else:
        return 'Not finished, keep playing'


# class GameResult(enum.Enum):
#     """ constants of game result
#     """
#     UNFINISHED = 0
#     X_WINS = CellState.PLAYER_X
#     O_WINS = CellState.PLAYER_O
#     DRAW = 3
#
#     @staticmethod
#     def from_role(role):
#         if role == CellState.PLAYER_O:
#             return GameResult.O_WINS
#         elif role == CellState.PLAYER_X:
#             return GameResult.X_WINS
#         else:
#             raise Exception('Invalid role: ' + role)
#
#     def announce(self):
#         if self == self.X_WINS:
#             return 'X wins! Game over.'
#         elif self == self.O_WINS:
#             return 'O wins! Game over.'
#         elif self == self.DRAW:
#             return 'Tie game, shake hands'
#         else:
#             return 'Not finished, keep playing'


class Board(object):
    """
    Wrap a bunch helper functions around the actual board representation, which is a
      list of rows, each row a list of 3 ints.
    """

    BOARD_FORMAT_WITH_INDEX = '\n'.join([
        '----------------------------',
        '| {0} 0| {1} 1| {2} 2|',
        '|--------------------------|',
        '| {3} 3| {4} 4| {5} 5|',
        '|--------------------------|',
        '| {6} 6| {7} 7| {8} 8|',
        '----------------------------'])

    BOARD_FORMAT = '\n'.join([
        '----------------------------',
        '| {0} | {1} | {2} |',
        '|--------------------------|',
        '| {3} | {4} | {5} |',
        '|--------------------------|',
        '| {6} | {7} | {8} |',
        '----------------------------'])

    def __init__(self, init_state=None):
        EMPTY = CellState.EMPTY
        if not init_state:
            self.board = [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]
        else:
            self.board = init_state

    def print_board_with_last_move(self, row, col):
        NAMES = [' ', 'X', 'O']

        cells = []
        for irow in range(3):
            for icol in range(3):
                char = NAMES[self.board[irow][icol]]
                if irow == row and icol == col:
                    char = '(%s)' % char
                cells.append(char.center(5))

        print self.BOARD_FORMAT_WITH_INDEX.format(*cells)

    @staticmethod
    def empty_score_board():
        return [['', '', ''], ['', '', ''], ['', '', '']]

    @staticmethod
    def print_score_board_with_highlight(board, row, col):
        cells = []
        for irow in range(3):
            for icol in range(3):
                s = board[irow][icol]
                if irow == row and icol == col:
                    s = '(%s)' % s
                cells.append(s.center(10))

        print Board.BOARD_FORMAT.format(*cells)

    def print_board(self):
        self.print_board_with_last_move(-1, -1)

    def num_empty_squares(self):
        num = sum([val == CellState.EMPTY for row in self.board for val in row])
        return num

    def next_empty_square(self):
        """ generator over all empty spots on board
        :return: row, col
        """
        for irow, row in enumerate(self.board):
            for icol, stone in enumerate(row):
                if stone == CellState.EMPTY:
                    yield irow, icol

    def kth_empty_square(self, k):
        for i, (row, col) in enumerate(self.next_empty_square()):
            if i == k:
                return row, col
        raise Exception('Invalid k=%d' % k)

    def evaluate(self):
        """evaluate board -> winning player, DRAW, or EMPTY
        :return:
        """
        board = self.board
        for i in range(3):
            if board[i][0] != CellState.EMPTY and board[i][0] == board[i][1] and board[i][0] == board[i][2]:
                return board[i][0]
            if board[0][i] != CellState.EMPTY and board[0][i] == board[1][i] and board[0][i] == board[2][i]:
                return board[0][i]
        if board[0][0] != CellState.EMPTY and board[0][0] == board[1][1] and board[0][0] == board[2][2]:
            return board[0][0]
        if board[0][2] != CellState.EMPTY and board[0][2] == board[1][1] and board[0][2] == board[2][0]:
            return board[0][2]
        for i in range(3):
            for j in range(3):
                if board[i][j] == CellState.EMPTY:
                    return GameResult.UNFINISHED
        return GameResult.DRAW
