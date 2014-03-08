import unittest
import time
from datetime import datetime
from datetime import timedelta

import suite


class Tests(unittest.TestCase):
    def test_library_max(self):
        s1 = suite.Shelf(max=4, priority=2)
        s2 = suite.Shelf(max=3, priority=1)
        c = suite.Library(s1, s2)
        self.assertListEqual(c.shelves, [s2, s1])
        for x in range(3):
            self.assertTrue(c.append(x))
            self.assertEqual(len(s2), x+1)
        for x in range(4):
            self.assertTrue(c.append(x))
            self.assertEqual(len(s1), x+1)
        self.assertEqual(c.append(x), False)

    def test_shelf_checks(self):
        s1 = suite.Shelf(check=lambda s, v: isinstance(v, str))
        s2 = suite.Shelf(check=lambda s, v: isinstance(v, int))
        l = suite.Library(s1, s2)
        _id = l.append(75)
        self.assertTrue(_id is not False)
        self.assertEqual(len(s2), 1)
        self.assertEqual(len(s1), 0)
        self.assertTrue(l.append("steve"))
        self.assertEqual(len(s2), 1)
        self.assertEqual(len(s1), 1)
        self.assertEqual(len(l), 2)

    def test_library_fitter(self):
        s1 = suite.Shelf(priority=2, check=lambda s, v: isinstance(v, int))
        s2 = suite.Shelf(priority=1)
        c = suite.Library(s1, s2, fitter=lambda _, su, value: su.priority % 2 == value % 2)
        for x in range(100):
            self.assertTrue(c.append(x))
        self.assertEqual(len(c), 100)
        self.assertEqual(len(s1), 50)
        self.assertEqual(len(s2), 50)

    def test_getters(self):
        s = suite.Shelf(getter=lambda k: ('value', None, None))
        self.assertEqual(s.get('key'), 'value')
        c = suite.Library(suite.Shelf(getter=lambda k: ('value', None, None)))
        self.assertEqual(c.get('key'), 'value')

    def test_expires_future(self):
        s = suite.Shelf()
        k1 = s.append('steve', expires=datetime.now() + timedelta(seconds=1))
        k2 = s.append('eric', expires=datetime.now() + timedelta(seconds=1))
        k3 = s.append('joe', expires=datetime.now() + timedelta(seconds=1))
        k4 = s.append('madison', future=datetime.now() + timedelta(seconds=1))
        self.assertEqual(s.get(k1), 'steve')
        self.assertEqual(s.get(k2), 'eric')
        self.assertEqual(s.get(k3), 'joe')
        self.assertTrue(s.get(k4) is suite.Undefined)
        self.assertEqual(len(s), 3)
        time.sleep(1)
        self.assertTrue(s.get(k1) is suite.Undefined)
        self.assertTrue(s.get(k2) is suite.Undefined)
        self.assertTrue(s.get(k3) is suite.Undefined)
        self.assertEqual(s.get(k4), 'madison')
        self.assertEqual(len(s), 1)

    def test_iter(self):
        s = suite.Shelf()
        [s.append(x) for x in range(10)]
        self.assertListEqual([x for x in s],
                             [(x+1, x) for x in range(10)])

if __name__ == '__main__':
    unittest.main()
