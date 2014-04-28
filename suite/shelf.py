import signals
from threading import RLock
from datetime import datetime
from datetime import timedelta

from suite.helpers import undefined
from suite.helpers import KeyGenerator


class Book(object):
    """Books will always have (1) value at a time.
    Any new values added will replace the prior value with no discrimination
    """
    __slots__ = ['futures', 'lock']
    def __init__(self, value=undefined, expires=None, future=None):
        self.futures = []
        # thread safety
        self.lock = RLock()
        if value != undefined:
            self.set(value, expires, future)

    def get(self):
        """Called to get the asset values and if it is valid
        """
        now = datetime.now()
        with self.lock:
            active = []
            for i, vef in enumerate(self.futures):
                # has expired
                if (vef[1] or datetime.max) <= now:
                    self.futures.pop(i)
                    continue
                # in future
                elif (vef[2] or datetime.min) >= now:
                    continue
                active.append(i)

            if active:
                # this will evict values old values
                # because new ones are "more recent" via future
                values = self.futures[active[-1]]
                for i in active[:-1]:
                    self.futures.pop(i)
                return self.futures.index(values), values[0]
            return None, undefined

    def __len__(self):
        return len(self.futures)

    def evict(self):
        key, value = self.get()
        if key:
            self.futures.pop(key)

    def set(self, value, expires=None, future=None):
        # this needs to change, because of TZ issues
        now = datetime.now()
        assert expires is None or expires > now, "already expired"
        assert future is None or future > now, "future must be in the future"
        if expires and future:
            assert future < expires, "expires before existing"

        if future and future < now:
            self.evict()

        self.futures.append((value, expires, future))


class Shelf(object):
    """A groovy dictonary on steroids.
    """
    __slots__ = ["getter", "checker", "changed", "_priority",
                 "yielder", "refresh", "signals", 
                 "_lastrefresh", "max", "_dict", "_key_gen"]
    
    def __init__(self, getter=None, check=None, changed=None, yielder=None, 
                 refresh=None, max=None, priority=0):
        # set custom functions
        self.getter = getter
        self.checker = check
        self.changed = changed
        self.yielder = yielder
        self.refresh = refresh
        self._lastrefresh = datetime.now() if self.refresh else None
        self.max = max
        self._priority = priority
        self.signals = signals.Signals(self, "shelf-refresh", "priority-changed",
                                             "asset-removed", "asset-added")

        self._dict = {}
        self._key_gen = KeyGenerator()
        # default method for sorting

    def _get_next_key(self):
        """Serial integar generator
        """
        key = self._key_gen.next()
        if key not in self._dict:
            return key
        while key in self._dict:
            key = self._key_gen.next()
        return key

    def _refresh(self):
        if self.refresh:
            if isinstance(self.refresh, datetime) and datetime.now() >= self.refresh:
                self.refresh = None
                self.signals.emit("shelf-refresh")
            elif isinstance(self.refresh, timedelta) and datetime.now() >= self._lastrefresh + self.refresh:
                self._lastrefresh = datetime.now()
                self.signals.emit("shelf-refresh")

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

    def get(self, key, _else=undefined, tz=None):
        """The method to get an assets value
        """
        self._refresh()
        if key in self._dict:
            # get the asset, call it
            _, value = self._dict[key].get()
            # asset expired
            return value if value is not undefined else _else
        # asset not found, is there a getter?
        elif self.getter is not None:
            if self._max_hit():
                # sorry, max hit, cant even look for a new key.
                return _else
            # getter must return, the value, expires and future
            try:
                value, expires, future = self.getter(key)
                # set the data
                self._dict[key] = Book(value, expires, future)
                # return the asset, use this method to make sure the Expires/Future
                return self.get(key)
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
        if key and (self._check_value(value) or not check):
            self._dict[key].set(value, expires=expires, future=future)
            self.signals.emit("asset-added", key, value)
            return key
        else:
            if self._max_hit():
                return False
            if (check and self._check_value(value)) or not check:
                key = self._get_next_key()
                self._dict[key] = Book(value, expires=expires, future=future)
                self.signals.emit("asset-added", key, value)
                return key
            return False

    def append(self, value, expires=None, future=None, check=True):
        """Add a new value to the suite
        """
        return self.set(None, value, expires=expires, future=future, check=check)

    def setdefault(self, key, value, expires=None, future=None, check=True):
        if self.has(key):
            return self.get(key)
        else:
            return self.set(key, value, expires=expires, future=future, check=check)

    # -------------
    # Deletes
    # -------------
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

    # -------------
    # Basics
    # -------------
    def has(self, key):
        """Does the key exist?
        This method will check to see if it has expired too.
        """
        return self.get(key) is not undefined

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

    # -------------
    # Callbacks
    # -------------
    def _check_value(self, value):
        if hasattr(self.checker, "__call__"):
            return self.checker(self, value) is True
        else:
            return True

    def _max_hit(self):
        return self.max is not None and len(self) >= self.max
