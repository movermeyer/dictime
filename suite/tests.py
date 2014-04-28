import unittest
import time
from datetime import datetime
from datetime import timedelta

import suite
from suite.helpers import undefined


class Tests(unittest.TestCase):
    # -----
    # Books
    # -----
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

    # -------
    # Shelves
    # -------

    # -------
    # Library
    # -------
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

    def test_shelf_max(self):
        "max books on shelf"
        s = suite.Shelf(max=4)
        for x in range(4):
            self.assertTrue(s.append(x))
        self.assertFalse(s.append(1))

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

    def test_shelf_checks(self):
        "shelf can check books"
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
        "library can prioritize shelves"
        s1 = suite.Shelf(priority=2, check=lambda s, v: isinstance(v, int))
        s2 = suite.Shelf(priority=1)
        c = suite.Library(s1, s2, fitter=lambda _, su, value: su.priority % 2 == value % 2)
        for x in range(100):
            self.assertTrue(c.append(x))
        self.assertEqual(len(c), 100)
        self.assertEqual(len(s1), 50)
        self.assertEqual(len(s2), 50)

    def test_getters(self):
        "shelf can get books"
        s = suite.Shelf(getter=lambda k: ('value', None, None))
        self.assertEqual(s.get('key'), 'value')
        c = suite.Library(suite.Shelf(getter=lambda k: ('value', None, None)))
        self.assertEqual(c.get('key'), 'value')

    def test_iter(self):
        "can iter shelf"
        s = suite.Shelf()
        [s.append(x) for x in range(10)]
        self.assertListEqual([x for x in s],
                             [(x+1, x) for x in range(10)])


if __name__ == '__main__':
    unittest.main()
