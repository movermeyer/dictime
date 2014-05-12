import unittest
import time
from datetime import datetime
from datetime import timedelta

from dictime import moment


class Tests(unittest.TestCase):
    def test_has_one_value(self):
        "moments have only one value at any moment"
        pass

    def test_future(self):
        "moments can have multiple future values"
        b = moment('a', future=dict(milliseconds=10))
        b.set('b', future=dict(milliseconds=20))
        self.assertRaises(ValueError, b.get)
        time.sleep(.01)
        self.assertEquals(b.get(), 'a')
        time.sleep(.01)
        self.assertEquals(b.get(), 'b')
        self.assertEquals(len(b), 1, "'a' was not removed")

    def tests_expire(self):
        "moments can expire values"
        b = moment()
        b.set('a', expires=datetime.now() + timedelta(milliseconds=10))
        self.assertEquals(b.get(), 'a')
        time.sleep(.01)
        self.assertRaises(ValueError, b.get)
    
    def tests_value(self):
        "moments evicts present"
        b = moment()
        b.set('a')
        b.set('b')
        self.assertEquals(b.get(), 'b')
        b.set('c')
        self.assertEquals(b.get(), 'c')
        self.assertEquals(len(b), 1)
        # replace w/ future
        b.set('d', future=datetime.now() + timedelta(milliseconds=10))
        self.assertEquals(b.get(), 'c')
        self.assertEquals(len(b), 2)
        time.sleep(.01)
        self.assertEquals(b.get(), 'd')

    def test_set(self):
        "moments validate expires/future values"
        self.assertRaises(ValueError, moment().set, 1, 'not a date')
        self.assertRaises(ValueError, moment().set, 1, future='not a date')
        self.assertRaises(AssertionError, moment().set, 1, expires=datetime.now() - timedelta(minutes=10))
        self.assertRaises(AssertionError, moment().set, 1, datetime.now() + timedelta(minutes=10), datetime.now() + timedelta(minutes=20))
