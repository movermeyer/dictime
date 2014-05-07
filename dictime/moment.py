from threading import RLock
from datetime import datetime


class moment(object):
    __slots__ = ['futures', '_lock']
    def __init__(self, value=None, expires=None, future=None, lock=None):
        self.futures = []
        # thread safety
        self._lock = lock or RLock()
        self.set(value, expires, future)

    def get(self):
        """Called to get the asset values and if it is valid
        """
        with self._lock:
            now = datetime.now()
            active = []
            for i, vef in enumerate(self.futures):
                # has expired
                if (vef[1] or datetime.max) <= now:
                    self.futures.pop(i)
                    continue
                # in future
                elif (vef[2] or datetime.min) >= now:
                    continue
                else:
                    active.append(i)

            if active:
                # this will evict values old values
                # because new ones are "more recent" via future
                value, _e, _f = self.futures[active[-1]]
                for i in active[:-1]:
                    self.futures.pop(i)
                return value

            raise ValueError("dicttime: no current value, however future has (%d) values" % len(self.futures))

    def set(self, value, expires=None, future=None):
        now = datetime.now()
        assert isinstance(expires, (type(None), datetime)) and (expires is None or expires > now), "expired: invalid or already expired"
        assert isinstance(future, (type(None), datetime)) and (future is None or future > now), "future: invalid or not in future"
        if expires and future:
            assert future < expires, "expires before existing"

        self.futures.append((value, expires, future))

    def __len__(self):
        return len(self.futures)
