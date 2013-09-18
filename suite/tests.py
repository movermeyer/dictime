import unittest
import suite


class Tests(unittest.TestCase):
    def testOne(self):
        s1 = suite.Suite(max=4, priority=1)
        s2 = suite.Suite(max=3, priority=1)
        c = suite.Collection(s1, s2)
        for x in range(4):
            self.assertTrue(c.append(x))
            self.assertEquals(len(s1), x+1)

        for x in range(3):
            self.assertTrue(c.append(x))
            self.assertEquals(len(s1), 4)
            self.assertEquals(len(s2), x+1)
    

    def testTwo(self):
        elcount = 0
        s = suite.Suite(max=3,
                        setter=lambda k, v: isinstance(v, str),
                        changed=lambda su: self.assertEquals(len(su), elcount))
        self.assertEquals(s.max, 3)
        elcount = 1
        s.append("Steve")
        # Cannot append numbers
        self.assertFalse(s.append(10))
        elcount = 2
        s.append("Joe")
        elcount = 3
        s.append("Andy")
        # Max reached
        self.assertFalse(s.append('Eric'))

if __name__ == '__main__':
    unittest.main()
