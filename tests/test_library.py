import unittest

import suite


class Tests(unittest.TestCase):
    def test_library_prioritize(self):
        "library will prioritize shelves"
        l = suite.Library(suite.Shelf(max=4, priority=2),
                          suite.Shelf(max=3, priority=1),
                          suite.Shelf(max=3, priority=10),
                          suite.Shelf(max=3, priority=None))
        self.assertListEqual(map(lambda s: s.priority, l.shelves), [None, 1, 2, 10])

    def test_prio_change(self):
        "library watches for priority changes"
        a = suite.Shelf(priority=1)
        b = suite.Shelf(priority=2)
        l = suite.Library(a, b)
        self.assertListEqual(l.shelves, [a, b])
        # change shelf priority
        a.priority = 3
        self.assertListEqual(l.shelves, [b, a])

    def test_add_shelves(self):
        "library can add shelves"
        l = suite.Library()
        a = suite.Shelf()
        l.add_shelf(a)
        self.assertListEqual(l.shelves, [a])

    def test_library_max(self):
        "max books in library"
        s1 = suite.Shelf(max=4, priority=2)
        s2 = suite.Shelf(max=3, priority=1)
        c = suite.Library(s1, s2)
        for x in range(3):
            self.assertTrue(c.append(x))
            self.assertEqual(len(s2), x+1)
        for x in range(4):
            self.assertTrue(c.append(x))
            self.assertEqual(len(s1), x+1)
        self.assertEqual(c.append(x), False)

    def test_library_fitter(self):
        "library can prioritize shelves"
        s1 = suite.Shelf(priority=2, validate=lambda s, v: isinstance(v, int))
        s2 = suite.Shelf(priority=1)
        c = suite.Library(s1, s2, fitter=lambda _, su, value: su.priority % 2 == value % 2)
        for x in range(100):
            self.assertTrue(c.append(x))
        self.assertEqual(len(c), 100)
        self.assertEqual(len(s1), 50)
        self.assertEqual(len(s2), 50)

    def test_library_values(self):
        "get library values"
        c = suite.Library(suite.Shelf(max=2), suite.Shelf(max=2))
        [c.append(x) for x in 'abcd']
        self.assertItemsEqual(c.values(), list('abcd'))

    def test_library_keys(self):
        "get library keys"
        c = suite.Library(suite.Shelf(max=2), suite.Shelf(max=2))
        [c.append(x) for x in 'abcd']
        self.assertItemsEqual(c.keys(), map(int,list('1234')))

    def test_library_clear(self):
        "clear library"
        c = suite.Library(suite.Shelf(max=2), suite.Shelf(max=2))
        [c.append(x) for x in 'abcd']
        c.clear()
        self.assertEqual(len(c), 0)

    def test_library_iter(self):
        c = suite.Library(suite.Shelf(max=2), suite.Shelf(max=2))
        [c.append(x) for x in 'abcd']
        self.assertListEqual([x for x in c], list('abcd'))

    def test_libary_getitem(self):
        "library key via __getitem__"
        c = suite.Library(suite.Shelf(max=2), suite.Shelf(max=2))
        [c.append(x) for x in 'abcd']
        self.assertEqual(c[1], 'a')
        self.assertEqual(c[2], 'b')
        self.assertEqual(c[3], 'c')
        self.assertEqual(c[4], 'd')

    def test_library_requires_shelves(self):
        "library must have shelves to add books"
        pass

    def test_library_remove(self):
        "library can remove by key"
        c = suite.Library(suite.Shelf())
        key = c.append('a')
        self.assertFalse(c.remove('not found'))
        self.assertTrue(c.remove(key))
