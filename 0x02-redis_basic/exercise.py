#!/usr/bin/env python3
"""
Redis and Python exercise
"""


import uuid
from functools import wraps
from typing import Callable, Union

import redis


class Cache:
    """Cache class with Redis"""

    def __init__(self) -> None:
        """Initialize the Cache instance with a Redis client"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @staticmethod
    def generate_key() -> str:
        """Generate a random key using UUID"""
        return str(uuid.uuid4())

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis and return the generated key"""
        key = self.generate_key()
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable = None) -> Union[
      str, bytes, int, float]:
        """Retrieve data from Redis and optionally apply conversion function"""
        data = self._redis.get(key)
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """Retrieve data from Redis and decode as UTF-8"""
        return self.get(key, str)

    def get_int(self, key: str) -> int:
        """Retrieve data from Redis and convert to integer"""
        return self.get(key, int)


def count_calls(method: Callable) -> Callable:
    """Decorator to count the number of times a method is called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Increment the count for that key every time the method is called"""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs for a function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Save the input and output of each function in Redis"""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        output = method(self, *args, **kwargs)

        self._redis.rpush(input_key, str(args))
        self._redis.rpush(output_key, str(output))

        return output

    return wrapper


def replay(fn: Callable) -> None:
    """Display the history of calls of a particular function"""
    r = redis.Redis()
    f_name = fn.__qualname__
    n_calls = int(r.get(f_name) or 0)
    print(f'{f_name} was called {n_calls} times:')

    ins = r.lrange(f_name + ":inputs", 0, -1)
    outs = r.lrange(f_name + ":outputs", 0, -1)

    for i, o in zip(ins, outs):
        i_str = i.decode('utf-8') if isinstance(i, bytes) else ""
        o_str = o.decode('utf-8') if isinstance(o, bytes) else ""
        print(f'{f_name}(*{i_str}) -> {o_str}')
