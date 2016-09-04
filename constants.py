
# board representation: list of rows, each row a list of 3 ints.

# Stone value:
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


def emptystate():
    return [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]


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


def print_board_with_last_move(board, row, col):
    NAMES = [' ', 'X', 'O']

    cells = []
    for irow in range(3):
        for icol in range(3):
            char = NAMES[board[irow][icol]]
            if irow == row and icol == col:
                char = '(%s)' % char
            cells.append(char.center(5))

    print BOARD_FORMAT_WITH_INDEX.format(*cells)


def empty_score_board():
    return [['', '', ''], ['', '', ''], ['', '', '']]


def print_score_board_with_highlight(board, row, col):
    cells = []
    for irow in range(3):
        for icol in range(3):
            s = board[irow][icol]
            if irow == row and icol == col:
                s = '(%s)' % s
            cells.append(s.center(10))

    print BOARD_FORMAT.format(*cells)


def print_board(board):
    print_board_with_last_move(board, -1, -1)


def num_empty_squares(board):
    num = sum([val == EMPTY for row in board for val in row])
    return num


def next_empty_square(board):
    """  generator over all empty spots on board
    :return: row, col
    """
    for irow, row in enumerate(board):
        for icol, stone in enumerate(row):
            if stone == EMPTY:
                yield irow, icol


def kth_empty_square(board, k):
    for i, (row, col) in enumerate(next_empty_square(board)):
        if i == k:
            return row, col
    raise Exception('Invalid k=%d' % k)


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
