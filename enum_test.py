from unittest import TestCase
from collections import namedtuple
import enum


class Result(object):
    X_WIN, O_WIN, DRAW = range(3)


# has to be IntEnum
class EnumResult(enum.IntEnum):
    YES = 0,
    NO = 1,
    NEVER = 2

    def is_negative(self):
        return self.value >= 1


IntResult = namedtuple('Result', "YES NO")._make(range(2))


class EnumTest(TestCase):
    def test_class_vars_mutable(self):
        self.assertEqual(Result.DRAW, 2)
        Result.DRAW = 0
        self.assertEqual(Result.X_WIN, Result.DRAW)

    def test_named_tuple(self):
        self.assertIsInstance(IntResult.YES, int)
        self.assertEqual(0, IntResult.YES)

    def test_enum(self):
        self.assertEqual(EnumResult.YES.name, 'YES')
        self.assertEqual(EnumResult.YES.value, 0)

        self.assertFalse(EnumResult.YES.is_negative())
        self.assertTrue(EnumResult.NO.is_negative())
