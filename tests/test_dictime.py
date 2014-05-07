import time
import unittest
from datetime import timedelta

from dictime import dictime


class Tests(unittest.TestCase):
    def test_iter(self):
        "dictime can iter"
        s = dictime(one=1, two=2, three=3)
        self.assertItemsEqual([x for x in s], [('one', 1), ('two', 2), ('three', 3)])

    def test_no_kwargs(self):
        s = dictime()
        self.assertEqual(len(s), 0)
        s['key'] = 'value'
        self.assertEqual(len(s), 1)

    def test_clear(self):
        s = dictime(one=1, two=2, three=3)
        self.assertEqual(len(s), 3)
        s.clear()
        self.assertEqual(len(s), 0)

    def test_values(self):
        s = dictime(one=1, two=2, three=3)
        self.assertItemsEqual(s.values(), [1,2,3])

    def test_keys(self):
        s = dictime(one=1, two=2, three=3)
        self.assertItemsEqual(s.keys(), ['one', 'two', 'three'])

    def test_nonzero(self):
        s = dictime(one=1, two=2, three=3)
        self.assertTrue(s.__nonzero__())
        s = dictime()
        self.assertFalse(s.__nonzero__())

    def test_remove(self):
        s = dictime(one=1, two=2, three=3)
        del s['one']
        self.assertNotIn('one', s)
        s.remove('two')
        self.assertNotIn('two', s)

    def test_setdefault(self):
        s = dictime()
        self.assertEqual(len(s), 0)
        s.setdefault('key', 'value')
        self.assertEqual(len(s), 1)
        self.assertEqual(s.get('key'), 'value')
        s.setdefault('key', 'different')
        self.assertEqual(s.get('key'), 'value')

    def test_expire(self):
        "dictime can expire all its contents"
        s = dictime(one=1, two=2, three=3)
        s.set_expires(timedelta(milliseconds=100))
        time.sleep(.2)
        self.assertFalse(s.has_key('one'), "the dicttime was not emptied")
        s['one'] = "something_else"
        self.assertEqual(s['one'], "something_else")
        time.sleep(.1)
        self.assertFalse(s.has_key('one'), "the dicttime was not emptied")

    def test_contains(self):
        s = dictime(one=1, two=2, three=3)
        self.assertIn('one', s)
        self.assertNotIn('__', s)
    
    def test_expire_callback(self):
        "dictime can expire and callback"
        s = dictime(fruit="orange")
        s.set_expires(timedelta(milliseconds=100), lambda s: s.set('fruit', 'apple'))
        self.assertEqual(s["fruit"], 'orange')
        time.sleep(.1)
        self.assertEqual(s["fruit"], 'apple')

    def test_getitem(self):
        s = dictime(one=1, two=2, three=3)
        self.assertEqual(s['one'], 1)
        self.assertRaises(KeyError, s.__getitem__, '__')
