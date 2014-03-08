class MaxHit(Exception):
    def __init__(self, key, value):
        self.msg = "Max number of assets in suite hit. Could not add another."
        self.key = key
        self.value = value

class KeyGenerator:
    def __init__(self, start=0):
        self.i = start
        
    def next(self):
        self.i += 1
        return self.i

class Undefined:
    pass
