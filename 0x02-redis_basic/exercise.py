#!/usr/bin/env python3
"""
Main file
"""
import redis
import uuid
import functools


class Cache:
    """Cache class for working with Redis"""

    def __init__(self):
        """Initialize the Cache instance with a Redis client"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: str) -> str:
        """Store data in Redis and return the generated key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn=None):
        """Retrieve data from Redis and optionally apply conversion function"""
        data = self._redis.get(key)
        return fn(data) if fn else data

    def get_str(self, key: str):
        """Retrieve data from Redis and decode as UTF-8"""
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str):
        """Retrieve data from Redis and convert to integer"""
        return self.get(key, fn=int)

    @functools.wraps(redis.Redis.incr)
    def count_calls(method):
        """Decorator to count the number of times a method is called"""
        def wrapper(self, *args, **kwargs):
            key = method.__qualname__
            self._redis.incr(key)
            return method(self, *args, **kwargs)
        return wrapper

    @count_calls
    def store(self, data: str) -> str:
        """Store data in Redis and return the generated key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def call_history(method):
        """Decorator to store the history of inputs
        and outputs for a function"""
        def wrapper(self, *args, **kwargs):
            input_key = f"{method.__qualname__}:inputs"
            output_key = f"{method.__qualname__}:outputs"

            # Store input arguments
            self._redis.rpush(input_key, str(args))

            # Execute the original function and store its output
            output = method(self, *args, **kwargs)
            self._redis.rpush(output_key, str(output))

            return output
        return wrapper

    @call_history
    def store(self, data: str) -> str:
        """Store data in Redis and return the generated key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key


def replay(method):
    """Display the history of calls of a particular function"""
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    inputs = cache._redis.lrange(input_key, 0, -1)
    outputs = cache._redis.lrange(output_key, 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")
    for inp, outp in zip(inputs, outputs):
        input_str = inp.decode('utf-8')
        output_str = outp.decode('utf-8')
        print(f"{method.__qualname__}(*{input_str}) -> {output_str}")
