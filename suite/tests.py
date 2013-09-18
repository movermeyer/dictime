import unittest
import suite


class Tests(unittest.TestCase):
    def testCollectionMax(self):
        s1 = suite.Suite(max=4, priority=2)
        s2 = suite.Suite(max=3, priority=1)
        c = suite.Collection(s1, s2)
        self.assertListEqual(c.suites, [s2, s1])
        for x in range(3):
            self.assertTrue(c.append(x))
            self.assertEquals(len(s2), x+1)
        for x in range(4):
            self.assertTrue(c.append(x))
            self.assertEquals(len(s1), x+1)
        self.assertFalse(c.append(1))

    def testSuiteChecks(self):
        s1 = suite.Suite(check=lambda s, v: isinstance(v, str))
        s2 = suite.Suite(check=lambda s, v: isinstance(v, int))
        c = suite.Collection(s1, s2)
        self.assertTrue(c.append(75))
        self.assertEquals(len(s2), 1)
        self.assertEquals(len(s1), 0)
        self.assertTrue(c.append("steve"))
        self.assertEquals(len(s2), 1)
        self.assertEquals(len(s1), 1)
        self.assertEquals(len(c), 2)

    def testSuiteChanged(self):
        elcount = 0
        s = suite.Suite(max=3,
                        check=lambda s, v: isinstance(v, str),
                        changed=lambda su: self.assertEquals(len(su), elcount))
        self.assertEquals(s.max, 3)
        elcount = 1
        s.append("Steve")
        elcount = 2
        s.append("Joe")
        elcount = 3
        s.append("Andy")
        # Max reached
        self.assertFalse(s.append('Eric'))
        # Cannot append numbers
        self.assertFalse(s.append(10))

    def testCollectionFitter(self):
        s1 = suite.Suite(priority=2, check=lambda s, v: isinstance(v, int))
        s2 = suite.Suite(priority=1)
        c = suite.Collection(s1, s2, fitter=lambda _, su, value: su.priority % 2 == value % 2)
        for x in range(100):
            self.assertTrue(c.append(x))
        self.assertEquals(len(c), 100)
        self.assertEquals(len(s1), 50)
        self.assertEquals(len(s2), 50)


if __name__ == '__main__':
    unittest.main()