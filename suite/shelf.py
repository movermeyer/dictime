from datetime import datetime

from suite.helpers import MaxHit
from suite.helpers import KeyGenerator

class Book(object):
    def __init__(self, value, expires=None, future=None):
        self.value = value
        self.expires = expires
        self.future = future
        self._iter_keys = None

    def __call__(self):
        """Called to get the asset values and if it is valid
        
        valid: True =>  Is valid
               False => Has expired, destory it
               None =>  Future, do nothing
        """
        if self.expires and self.expires <= datetime.now():
            return self.value, False
        elif self.future:
            if self.future <= datetime.now():
                # has recently become valid
                self.future = None
            else:
                # not valid, will be in the future
                return self.value, None
        return self.value, True

class Shelf(object):
    """A groovy dictonary on steroids.
    """
    def __init__(self, getter=None, check=None, changed=None, yielder=None, max=None, priority=0):
        # set custom functions
        self.getter = getter
        self.checker = check
        self.changed = changed
        self.yielder = yielder
        self.max = max
        self.priority = priority

        self._dict = {}
        self._key_gen = KeyGenerator()
        # default method for sorting
    
    def _manage_asset(self, key):
        """Pass an asset in 
        this method will deduce its validity
        """
        try:
            asset = self._dict[key]
        except KeyError:
            return None, False
        value, valid = asset()
        # asset expired
        if valid is False:
            # delete the asset
            del self._dict[key]
            self._on_changed()
            return None, False
        elif valid is None:
            return value, False
        return value, True

    def _get_next_key(self):
        """Serial integar generator
        """
        key = self._key_gen.next()
        if key not in self._dict:
            return key
        while key in self._dict:
            key = self._key_gen.next()
        return key

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
            value, valid = self._manage_asset(key)
            if valid:
                keys.append(key)
        return keys

    def values(self):
        """Will only return the current values
        """
        values = []
        for key in self._dict.keys():
            value, valid = self._manage_asset(key)
            if valid:
                values.append(value)
        return values

    def get(self, key, _else=None):
        """The method to get an assets value
        """
        if key in self._dict:
            # get the asset, call it
            value, valid = self._manage_asset(key)
            # asset expired
            return value if valid else _else
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
        if self._max_hit():
            raise MaxHit(key, value)
        if (check and self._check_value(value)) or not check:
            if key is None:
                key = self._get_next_key()
            self._dict[key] = Book(value, expires=expires, future=future)
            self._on_changed()
            return key

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
        self._on_changed()

    def __delitem__(self, key):
        self.remove(key)

    def clear(self):
        """Delete all keys
        """
        self._dict = {}
        self._on_changed()

    # -------------
    # Basics
    # -------------
    def has(self, key):
        """Does the key exist?
        This method will check to see if it has expired too.
        """
        if key in self._dict:
            self.get(key)
            return key in self._dict
        return False

    def __contains__(self, key):
        return self.has(key)

    def __len__(self):
        length = 0
        for key in self._dict.keys():
            value, valid = self._manage_asset(key)
            if valid:
                length += 1
        return length
    
    def __iter__(self):
        if self.yielder:
            return self.yielder()
        else:
            self._iter_keys = self.keys()
            return self

    def next(self):
        if len(self._iter_keys) == 0:
            raise StopIteration
        key = self._iter_keys.pop()
        return key, self.get(key)

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
    def _on_changed(self):
        if self.changed is not None:
            self.changed(self)

    def _check_value(self, value):
        assert self.checker is not False, "Not allowed to add to this Shelf"
        if self.checker is None:
            return True
        else:
            return self.checker(self, value) is not False

    def _max_hit(self):
        return self.max is not None and len(self) >= self.max

