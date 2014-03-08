from suite.helpers import KeyGenerator
from suite.shelf import Shelf

class Library(object):
    def __init__(self, *suites, **kwargs):
        self._suites = []
        self._fitter = kwargs.get('fitter', None)
        self._key_gen = KeyGenerator()
        if suites:
            for suite in self._suites:
                suite._key_gen = self._key_gen
            self._suites = sorted(suites)
            

    def push(self, suite):
        assert isinstance(suite, Shelf)
        self._suites.append(suite)
        self._suites = sorted(self._suites)

    def append(self, value):
        """Checks for best fit suite via sorted suites -> fitter
        """
        # try best fit
        for suite in self._suites:
            if self._fitter and suite._check_value(value) and self._fitter(self, suite, value):
                if suite.append(value):
                    return True
        # try any fit
        for suite in self._suites:
            if suite.append(value):
                return True
        return False

    @property
    def suites(self):
        return self._suites

    def __len__(self):
        return sum([len(s) for s in self._suites])
    
    def values(self):
        values = []
        [[values.append(value) for value in suite] for suite in self._suites]
        return values

    def keys(self):
        keys = []
        [[keys.append(key) for key in suite.keys()] for suite in self._suites]
        return keys

    def clear(self):
        [suite.clear() for suite in self._suites]

    def __iter__(self):
        return iter(self.values())

    def __getitem__(self, key):
        for suite in self._suites:
            if key in suite:
                return suite.get(key)

    def get(self, key, _else=None):
        # Check if its already there
        for suite in self._suites:
            if key in suite:
                return suite.get(key)
        # ok, go with else
        if _else is not None:
            return _else
        # try to find a value
        for suite in self._suites:
            returns = suite.get(key)
            if returns is not None:
                return returns

    def remove(self, child):
        for suite in self._suites:
            if suite.has(child):
                return suite.remove(child)
        return None


