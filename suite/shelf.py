import signals
from threading import RLock
from datetime import datetime
from datetime import timedelta

from .book import Book
from .helpers import undefined
from .helpers import KeyGenerator


class Shelf(object):
    __slots__ = ["_lookup", "_validate", "_priority",
                 "_expires", "signals", "__lock",
                 "_last_expired", "_max", "_dict", "__keygen"]

    def __init__(self, lookup=None, validate=None, expires=None, max=None, priority=0):
        # set custom functions
        self._lookup = lookup
        assert hasattr(lookup, "__call__") or lookup is None, "lookup must be callable"

        self._validate = validate
        assert hasattr(validate, "__call__") or validate is None, "validate must be callable"

        self._expires = expires
        self._last_expired = datetime.now() if expires else None
        assert expires is None or isinstance(expires, timedelta), "expires is not a valid type"

        self._max = max
        assert isinstance(self._max, (int, type(None))), "max must be an integer"

        self._priority = priority
        assert isinstance(self._priority, (int, type(None))), "priority must be an integer"

        self._dict = {}
        self.__keygen = None
        self.__lock = None

        self.signals = signals.Signals(self, "priority-changed", "asset-removed", "asset-added")

    @property
    def _keygen(self):
        if self.__keygen is None:
            self.__keygen = KeyGenerator()
        return self.__keygen

    @_keygen.setter
    def _keygen(self, keygen):
        self.__keygen = keygen

    @property
    def _lock(self):
        if self.__lock is None:
            self.__lock = RLock()
        return self.__lock

    @_lock.setter
    def _lock(self, lock):
        self.__lock = lock

    def _get_next_key(self):
        """Serial integer generator
        """
        key = self._keygen.next()
        if key not in self._dict:
            return key
        while key in self._dict:
            key = self._keygen.next()
        return key

    def _expired(self):
        if self._expires and self._last_expired:
            now = datetime.now()
            if (self._last_expired + self._expires) <= now:
                self._last_expired = now
                self._dict = {}
                return True
        return False

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, priority):
        self._priority = priority
        self.signals.emit('priority-changed', priority)

    # ----
    # Gets
    # ----
    def __getitem__(self, key):
        """Return the value or raise KeyError
        """
        if key in self._dict:
            return self.get(key)
        raise KeyError(key)

    def keys(self):
        """Will only return the current keys
        """
        keys = []
        for key in self._dict.keys():
            _, value = self._dict[key].get()
            if value is not undefined:
                keys.append(key)
        return keys

    def values(self):
        """Will only return the current values
        """
        values = []
        for key in self._dict.keys():
            _, value = self._dict[key].get()
            if value is not undefined:
                values.append(value)
        return values

    def get(self, key, _else=None):
        """The method to get an assets value
        """
        with self._lock:
            # see if everything expired
            if self._expired():
                return _else
            try:
                _, value = self._dict[key].get()
                return value
            except KeyError:
                # sorry, max hit, cant even look for a new key.
                if self._max_hit():
                    return _else
                # asset not found, lookup
                elif self._lookup:
                    # lookup must return, the value, expires and future
                    try:
                        value, expires, future = self._lookup(key)
                        # set the data
                        self._dict[key] = Book(value, expires, future, lock=self._lock)
                        # return the asset, use this method to make sure the Expires/Future
                        return value
                    except KeyError:
                        # no asset exists, dont save it as None
                        pass
            # all else, return the else
            return _else

    # ----
    # Sets
    # ----
    def setall(self, _dict):
        """Quietly set the entire cache
        """
        assert isinstance(_dict, dict), "dict object required"
        (self.set(k, v) for k, v in _dict.iteritems())
    
    def set(self, key, value, expires=None, future=None, check=True):
        """Set a value
        """
        # assert the values above
        with self._lock:
            if key and (not check or self._check_value(value)):
                self._dict[key].set(value, expires=expires, future=future)
                self.signals.emit("asset-added", key, value)
                return key
            else:
                if self._max_hit():
                    return False
                if not check or self._check_value(value):
                    key = self._get_next_key()
                    self._dict[key] = Book(value, expires=expires, future=future, lock=self._lock)
                    self.signals.emit("asset-added", key, value)
                    return key
                return False

    def append(self, *values, **kwargs):
        """Add a new value to the suite
        """
        expires, future, check = kwargs.get('expires'), kwargs.get('future'), kwargs.get('check', True)
        keys = map(lambda v: self.set(None, v, expires, future, check), values)
        return keys[0] if len(keys) == 1 else keys

    def setdefault(self, key, value, expires=None, future=None, check=True):
        if self.has(key):
            return self.get(key)
        else:
            return self.set(key, value, expires=expires, future=future, check=check)

    # -------
    # Deletes
    # -------
    def remove(self, key):
        """Removes a key from the Suite
        """
        del self._dict[key]
        self.signals.emit("asset-removed", key)
        return True

    def __delitem__(self, key):
        self.remove(key)

    def clear(self):
        """Delete all keys
        """
        self._dict = {}

    # ------
    # Basics
    # ------
    def has_key(self, key):
        """Does the key exist?
        This method will check to see if it has expired too.
        """
        return self.get(key, undefined) is not undefined

    def __contains__(self, key):
        """Time insensitive
        """
        return self.has(key)

    def __len__(self):
        """Time insensitive
        """
        length = 0
        for key in self._dict.keys():
            _, value = self._dict[key].get()
            if value is not undefined:
                length += 1
        return length

    def __iter__(self):
        for key in self._dict:
            value = self.get(key, undefined)
            if value is not undefined:
                yield key, value

    def pos(self, child):
        """returns the index this child is found at
        """
        return self.values().index(child)

    # ---------
    # Comparing
    # ---------
    def __lt__(self, other):
        if not isinstance(other, Shelf):
            return NotImplemented
        else:
            return self.priority < other.priority

    def __gt__(self, other):
        if not isinstance(other, Shelf):
            return NotImplemented
        else:
           return self.priority > other.priority

    def __eq__(self, other):
        if not isinstance(other, Shelf):
            return NotImplemented
        else:
            return self.priority == other.priority

    # ---------
    # Callbacks
    # ---------
    def _check_value(self, value):
        try:
            return self._validate(self, value) is True if self._validate else True
        except:
            return False

    def _max_hit(self):
        return self._max is not None and len(self) >= self._max
