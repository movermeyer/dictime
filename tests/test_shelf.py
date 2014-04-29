import unittest

import suite


class Tests(unittest.TestCase):
    def test_checks(self):
        "shelf can validate values"
        s1 = suite.Shelf(validate=lambda s, v: isinstance(v, str))
        s2 = suite.Shelf(validate=lambda s, v: isinstance(v, int))
        l = suite.Library(s1, s2)
        _id = l.append(75)
        self.assertTrue(_id is not False)
        self.assertEqual(len(s2), 1)
        self.assertEqual(len(s1), 0)
        self.assertTrue(l.append("steve"))
        self.assertEqual(len(s2), 1)
        self.assertEqual(len(s1), 1)
        self.assertEqual(len(l), 2)

    def test_fetch(self):
        "shelf can lookup values"
        s = suite.Shelf(lookup=lambda k: ('value', None, None))
        self.assertEqual(s.get('x'), 'value')

    def test_iter(self):
        "can iter shelf"
        s = suite.Shelf()
        s.append(*range(10))
        self.assertListEqual([x[1] for x in s],
                             range(10))

    def test_max(self):
       "max books on shelf"
       s = suite.Shelf(max=4)
       for x in range(4):
           self.assertTrue(s.append(x))
       self.assertFalse(s.append(1))

    def test_refresh(self):
        "shelves can expire all its contents"
        self.skipTest("wip")
