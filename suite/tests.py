import unittest
import time
from datetime import datetime
from datetime import timedelta

import suite


class Tests(unittest.TestCase):
    def _test_collection_max(self):
        s1 = suite.Shelf(max=4, priority=2)
        s2 = suite.Shelf(max=3, priority=1)
        c = suite.Library(s1, s2)
        self.assertListEqual(c.suites, [s2, s1])
        for x in range(3):
            self.assertTrue(c.append(x))
            self.assertEqual(len(s2), x+1)
        for x in range(4):
            self.assertTrue(c.append(x))
            self.assertEqual(len(s1), x+1)
        self.assertRaises(suite.MaxHit, c.append, x)

    def test_suite_checks(self):
        s1 = suite.Shelf(check=lambda s, v: isinstance(v, str))
        s2 = suite.Shelf(check=lambda s, v: isinstance(v, int))
        c = suite.Library(s1, s2)
        self.assertTrue(c.append(75))
        self.assertEqual(len(s2), 1)
        self.assertEqual(len(s1), 0)
        self.assertTrue(c.append("steve"))
        self.assertEqual(len(s2), 1)
        self.assertEqual(len(s1), 1)
        self.assertEqual(len(c), 2)

    def test_suite_changed(self):
        elcount = 0
        s = suite.Shelf(max=3,
                        check=lambda s, v: isinstance(v, str),
                        changed=lambda su: self.assertEqual(len(su), elcount))
        self.assertEqual(s.max, 3)
        elcount = 1
        self.assertEqual(s.append("Steve"), 1)
        elcount = 2
        self.assertEqual(s.append("Joe"), 2)
        # Cannot append numbers
        self.assertFalse(s.append(10))
        elcount = 3
        self.assertEqual(s.append("Andy"), 3)
        
        # Max reached
        self.assertRaises(suite.MaxHit, s.append, 'Eric')

    def test_collection_fitter(self):
        s1 = suite.Shelf(priority=2, check=lambda s, v: isinstance(v, int))
        s2 = suite.Shelf(priority=1)
        c = suite.Library(s1, s2, fitter=lambda _, su, value: su.priority % 2 == value % 2)
        for x in range(100):
            self.assertTrue(c.append(x))
        self.assertEqual(len(c), 100)
        self.assertEqual(len(s1), 50)
        self.assertEqual(len(s2), 50)

    def test_default(self):
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
        self.assertEqual(s.get(k4), None)
        self.assertEqual(len(s), 3)
        time.sleep(1)
        self.assertEqual(s.get(k1), None)
        self.assertEqual(s.get(k2), None)
        self.assertEqual(s.get(k3), None)
        self.assertEqual(s.get(k4), 'madison')
        self.assertEqual(len(s), 1)

if __name__ == '__main__':
    unittest.main()
