from collections import namedtuple

CellState = namedtuple('BoardState', 'EMPTY PLAYER_X PLAYER_O')._make(range(3))
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def reverse_role(role):
    if role == PLAYER_O:
        return PLAYER_X
    elif role == PLAYER_X:
        return PLAYER_O
    else:
        raise Exception('invalid role')


class GameResult(object):
    """ constants of game result
    """
    UNFINISHED = 0
    X_WINS = PLAYER_X
    O_WINS = PLAYER_O
    DRAW = 3

    @classmethod
    def announce(cls, result):
        if result == cls.X_WINS:
            return 'X wins! Game over.'
        elif result == cls.O_WINS:
            return 'O wins! Game over.'
        elif result == cls.DRAW:
            return 'Tie game, shake hands'
        else:
            return 'Not finished, keep playing'


class Board(object):
    """
    A bunch helper functions around the actual board representation, which is a
      list of rows, each row a list of 3 ints.
    """

    def __init__(self):
        self.board = [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]

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
        num = sum([val == EMPTY for row in self.board for val in row])
        return num

    def next_empty_square(self):
        """ generator over all empty spots on board
        :return: row, col
        """
        for irow, row in enumerate(self.board):
            for icol, stone in enumerate(row):
                if stone == EMPTY:
                    yield irow, icol

    def kth_empty_square(self, k):
        for i, (row, col) in enumerate(self.next_empty_square()):
            if i == k:
                return row, col
        raise Exception('Invalid k=%d' % k)

    def gameover(self):
        """evaluate board -> winning player, DRAW, or EMPTY
        :return:
        """
        board = self.board
        for i in range(3):
            if board[i][0] != EMPTY and board[i][0] == board[i][1] and board[i][0] == board[i][2]:
                return board[i][0]
            if board[0][i] != EMPTY and board[0][i] == board[1][i] and board[0][i] == board[2][i]:
                return board[0][i]
        if board[0][0] != EMPTY and board[0][0] == board[1][1] and board[0][0] == board[2][2]:
            return board[0][0]
        if board[0][2] != EMPTY and board[0][2] == board[1][1] and board[0][2] == board[2][0]:
            return board[0][2]
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    return GameResult.UNFINISHED
        return GameResult.DRAW
