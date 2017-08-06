import random
import unittest
import time

from strategies import MinMaxStrat, AntiMinMaxStrat, DefensiveStrat1, Human
from game_play import GamePlay
from utils import GameResult


class Competition(unittest.TestCase):
    def setUp(self):
        random.seed(time.time())

    def test_anti_minmax(self):
        game = GamePlay(MinMaxStrat(), AntiMinMaxStrat())
        verdict = game.run(verbose=True)
        self.assertEqual(verdict, GameResult.DRAW)

        pctg = game.run_tournament(3)
        self.assertAlmostEqual(pctg[2], 1.0)

    def test_def_minmax(self):
        # game = GamePlay(, AntiMinMaxStrat())
        verdict = game.run(verbose=True)
        # self.assertEqual(verdict, GameResult.DRAW)

        game.run_tournament(3)
