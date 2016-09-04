from collections import Counter
import random
import time
import os

import constants as TTT
from constants import GameResult, kth_empty_square


PARAM_FILE = '/tmp/rl.pickle'


class Strategy(object):
    def next_move(self, board, role):
        """
        :param board:
        :param role: role == ttt.PLAYER_X or O
        :return: row, col
        """
        raise Exception('Not implemented')


class Human(Strategy):
    def next_move(self, board, role):
        while True:
            action = raw_input('Your move (row,col) or index (row-major)? ')
            elements = action.split(',')
            if len(elements) == 2:
                row, col = int(elements[0]), int(elements[1])
            elif len(elements) == 1:
                index = int(elements[0])
                row, col = index / 3, index % 3
            else:
                print 'invalid input, try again...'
                continue
            return row, col


def gameover(board):
    """evaluate board -> winning player, DRAW, or EMPTY
    :return:
    """
    for i in range(3):
        if board[i][0] != TTT.EMPTY and board[i][0] == board[i][1] and board[i][0] == board[i][2]:
            return board[i][0]
        if board[0][i] != TTT.EMPTY and board[0][i] == board[1][i] and board[0][i] == board[2][i]:
            return board[0][i]
    if board[0][0] != TTT.EMPTY and board[0][0] == board[1][1] and board[0][0] == board[2][2]:
        return board[0][0]
    if board[0][2] != TTT.EMPTY and board[0][2] == board[1][1] and board[0][2] == board[2][0]:
        return board[0][2]
    for i in range(3):
        for j in range(3):
            if board[i][j] == TTT.EMPTY:
                return GameResult.UNFINISHED
    return GameResult.DRAW


class GamePlay(object):
    def __init__(self, strategy_x, strategy_o):
        self.players = [strategy_x, strategy_o]

    def run(self, verbose=True):
        board = TTT.emptystate()
        if verbose:
            TTT.print_board(board)
        for i in range(8):
            iplayer = i % 2
            stone = iplayer + 1
            assert stone == TTT.PLAYER_O or stone == TTT.PLAYER_X

            row, col = self.players[iplayer].next_move(board, stone)

            if board[row][col] != TTT.EMPTY:
                print 'player %d made an invalid move: (%d, %d)' % (stone, row, col)
                raise Exception('Debug now!')
            board[row][col] = stone

            if verbose:
                print '%dth move, player %d picked row %d, col %d' % (i, stone, row, col)
                TTT.print_board_with_last_move(board, row, col)

            verdict = gameover(board)
            if verdict == GameResult.UNFINISHED:
                continue

            if verbose:
                print GameResult.announce(verdict)
            return verdict

        # last move is trivial if it gets here
        row, col = kth_empty_square(board, 0)
        board[row][col] = TTT.PLAYER_X
        verdict = gameover(board)
        if verbose:
            TTT.print_board_with_last_move(board, row, col)
            print GameResult.announce(verdict)
        return verdict

    def run_tournament(self, N=100):
        counter = Counter()
        for i in range(N):
            result = self.run(verbose=False)
            counter[result] += 1
        percentage = [float(counter[result]) / N for result in (GameResult.X_WINS, GameResult.O_WINS, GameResult.DRAW)]
        print '%d runs: %s' % (N, percentage)


def train_RL(strat1, game):
    explore_rate = 0.01
    for i in range(10):
        strat1.set_explore_rate(explore_rate)
        game.run_tournament(N=5000)
        print 'q_table size = ', strat1.q_table.stats()
        # explore_rate /= 2
    strat1.q_table.save(PARAM_FILE)


def test_RL(strat_rl, game):
    print 'Evaluation:'
    strat_rl.set_explore_rate(0)
    strat_rl.set_learn_rate(0)

    strat_rl.set_debug(True)
    game.run()

    strat_rl.set_debug(False)
    game.run_tournament(1000)



def run_RL_as_X():
    from strategies import RobertStrat1, MinMaxStrat, DefensiveStrat1
    from rl import RLStrat
    strat1 = RLStrat(TTT.PLAYER_X, 0.1)
    strat2 = RLStrat(TTT.PLAYER_O, 0.1)
    game = GamePlay(strat1, strat2)
    if os.path.exists(PARAM_FILE):
        strat1.q_table.load(PARAM_FILE)
        strat2.q_table.load(PARAM_FILE)

    # train_RL(strat1, game)
    test_RL (strat1, game)


def run_manual():
    from strategies import RandomPlay, RobertStrat1, MinMaxStrat, DefensiveStrat1
    strat1 = DefensiveStrat1()
    strat2 = DefensiveStrat1()
    game = GamePlay(strat1, strat2)
    game.run()
    game.run_tournament(5000)

if __name__ == '__main__':
    random.seed(time.time())
    run_RL_as_X()
    # run_manual()