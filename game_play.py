from collections import Counter
import random
import time
import os

from utils import CellState, GameResult, Board


PARAM_FILE = '/tmp/rl.pickle'


class GamePlay(object):
    def __init__(self, strategy_x, strategy_o):
        self.players = [strategy_x, strategy_o]

    def opponents(self):
        return '%s vs %s' % (self.players[0].name(), self.players[1].name())

    def run(self, verbose=True):
        board = Board()
        self.players[0].start_game(CellState.PLAYER_X)
        self.players[1].start_game(CellState.PLAYER_O)

        if verbose:
            board.print_board()
        stone = CellState.PLAYER_X
        for i in range(9):
            player = self.players[i % 2]

            row, col = player.next_move(board)

            if board.board[row][col] != CellState.EMPTY:
                print '%s made an invalid move: (%d, %d)' % (player.name(), row, col)
                raise Exception('Debug now!')
            board.board[row][col] = stone
            if verbose:
                print '%dth move, %s picked row %d, col %d' % (i, player.name(), row, col)
                board.print_board_with_last_move(row, col)
            stone = stone.reverse_role()

            verdict = board.evaluate()
            if verdict != GameResult.UNFINISHED:
                break

        if verbose:
            print verdict.announce()
        # end game
        for player in self.players:
            player.end_game(verdict)
        return verdict

    def run_tournament(self, N=100):
        counter = Counter()
        for i in range(N):
            result = self.run(verbose=False)
            counter[result] += 1
        percentage = [float(counter[result]) / N for result in (GameResult.X_WINS, GameResult.O_WINS, GameResult.DRAW)]
        print '%d runs: (X win, X lose, tie) = %s' % (N, percentage)
        return percentage


def train_RL(strat1, game):
    assert strat1.learn_rate > 1e-6
    explore_rate = 0.1
    for i in range(10):
        strat1.set_explore_rate(explore_rate)
        game.run_tournament(N=10000)
        print 'q_table size, #updates = ', strat1.q_table.stats()
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


def load_rl_strat():
    from rl import RLStrat
    strat1 = RLStrat(0.1)
    if os.path.exists(PARAM_FILE):
        strat1.q_table.load(PARAM_FILE)
    return strat1


def run_RL_as_X_against(rl_strat, strat2):
    """
    train an RL strategy, then test it. Training RL takes a bit of time, so we auto-save/load a parameter
    file (in PARAM_FILE)
    """
    game = GamePlay(rl_strat, strat2)

    train_RL(rl_strat, game)
    test_RL (rl_strat, game)


def run_manual_against(strat, human_as=CellState.PLAYER_X):
    """ play a manual game vs a strategy (human in the specified role)
    """
    if human_as == CellState.PLAYER_X:
        game = GamePlay(strategies.Human(), strat)
    else:
        game = GamePlay(strat, strategies.Human())

    game.run()
    # game.run_tournament(5000)


def save_minmax_qtable():
    strat = strategies.MinMaxWithQTable()

    board = Board()
    best_result, best_move = strat.eval_board(board, CellState.PLAYER_X)
    # 3964 states: once we find a win, no need to explore other branches
    print strat.q_table.stats()
    print strat.q_table.stats_by_num_stones().items()

    strat.q_table.save('/tmp/minmax.qtable')


if __name__ == '__main__':
    import strategies

    strat = strategies.MinMaxWithQTable()
    # strat = strategies.WeakenedMinMax('/tmp/minmax.qtable')

    random.seed(time.time())
    rl_strat = load_rl_strat()
    run_RL_as_X_against(rl_strat, strat)

    # when minmax goes first, we can never win, but you'll learn how to achieve a draw!
    # run_manual_against(strat)