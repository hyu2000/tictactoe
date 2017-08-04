"""
test generator in recursion situation
"""
from unittest import TestCase
from collections import namedtuple


def count_down(n):
    while n >= 0:
        yield n
        n -= 1


class CountDownTest(TestCase):
    def testGen(self):
        for i in count_down(4):
            print i
        print 'done'

    def test2(self):
        for i in count_down(2):
            for j in count_down(2):
                print i, j

        print 'done'


class Result(object):
    X_WIN, O_WIN, DRAW = range(3)


class NamedTupleTest(TestCase):
    def test_class_vars_mutable(self):
        self.assertEqual(Result.DRAW, 2)
        Result.DRAW = 0
        self.assertEqual(Result.X_WIN, Result.DRAW)


class Result(namedtuple('Result', "YES NO")):
    def __str__(self):
        pass