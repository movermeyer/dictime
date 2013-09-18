version = '0.1.0'
__version__ = version

class KeyGenerator:
    def __init__(self, start=0):
        self.i = start
        
    def next(self):
        self.i += 1
        return self.i


class Collection(object):
    def __init__(self, *suites, **kwargs):
        self._suites = []
        self._fitter = kwargs.get('fitter', None)
        self._key_gen = KeyGenerator()
        if suites:
            for suite in self._suites:
                suite._key_gen = self._key_gen
            self._suites = sorted(suites)
            

    def push(self, suite):
        assert isinstance(suite, Suite)
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
            if suite.has_get(key):
                return suite.get(key)


class Suite( object ):
    def __init__(self, getter=None, check=None, changed=None, yielder=None, max=None, priority=0):
        self._getter = getter
        self._checker = check
        self._changed = changed
        self._yielder = yielder
        self._dict = {}
        self._key_gen = KeyGenerator()
        self._max = max
        # default method for sorting
        self._priority = priority
    
    # -------------
    # Gets
    # -------------
    def _get_next_key(self):
        key = self._key_gen.next()
        if key not in self._dict:
            return key
        while key in self._dict:
            key = self._key_gen.next()
        return key

    def __getitem__(self, key):
        if key in self._dict:
            return self._dict.get(key)
        else:
            if self._getter is not None:
                return self._getter(key)
            else:
                raise KeyError(key)

    def keys(self):
        return self._dict.keys()

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
        if self._check_value(value):
            self._dict[key] = value
            self._on_changed()
            return key
        else:
            return False

    def setdefault(self, key, value):
        if key in self._dict:
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
        return self.priority < other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def __eq__(self, other):
        return self.priority == other.priority

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
        self._checker = callback

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

    def _check_value(self, value):
        assert self._checker is not False, "Not allowed to add to this Suite"
        if self._checker is None:
            return True
        else:
            return self._checker(self, value) is not False

    def _max_hit(self):
        return self.max is not None and len(self._dict) >= self.max

