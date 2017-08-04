"""
test generator in recursion situation
"""
from unittest import TestCase


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
