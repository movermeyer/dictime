from suite.shelf import Shelf
from suite.helpers import Undefined
from suite.helpers import KeyGenerator


class Library(object):
    def __init__(self, *shelves, **kwargs):
        self._shelves = []
        self.fitter = kwargs.get('fitter', None)
        self._key_gen = KeyGenerator()
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
        # set the labeler
        shelf._key_gen = self._key_gen
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
            if shelf._check_value(value) \
              and shelf.set(key, value, expires=expires, future=future):
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
                result = shelf.get(key, Undefined)
                if result is not Undefined:
                    return result

        # ok, go with else
        return _else

    def remove(self, key):
        for shelf in self._shelves:
            if shelf.has(key):
                return shelf.remove(key)
        return None
