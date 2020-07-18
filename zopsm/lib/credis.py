from credis import Connection
import inspect


class DataError(Exception):
    pass


def dict_merge(*dicts):
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged


def string_keys_to_dict(key_string, callback):
    return dict.fromkeys(key_string.split(), callback)


def pairs_to_dict(response):
    """
    Create a dict given a list of key/value pairs
    Args:
        response (list): list of key value pairs

    Returns:
        dict: response dict
    """
    it = iter(response)
    return dict(zip(it, it))


def list_or_args(keys, args):
    # returns a single list combining keys and args
    try:
        iter(keys)
        # a string or bytes instance can be iterated, but indicates
        # keys wasn't passed as a list
        if isinstance(keys, (str, bytes)):
            keys = [keys]
    except TypeError:
        keys = [keys]
    if args:
        keys.extend(args)
    return keys


def nativestr(x):
    return x if isinstance(x, str) else x.decode('utf-8', 'replace')


def bool_ok(response):
    return nativestr(response) == 'OK'


def parse_scan(response, **options):
    cursor, r = response
    return int(cursor), r


class ZRedis(Connection):
    """
    Custom wrapper for credis
    """
    RESPONSE_CALLBACKS = dict_merge(
        string_keys_to_dict(
            'exists expire hexists hset hmset sismember setnx renamenx persist',
            bool
        ),
        string_keys_to_dict(
            'sadd srem del sinterstore sunionstore hdel ttl',
            int
        ),
        string_keys_to_dict(
            'sdiff sinter smembers sunion',
            lambda r: r and set(r) or set()
        ),
        string_keys_to_dict(
            'hget hmget spop get', lambda r: r or None
        ),
        string_keys_to_dict(
            'rename', bool_ok
        ),
        {
            'hgetall': lambda r: r and pairs_to_dict(r) or {},
            'set': lambda r: r and bool_ok(r),
            'scan': parse_scan,
        }

    )

    def __init__(self, host, password=None, db=0, *args, **kwargs):
        super(ZRedis, self).__init__(host=host, password=password, db=db)
        self.response_callbacks = self.__class__.RESPONSE_CALLBACKS.copy()

    def who_am_i(self):
        return inspect.stack()[1][3]

    # Key Commands
    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        """
        Set the value at key ``name`` to ``value``

        Args:
            name (str):

            value (str):

            ex (int): ``ex`` sets an expire flag on key ``name`` for ``ex`` seconds

            px (int): ``px`` sets an expire flag on key ``name`` for ``px`` milliseconds.

            nx (bool): ``nx`` if set to True, set the value at key ``name`` to ``value`` only
            if it does not exist.

            xx (bool): ``xx`` if set to True, set the value at key ``name`` to ``value`` only
            if it already exists.

        Returns:
            bool
        """
        pieces = [name, value]
        if ex is not None:
            pieces.append('ex')
            pieces.append(ex)

        if px is not None:
            pieces.append('px')
            pieces.append(px)

        if nx:
            pieces.append('nx')
        if xx:
            pieces.append('xx')

        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), *pieces))

    def setnx(self, name, value):
        """
        Set the value of key ``name`` to ``value`` if key doesn't exist

        Args:
            name (str):
            value (str):

        Returns:
            bool
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, value))

    def rename(self, src, dst):
        """
        Rename key ``src`` to ``dst``

        Args:
            src (str):
            dst (str):

        Returns:
            bool
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), src, dst))

    def renamenx(self, src, dst):
        """
        Rename key ``src`` to ``dst`` if ``dst`` doesn't already exist

        Args:
            src (str):
            dst (str):

        Returns:
            bool
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), src, dst))

    def get(self, name):
        """
        Return the value at key ``name``, or None if the key doesn't exist

        Args:
            name (str):

        Returns:

        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name))

    def expire(self, name, time):
        """
        Set an expire flag on key ``name`` for ``time`` seconds. ``time``
        must be represented by an integer.

        Args:
            name (str):
            time (int): seconds

        Returns:
            bool
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, time))

    def exists(self, name):
        """
        "Returns a boolean indicating whether key ``name`` exists"
        Args:
            name (str):

        Returns:
            bool
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name))
    __contains__ = exists

    def delete(self, *names):
        """
        Delete one or more keys specified by ``names``
        Args:
            *names:

        Returns:
            int: The number of keys that were removed.
        """
        return self.response_callbacks['del'](self.execute('del', *names))

    def persist(self, name):
        """
        Removes an expiration on ``name``

        Args:
            name (str):

        Returns:
            bool
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name))

    # Hash Commands
    def hgetall(self, name):
        """
        Return a Python dict of the hash's name/value pairs.
        Args:
            name (str): name(redis key) of hash

        Returns:
            dict: dict of name/value pairs
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name))

    def hexists(self, name, key):
        """
        Returns a boolean indicating if ``key`` exists within hash ``name``
        Args:
            name (str): name(redis key) of hash
            key (str): key in the hash

        Returns:
            bool: indicating if ``key`` exists
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, key))

    def hget(self, name, key):
        """
        Return the value of ``key`` within the hash ``name``"
        Args:
            name (str): name(redis key) of hash
            key (str): key in the hash

        Returns:
            bytes: value of key
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, key))

    def hset(self, name, key, value):
        """
        Set ``key`` to ``value`` within hash ``name``
        Returns ``True`` if HSET created a new field, otherwise ``False`

        Args:
            name (str): name(redis key) of hash
            key (str): key in the hash
            value (str): value of key

        Returns:
            bool:
        """
        return self.response_callbacks[self.who_am_i()](
            self.execute(self.who_am_i(), name, key, value))

    def hmset(self, name, mapping):
        """
        Set key to value within hash ``name`` for each corresponding
        key and value from the ``mapping`` dict.
        Args:
            name (str):
            mapping (dict):

        Returns:
            bool
        """
        if not mapping:
            raise DataError("'hmset' with 'mapping' of length 0")
        items = []
        for pair in iter(mapping.items()):
            items.extend(pair)
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, *items))

    def hmget(self, name, keys, *args):
        """
        Returns a list of values ordered identically to ``keys``
        Args:
            name (str):
            keys (list): list of str
            *args:

        Returns:
            list:
        """
        args = list_or_args(keys, args)
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, *args))

    def hincrby(self, name, key, amount=1):
        """
        Increment the value of ``key`` in hash ``name`` by ``amount``

        Args:
            name (str):
            key (str):
            amount (int):

        Returns:
            int: the value
        """
        return self.execute(self.who_am_i(), name, key, amount)

    def hdel(self, name, *keys):
        """
        Delete ``keys`` from hash ``name``
        Args:
            name:
            *keys:

        Returns:

        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, *keys))

    # Set Commands
    def sadd(self, name, *values):
        """
        Add ``value(s)`` to set ``name`` and returns the cardinality of the set
        Args:
            name (str):
            *values:

        Returns:
            int: Cardinality of the set ``name``
        """
        if not values:
            raise ValueError("SADD does not accept empty list as argument!")
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, *values))

    def sismember(self, name, value):
        """
        Return a boolean indicating if ``value`` is a member of set ``name``

        Args:
            name (str):
            value (str):

        Returns:
            bool:
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, value))

    def smembers(self, name):
        """
        Return all members of the set ``name``

        Args:
            name (str):

        Returns:
            set:
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name))

    def spop(self, name):
        """
        Remove and return a random member of set ``name``

        Args:
            name (str):

        Returns:
            bytes:
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name))

    def srem(self, name, *values):
        """
        Remove ``values`` from set ``name``

        Args:
            name:
            *values:

        Returns:
            int: the number of members that were removed from the set

        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name, *values))

    def sinterstore(self, dest, keys, *args):
        """
        Store the intersection of sets specified by ``keys`` into a new
        set named ``dest``.  Returns the number of keys in the new set.

        :param dest:
        :param keys:
        :param args:
        :return:
        """
        args = list_or_args(keys, args)
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), dest, *args))

    def sunion(self, keys, *args):
        """
        Return the union of sets specified by ``keys``
        Args:
            keys:
            *args:

        Returns:

        """
        args = list_or_args(keys, args)
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), *args))

    def sunionstore(self, dest, keys, *args):
        """
        Store the union of sets specified by ``keys`` into a new
        set named ``dest``.  Returns the number of keys in the new set.

        Args:
            dest:
            keys:
            *args:

        Returns:

        """
        args = list_or_args(keys, args)
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), dest, *args))

    def sdiffstore(self, dest, keys, *args):
        """
        Store the difference of sets specified by ``keys`` into a new
        set named ``dest``.  Returns the number of keys in the new set.

        Args:
            dest:
            keys:
            *args:

        Returns:

        """
        args = list_or_args(keys, args)
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), dest, *args))

    # Scan Commands
    def scan(self, cursor=0, match=None, count=None):
        """
        Incrementally return lists of key names. Also return a cursor indicating the scan position.

        Args:
            cursor:
            match: ``match`` allows for filtering the keys by pattern
            count: ``count`` allows for hint the minimum number of returns

        Returns:
            tuple: cursor(int), list of key names
        """
        pieces = [cursor]
        if match is not None:
            pieces.extend(['match', match])
        if count is not None:
            pieces.extend(['count', count])
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), *pieces))

    def ttl(self, name):
        """
        Returns the remaining time to live of a key that has a timeout.

        Args:
            name (str):

        Returns:
            int
        """
        return self.response_callbacks[self.who_am_i()](self.execute(self.who_am_i(), name))
