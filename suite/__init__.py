version = '0.0.2'
__version__ = version

class KeyGenerator:
    def __init__(self, start=-1):
        self.i = start
        
    def next(self):
        self.i += 1
        return self.i


class Collection(object):
    def __init__(self, *suites):
        self._orderby = 'priority'
        self._suites = sorted(suites,
                              key=lambda s: getattr(s, self.orderby))

    def push(self, suite):
        assert isinstance(suite, Suite)
        self._suites.append(suite)
        self._suites = sorted(self._suites,
                              key=lambda s: getattr(s, self.orderby))

    def append(self, value):
        for suite in self._suites:
            if suite.append(value):
                return True
        return False

    @property
    def orderby(self):
        return self._orderby

    @orderby.setter
    def orderby(self, attr):
        self._orderby = attr

    def __len__(self):
        return len(self._suites)
    
    def __iter__(self):
        return self._suites



class Suite( object ):
    def __init__(self, getter=None, setter=None, changed=None, yielder=None, max=None, priority=0, keygen_start=0):
        self._getter = getter
        self._setter = setter
        self._changed = changed
        self._yielder = yielder
        self._dict = {}
        self._key_gen = KeyGenerator(keygen_start)
        self._max = max
        self._priority = priority
    
    # -------------
    # Gets
    # -------------
    def _get_next_key(self):
        key = self._key_gen.next()
        if not self._dict.has_key(key):
            return key
        while self._dict.has_key(key):
            key = self._key_gen.next()
        return key

    def get_all(self):
        return self._dict

    def __getitem__(self, key):
        if self._dict.has_key(key):
            return self._dict.get(key)
        else:
            if self._getter is not None:
                return self._getter(key)
            else:
                raise KeyError(key)

    def iteritems(self):
        return self._dict

    def keys(self):
        return self._dict.keys()

    def has_key(self, key):
        return self._dict.has_key(key)
    
    def values(self):
        return self._dict.values()

    def get(self, key, _else=None):
        self._dict.get(key, _else if _else is not None else self._getter(key) if self._getter else None)

    # -------------
    # Sets
    # -------------
    def put_all(self, _dict):
        """Quietly set the entire cache
        """
        if not isinstance(_dict, dict):
            raise TypeError("Expecting type dict, got type " + type(_dict))
        self._dict = _dict
    
    def put(self, key, value):
        """Quietly set this key=>value
        No validation will occur
        """
        if self._max_hit():
            return False
        self._dict[key or self._get_next_key()] = value
        return True

    def append(self, value):
        """Used as a list option
        """
        if self._max_hit():
            return False
        key = self._get_next_key()
        if self._on_append(key, value):
            self._dict[key] = value
            self._on_changed()
            return key
        else:
            return False

    def setdefault(self, key, value):
        if self._dict.has_key(key):
            return self._dict[key]
        else:
            return self.put(key, value)


    # -------------
    # Deletes
    # -------------
    def remove(self, child):
        """Removes a child from the Suite.
        """
        key = None
        for i, c in self._dict.iteritems():
            if c == child:
                key = i
                break
        if key is not None:
            del self._dict[key]
            return True
    
    def delete(self, key):      
        """Quietly delete a key
        """
        del self._dict[key]

    def __delitem__(self, key):
        del self._dict[key]

    def clear(self):
        self._dict = {}

    # -------------
    # Basics
    # -------------
    def __len__(self):
        return len(self._dict)
    
    def __iter__(self):
        return self._yielder() if self._yielder else iter(self._dict.values())

    def __lt__(self, other):
        if isinstance(other, Suite):
            return len(self) < len(other)
        else:
            return len(self) < other

    def __gt__(self, other):
        if isinstance(other, Suite):
            return len(self) > len(other)
        else:
            return len(self) > other

    def __eq__(self, other):
        if isinstance(other, Suite):
            return len(self) == len(other)
        else:
            return len(self) == other

    # -------------
    # Properties
    # -------------
    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, max):
        self._max = max

    @property
    def changed(self, callback):
        self._changed = callback

    @property
    def getter(self, callback):
        self._getter = callback

    @property
    def setter(self, callback):
        self._setter = callback

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, priority):
        self._priority = priority

    # -------------
    # Callbacks
    # -------------
    def _on_changed(self):
        if self._changed is not None:
            self._changed(self)

    def _on_append(self, key, value):
        assert self._setter is not False, "Not allowed to add to this Suite"
        if self._setter is None:
            return True
        else:
            return self._setter(key, value) is not False

    def _max_hit(self):
        return self.max is not None and len(self._dict) >= self.max

