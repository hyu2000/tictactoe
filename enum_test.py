from unittest import TestCase
from collections import namedtuple
import enum


class Result(object):
    X_WIN, O_WIN, DRAW = range(3)


class IntEnumResult(enum.IntEnum):
    YES = 0,
    NO = 1,
    NEVER = 2

    def is_negative(self):
        return self.value >= 1


class EnumResult(enum.Enum):
    YES = (0, 'why, yes!')
    NO =  (1, 'no, thank you')
    NEVER = (2, 'hell no!')

    def __init__(self, value, description):
        self.int_value = value
        self.description = description

    def verbose(self):
        return self.description

    def is_negative(self):
        return self.int_value >= 1


IntResult = namedtuple('Result', "YES NO")._make(range(2))


class EnumTest(TestCase):
    def test_class_vars_mutable(self):
        self.assertEqual(Result.DRAW, 2)
        Result.DRAW = 0
        self.assertEqual(Result.X_WIN, Result.DRAW)

    def test_named_tuple(self):
        self.assertIsInstance(IntResult.YES, int)
        self.assertEqual(0, IntResult.YES)

    def test_intenum(self):
        self.assertEqual(IntEnumResult.YES.name, 'YES')
        self.assertEqual(IntEnumResult.YES.value, 0)

        # easily compare with int
        self.assertIsInstance(IntEnumResult.YES, int)
        self.assertEqual(IntEnumResult.YES, 0)

        self.assertEqual(IntResult.YES, IntEnumResult.YES)

        # access from int
        self.assertEqual(IntEnumResult(1), 1)
        with self.assertRaises(ValueError):
            IntEnumResult(3)

    def test_enum(self):
        self.assertEqual(EnumResult.YES.name, 'YES')
        self.assertEqual(EnumResult.YES.int_value, 0)

        self.assertFalse(EnumResult.YES.is_negative())
        self.assertTrue(EnumResult.NO.is_negative())

        self.assertEqual(EnumResult.NEVER.description, 'hell no!')
