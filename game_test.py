import random
import unittest
import time

from strategies import MinMaxStrat, AntiMinMaxStrat, DefensiveStrat1, MinMaxWithQTable, WeakenedMinMax
from game_play import GamePlay
from utils import GameResult


class Competition(unittest.TestCase):
    def setUp(self):
        random.seed(time.time())

    def test_anti_minmax(self):
        # MinMax would also pass, but way slower
        game = GamePlay(MinMaxWithQTable(), AntiMinMaxStrat())
        verdict = game.run(verbose=True)
        self.assertEqual(verdict, GameResult.DRAW)

        pctg = game.run_tournament(100)
        self.assertAlmostEqual(pctg[2], 1.0)

    def test_weakened_vs_minmax(self):
        game = GamePlay(MinMaxWithQTable(), WeakenedMinMax())
        verdict = game.run(verbose=True)
        self.assertEqual(verdict, GameResult.DRAW)

        pctg = game.run_tournament(100)
        self.assertAlmostEqual(pctg[2], 1.0)

