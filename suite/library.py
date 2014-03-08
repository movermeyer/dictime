from suite.shelf import Shelf
from suite.helpers import MaxHit
from suite.helpers import Undefined
from suite.helpers import KeyGenerator


class Library(object):
    def __init__(self, *suites, **kwargs):
        self._shelves = []
        self.fitter = kwargs.get('fitter', None)
        self._key_gen = KeyGenerator()
        if suites:
            for suite in self._shelves:
                suite._key_gen = self._key_gen
            self._shelves = sorted(suites)

    def push(self, suite):
        """Add another shelf
        """
        assert isinstance(suite, Shelf)
        self._shelves.append(suite)
        self._shelves = sorted(self._shelves)

    def append(self, value, expires=None, future=None):
        return self.set(None, value, expires=expires, future=future)

    def set(self, key, value, expires=None, future=None):
        """Checks for best fit suite via sorted suites -> fitter
        """
        # Check for fitters first
        for shelf in self._shelves:
            # must fit
            if self.fitter and self.fitter(self, shelf, value) and shelf._check_value(value):
                try:
                    return shelf.set(key, value, expires=expires, future=future)
                except MaxHit:
                    pass

        # Now any that check out
        for shelf in self._shelves:
            try:
                if shelf._check_value(value):
                    return shelf.set(key, value, expires=expires, future=future)
            except MaxHit:
                pass

        # Now any
        for shelf in self._shelves:
            try:
                return shelf.set(key, value, expires=expires, future=future)
            except MaxHit:
                pass

        return False

    @property
    def shelves(self):
        return self._shelves

    def __len__(self):
        return sum([len(s) for s in self._shelves])
    
    def values(self):
        values = []
        [[values.append(value) for value in shelf] for shelf in self._shelves]
        return values

    def keys(self):
        keys = []
        [[keys.append(key) for key in shelf.keys()] for shelf in self._shelves]
        return keys

    def clear(self):
        [shelf.clear() for shelf in self._shelves]

    def __iter__(self):
        return iter(self.values())

    def __getitem__(self, key):
        for shelf in self._shelves:
            if key in shelf:
                return shelf.get(key)

    def get(self, key, _else=None):
        # Check if its already there
        for shelf in self._shelves:
            if shelf.has(key):
                return shelf.get(key)

        # use getters
        for shelf in self._shelves:
            if shelf.getter:
                try:
                    result = shelf.get(key, Undefined)
                    if result is not Undefined:
                        return result
                except MaxHit:
                    pass

        # ok, go with else
        return _else

    def remove(self, key):
        for shelf in self._shelves:
            if shelf.has(key):
                return shelf.remove(key)
        return None
