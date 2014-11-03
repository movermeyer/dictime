[![codecov.io](https://codecov.io/github/stevepeak/dictime/coverage.svg?branch=master)](https://codecov.io/github/stevepeak/dictime?branch=master)
dictime [![Build Status](https://secure.travis-ci.org/stevepeak/dictime.png)](http://travis-ci.org/stevepeak/dictime) [![Version](https://pypip.in/v/dictime/badge.png)](https://github.com/stevepeak/dictime) [![Coverage Status](https://coveralls.io/repos/stevepeak/dictime/badge.png)](https://coveralls.io/r/stevepeak/dictime)
-------

> Time dimensional dictionaries, featuring expiring and future key values.
>  `dictime` extends the standard python `dict` with **3** distinct additions

#### Install
`pip install dictime`

## Extends `dict` with
1. keys that may have a **future** value, *but not exist now*
2. keys that can **expire** in the future
3. keys that have **multiple values**, *but only one value at any given time*

#### Policies
1. keys can only have **1** value at any moment
    - the extra values will be removed in the order they were added
2. calling methods like `":key" in dictime` or `dictime.has_key(":key")` will result in `True` **only** when the key **has a value that is `present`**. 
    - Therefore, if the key has no value now, but does so in the future it will return `False`

## Examples
```python
from dictime import dictime
from datetime import timedelta
from time import sleep

best = dictime()
best.set("who", "corey", expires=timedelta(seconds=10))
best.set("who", "casey", future=timedelta(seconds=10))

best.get("who") # "corey"

time.sleep(10)
best.get("who") # "casey"
```
> Notice in the example below how the key `who` will have **2** values but they are at different times

## Arguments
The method `.set()` accepts inline arguments in the following arrangement
```python 
_dictime.set(:key, :value, :expires default None, :future default None)
```
- **key**: any object
- **value**: any object
- **expres** accepts:
    - `None`: the value will never expire
    - `datetime.datetime`: the value will expire on `datetime`
    - `datetime.timedelta`: the value will expire on `now + timedelta`
    - `dict`: expire on `now + timedelta(**dict)`
- **future** accepts:
    - `None`: set this keys value **now**
    - `datetime.datetime`: the key will have this value on `datetime`
    - `datetime.timedelta`: the value will have this value on `now + timedelta`
    - `dict`: the key will have this value on `now + timedelta(**dict)`
