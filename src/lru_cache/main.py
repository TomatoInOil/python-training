import unittest.mock
from collections import OrderedDict


def lru_cache(maxsize=3):
    cached_results = OrderedDict()

    def lru_cache_wrapper(func, maxsize):
        def wrapper(*args, **kwargs):
            nonlocal cached_results
            kwargs_tuple = tuple(kwargs.items())
            cache_key = (args, kwargs_tuple)
            result = cached_results.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            if len(cached_results) >= maxsize:
                cached_results.popitem(last=False)
            cached_results[cache_key] = result
            return result

        return wrapper

    if callable(maxsize):
        user_func = maxsize
        maxsize = 3
        return lru_cache_wrapper(user_func, maxsize)

    def dec(func):
        return lru_cache_wrapper(func, maxsize)

    return dec


@lru_cache
def sum_two_number(a: int, b: int) -> int:
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == "__main__":
    assert sum_two_number(1, 2) == 3
    assert sum_two_number(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4
