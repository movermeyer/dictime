import itertools
from threading import RLock

from suite.shelf import Shelf
from suite.helpers import KeyGenerator


class Library(object):
    __slots__ = ["_shelves", "_lock", "fitter", "_keygen"]
    def __init__(self, *shelves, **kwargs):
        self._lock = RLock()
        self._shelves = []
        self.fitter = kwargs.get('fitter', None)
        self._keygen = KeyGenerator()
        if shelves:
            map(self.add_shelf, shelves)

    def add_shelf(self, shelf):
        """Add another shelf
        """
        assert isinstance(shelf, Shelf)
        # install shelf
        self._shelves.append(shelf)
        # listen for changes
        shelf.signals.connect("priority-changed", self._resort)
        # replace the key gen
        shelf._keygen = self._keygen
        # replace the locker
        shelf._lock = self._lock
        # resort the library
        self._resort()

    def _resort(self, *_):
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
                if shelf.set(key, value, expires=expires, future=future):
                    return True

        # Now any that check out
        for shelf in self._shelves:
            if shelf._check_value(value) and shelf.set(key, value, expires=expires, future=future):
                return True

        # Now any
        for shelf in self._shelves:
            if shelf.set(key, value, expires=expires, future=future):
                return True

        return False

    @property
    def shelves(self):
        return self._shelves

    def __len__(self):
        return sum([len(s) for s in self._shelves])
    
    def values(self):
        return itertools.chain(*[shelf.values() for shelf in self._shelves])

    def keys(self):
        return itertools.chain(*[shelf.keys() for shelf in self._shelves])

    def clear(self):
        map(lambda s: s.clear(), self._shelves)

    def __iter__(self):
        return self.values()

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, _else=None):
        # Check if its already there
        for shelf in self._shelves:
            try:
                return shelf[key]
            except KeyError:
                continue

        # use getters
        for shelf in self._shelves:
            if shelf.getter:
                try:
                    return shelf[key]
                except KeyError:
                    continue

        # ok, go with else
        return _else

    def remove(self, key):
        for shelf in self._shelves:
            try:
                return shelf.remove(key)
            except KeyError:
                continue
        return False
