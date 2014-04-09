import signals
from datetime import datetime
from datetime import timedelta

from suite.helpers import MaxHit
from suite.helpers import Undefined
from suite.helpers import KeyGenerator


class Book(object):
    __slots__ = ['assets']
    def __init__(self, value, expires=None, future=None):
        self.assets = [(value, expires, future)]

    def __call__(self, tz=None):
        """Called to get the asset values and if it is valid
        
        valid: True =>  Is valid
               False => Has expired, destory it
               None =>  Future, do nothing
        """
        now = datetime.now(tz)
        for value, expires, future in self.assets:
            # has expired
            if expires is not None and expires <= now:
                continue
            # in future
            elif future is not None and future >= now:
                continue
            return value

        return Undefined

    def set(self, value, expires=None, future=None):
        # override on conflicts!
        self.assets.append((value, expires, future))


class Shelf(object):
    """A groovy dictonary on steroids.
    """
    __slots__ = ["getter", "checker", "changed", "priority",
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
        self.priority = priority
        self.signals = signals.Signals(self, "shelf-refresh", "asset-removed", "asset-added")

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

    # -------------
    # Gets
    # -------------
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
            value = self._dict[key]()
            if value is not Undefined:
                keys.append(key)
        return keys

    def values(self):
        """Will only return the current values
        """
        values = []
        for key in self._dict.keys():
            value = self._dict[key]()
            if value is not Undefined:
                values.append(value)
        return values

    def get(self, key, _else=Undefined, tz=None):
        """The method to get an assets value
        """
        self._refresh()
        if key in self._dict:
            # get the asset, call it
            value = self._dict[key]()
            # asset expired
            return value if value is not Undefined else _else
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

    # -------------
    # Sets
    # -------------
    def setall(self, _dict):
        """Quietly set the entire cache
        """
        if not isinstance(_dict, dict):
            raise TypeError("Expecting type dict, got type " + type(_dict))
        for key in _dict:
            self.set(key, _dict[key])
    
    def set(self, key, value, expires=None, future=None, check=True):
        """Set a value
        """
        if key is None:
            key = self._get_next_key()
        if self.has(key):
            # multi-valued asset management :)
            if (check and self._check_value(value)) or not check:
                self._dict[key].set(value, expires=expires, future=future)
                self.signals.emit("asset-added", key, value)
                return key
            return False
        else:
            if self._max_hit():
                raise MaxHit(key, value)
            if (check and self._check_value(value)) or not check:
                self._dict[key] = Book(value, expires=expires, future=future)
                self.signals.emit("asset-added", key, value)
                return key
            return False


    def append(self, value, expires=None, future=None, check=True):
        """Add a new value to the suite
        """
        return self.set(None, value, expires=expires, future=future, check=check)

    def setdefault(self, key, value, expires=None, future=None, check=True, tz=None):
        if self.has(key, tz=tz):
            return self.get(key, tz=tz)
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
    def has(self, key, tz=None):
        """Does the key exist?
        This method will check to see if it has expired too.
        """
        return self.get(key, tz=tz) is not Undefined

    def __contains__(self, key):
        """Time insensitive
        """
        return self.has(key)

    def __len__(self):
        """Time insensitive
        """
        length = 0
        for key in self._dict.keys():
            value = self._dict[key]()
            if value is not Undefined:
                length += 1
        return length

    def iter(self, tz=None):
        """Timezone sensative itering
        """
        for key in self._dict:
            value = self.get(key, Undefined, tz=tz)
            if value is not Undefined:
                yield key, value

    def __iter__(self):
        """Time insensitive
        """
        return self.iter()

    # -------------
    # Comparing
    # -------------
    def __lt__(self, other):
        if isinstance(other, Shelf):
            return self.priority < other.priority
        elif isinstance(other, int):
            return len(self) < other
        raise TypeError("Can not compare Shelf to %s" % type(other))

    def __gt__(self, other):
        if isinstance(other, Shelf):
           return self.priority > other.priority
        elif isinstance(other, int):
           return len(self) > other
        raise TypeError("Can not compare Shelf to %s" % type(other))

    def __eq__(self, other):
        if isinstance(other, Shelf):
            return self.priority == other.priority
        elif isinstance(other, int):
            return len(self) == other
        raise TypeError("Can not compare Shelf to %s" % type(other))

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

