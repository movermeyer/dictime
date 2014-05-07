from threading import RLock
from datetime import datetime
from datetime import timedelta

from .moment import moment


class dictime(object):
    __slots__ = ["_expires", "_lock", "_callback", "_last_expired", "_dict"]

    def __init__(self, **kwargs):
        self._expires = None
        self._last_expired = None
        self._callback = None
        self._dict = {}
        self._lock = RLock()
        if kwargs:
            self.update(kwargs)

    def expired(self):
        if self._expires and self._last_expired:
            now = datetime.now()
            if (self._last_expired + self._expires) <= now:
                self._last_expired = now
                self._dict = {}
                if self._callback:
                    self._callback(self)

    def set_expires(self, expires, callback=None):
        assert expires is None or isinstance(expires, timedelta), "expires is not a valid type"
        assert hasattr(callback, "__call__") or callback is None, "callback must be callable"
        self._expires = expires
        self._last_expired = datetime.now()
        self._callback = callback

    # ----
    # Gets
    # ----
    def __getitem__(self, key):
        value = self.get(key, NotImplemented)
        if type(value) is type(NotImplemented):
            raise KeyError("key %s not found in dictime" % key)
        return value

    def get(self, key, _else=None):
        """The method to get an assets value
        """
        with self._lock:
            self.expired()
            # see if everything expired
            try:
                value = self._dict[key].get()
                return value
            except KeyError:
                return _else
            except ValueError:
                return _else

    # ----
    # Sets
    # ----
    def __setitem__(self, key, value):
        self.set(key, value)
    
    def set(self, key, value, expires=None, future=None):
        """Set a value
        """
        # assert the values above
        with self._lock:
            try:
                self._dict[key].set(value, expires=expires, future=future)
            except KeyError:
                self._dict[key] = moment(value, expires=expires, future=future, lock=self._lock)
            return value

    def setdefault(self, key, value, expires=None, future=None):
        if self.has_key(key):
            return self.get(key)
        else:
            return self.set(key, value, expires=expires, future=future)

    def update(self, _dict):
        for key, value in _dict.iteritems():
            self.set(key, value)

    # -------
    # Deletes
    # -------
    def remove(self, key):
        del self._dict[key]
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
    def keys(self):
        """Return list of keys that have values
        """
        self.expired()
        return self._dict.keys()

    def values(self):
        """Will only return the current values
        """
        self.expired()
        values = []
        for key in self._dict.keys():
            try:
                value = self._dict[key].get()
                values.append(value)
            except:
                continue
        return values

    def has_key(self, key):
        """Does the key exist?
        This method will check to see if it has expired too.
        """
        if key in self._dict:
            try: 
                self[key]
                return True
            except ValueError:
                return False
            except KeyError:
                return False
        return False

    def __contains__(self, key):
        """Time insensitive
        """
        return self.has_key(key)

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        for key in self._dict:
            try:
                yield key, self.get(key)
            except ValueError:
                continue

    def __nonzero__(self):
        return (len(self) > 0)
