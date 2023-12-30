import pytest

from aio_retrying import retry, RetryError, forever


async def test_immutable_with_kwargs():
    @retry(attempts=forever, fatal_exceptions=(KeyError,))
    async def coro(a):
        a.pop("a")
        raise RuntimeError

    with pytest.raises(KeyError):
        await coro({"a": "a"})
