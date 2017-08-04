from collections import Counter
import random
import time
import os

import utils
from utils import CellState
from utils import GameResult, kth_empty_square


PARAM_FILE = '/tmp/rl.pickle'


class GamePlay(object):
    def __init__(self, strategy_x, strategy_o):
        self.players = [strategy_x, strategy_o]

    def opponents(self):
        return '%s vs %s' % (self.players[0].name(), self.players[1].name())

    def run(self, verbose=True):
        board = utils.emptystate()
        if verbose:
            utils.print_board(board)
        for i in range(8):
            iplayer = i % 2
            stone = iplayer + 1
            assert stone == CellState.PLAYER_O or stone == CellState.PLAYER_X

            row, col = self.players[iplayer].next_move(board, stone)

            if board[row][col] != CellState.EMPTY:
                print 'player %d made an invalid move: (%d, %d)' % (stone, row, col)
                raise Exception('Debug now!')
            board[row][col] = stone

            if verbose:
                print '%dth move, player %d picked row %d, col %d' % (i, stone, row, col)
                utils.print_board_with_last_move(board, row, col)

            verdict = utils.gameover(board)
            if verdict == GameResult.UNFINISHED:
                continue

            if verbose:
                print GameResult.announce(verdict)
            return verdict

        # last move is trivial if it gets here
        row, col = kth_empty_square(board, 0)
        board[row][col] = CellState.PLAYER_X
        verdict = utils.gameover(board)
        if verbose:
            utils.print_board_with_last_move(board, row, col)
            print GameResult.announce(verdict)
        return verdict

    def run_tournament(self, N=100):
        counter = Counter()
        for i in range(N):
            result = self.run(verbose=False)
            counter[result] += 1
        percentage = [float(counter[result]) / N for result in (GameResult.X_WINS, GameResult.O_WINS, GameResult.DRAW)]
        print '%d runs: (X win, X lose, tie) = %s' % (N, percentage)


def train_RL(strat1, game):
    explore_rate = 0.01
    for i in range(10):
        strat1.set_explore_rate(explore_rate)
        game.run_tournament(N=500)
        print 'q_table size = ', strat1.q_table.stats()
        # explore_rate /= 2
    strat1.q_table.save(PARAM_FILE)


def test_RL(strat_rl, game):
    print 'Evaluating ', game.opponents()
    strat_rl.set_explore_rate(0)
    strat_rl.set_learn_rate(0)

    strat_rl.set_debug(True)
    game.run()

    strat_rl.set_debug(False)
    game.run_tournament(1000)


def run_RL_as_X():
    """
    train an RL strategy, then test it. Training RL takes a bit of time, so we auto-save/load a parameter
    file (in PARAM_FILE)
    """
    from strategies import RobertStrat1, MinMaxStrat, DefensiveStrat1
    from rl import RLStrat
    strat1 = RLStrat(CellState.PLAYER_X, 0.1)
    strat2 = RobertStrat1()  # pick your favorite player
    game = GamePlay(strat1, strat2)
    if os.path.exists(PARAM_FILE):
        strat1.q_table.load(PARAM_FILE)

    train_RL(strat1, game)
    test_RL(strat1, game)


def run_manual():
    """ play a manual game vs a strategy of your choice
    """
    from strategies import Human, RandomPlay, RobertStrat1, MinMaxStrat, DefensiveStrat1
    strat1 = Human()
    strat2 = MinMaxStrat()  # pick your favorite player!
    game = GamePlay(strat1, strat2)
    game.run()
    # game.run_tournament(5000)

if __name__ == '__main__':
    random.seed(time.time())
    run_RL_as_X()
    # run_manual()