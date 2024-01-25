#!/usr/bin/env python3
"""
Redis
"""
from functools import wraps
from typing import Union, Optional, Callable
from uuid import uuid4

import redis

UnionOfTypes = Union[str, bytes, int, float]


def count_calls(method: Callable) -> Callable:
    """
    count how many times Cache class are called
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper for counting calls
        """
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    decorator to store the history of inputs
    and outputs for a particular function
    """
    key = method.__qualname__
    input_key = f"{key}:inputs"
    output_key = f"{key}:outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapper for storing input and output history """
        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))
        return result

    return wrapper


class Cache:
    """
    redis class
    """

    def __init__(self):
        """
        redis model
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: UnionOfTypes) -> str:
        """
        Generate a random key (e.g., using uuid)
        """
        key = str(uuid4())
        self._redis.mset({key: data})
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> UnionOfTypes:
        """
        Convert the data
        """
        if fn:
            return fn(self._redis.get(key))
        data = self._redis.get(key)
        return data

    @staticmethod
    def get_int(data: bytes) -> int:
        """Get a number int"""
        return int.from_bytes(data, "big")

    @staticmethod
    def get_str(data: bytes) -> str:
        """Get a string"""
        return data.decode("utf-8")
