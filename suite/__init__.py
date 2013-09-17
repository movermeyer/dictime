
class KeyGenerator:
    def __init__(self, start=-1):
        self.i = start
        
    def next(self):
        self.i += 1
        return self.i
    
    
class Suite( object ):
    def __init__(self, getter=None, setter=None, yielder=None, keygen_start=-1):
        self._getter = getter
        self._setter = setter
        self._yielder = yielder
        self._dict = {}
        self._key_gen = KeyGenerator(keygen_start)
    
    # -------------
    # Gets
    # -------------
    def _get_next_key(self):
        """Gets a unique key that is not a member of this Suite
        """
        key = self._key_gen.next()
        if not self._dict.has_key(key):
            return key
        while self._dict.has_key(key):
            key = self._key_gen.next()
        return key

    def get_all(self):
        """Returns all the records as a dict
        """
        return self._dict

    def iteritems(self):
        return self._dict

    def keys(self):
        return self._dict.keys()

    def has_key(self, key):
    	return self._dict.has_key(key)
    
    def values(self):
        return self._dict.values()

    def get(self, key, _else=None):
        """Get the item only if its in cache
        """
        self._dict.get(key, _else if _else is not None else self._getter(key) if self._getter else None)

    def put_all(self, _dict):
        """Quietly set the entire cache
        """
        if not isinstance(_dict, dict):
        	raise TypeError("Expecting type dict, got type " + type(_dict))
        self._dict = _dict
    
    def put(self, key, value):
        """Quietly set this key=>value
        """
        self._dict[key or self._get_next_key()] = value
        return True

	# -------------
	# Sets
	# -------------
    def append(self, child):
        """Used as a list option
        """
        key = self._get_next_key()
        if self._check_append(key, child):
            self[key] = child
            return key

    def __lt__(self, child):
    	"""Alias for append
    	Ex. Suite() < new_child_object === Suite.append(child)
    	"""
        return self.append(child)

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
        
    def _check_append(self, key, value):
        if self._setter is False:
            raise AttributeError("Woops! Not allowed to set this Suites data.")
        elif self._setter is None:
            return True
        else:
            return self._setter(value, value)

	# -------------
	# Basics
	# -------------
    def __len__(self):
        return len(self._dict)
    
    def __iter__(self):
        """Loudly get all the possible records for this Suite
        """
        return self._yielder() if self._yielder else iter(self._dict.values())
    
    def __getitem__(self, key):
        """Used when accessing as dict: `Suite[...]`
        """
        if self._dict.has_key(key):
            return self._dict.get(key)
        else:
            if self._getter is not None:
                return self._getter(key)
            else:
                raise KeyError(key)

    def __setitem__(self, key, value):
        """Used when accessing as dict: `Suite[...] = x`
        """
        if self._check_append(key, value):
            self._dict[key] = value
            return True
        return False
