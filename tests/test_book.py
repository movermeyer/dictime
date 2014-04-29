import unittest
import time
from datetime import datetime
from datetime import timedelta

import suite
from suite.helpers import undefined


class Tests(unittest.TestCase):
    def test_book_future(self):
        "book can have multiple future values"
        b = suite.Book()
        b.set('a', future=datetime.now() + timedelta(milliseconds=10))
        b.set('b', future=datetime.now() + timedelta(milliseconds=20))
        self.assertEquals(b.get()[1], undefined)
        time.sleep(.01)
        self.assertEquals(b.get()[1], 'a')
        time.sleep(.01)
        self.assertEquals(b.get()[1], 'b')
        self.assertEquals(len(b), 1, "'a' was not removed")

    def test_books_expire(self):
        "books can expire values"
        b = suite.Book()
        b.set('a', expires=datetime.now() + timedelta(milliseconds=10))
        self.assertEquals(b.get()[1], 'a')
        time.sleep(.01)
        self.assertEquals(b.get()[1], undefined)
    
    def test_books_value(self):
        "books evicts present"
        b = suite.Book()
        b.set('a')
        b.set('b')
        self.assertEquals(b.get()[1], 'b')
        b.set('c')
        self.assertEquals(b.get()[1], 'c')
        self.assertEquals(len(b), 1)
        # replace w/ future
        b.set('d', future=datetime.now() + timedelta(milliseconds=10))
        self.assertEquals(b.get()[1], 'c')
        self.assertEquals(len(b), 2)
        time.sleep(.01)
        self.assertEquals(b.get()[1], 'd')

    def test_book_set(self):
        "book validates expires/future values"
        self.assertRaises(AssertionError, suite.Book().set, 1, 'not a date')
        self.assertRaises(AssertionError, suite.Book().set, 1, future='not a date')
        self.assertRaises(AssertionError, suite.Book().set, 1, expires=datetime.now() - timedelta(minutes=10))
        self.assertRaises(AssertionError, suite.Book().set, 1, datetime.now() + timedelta(minutes=10), datetime.now() + timedelta(minutes=20))
