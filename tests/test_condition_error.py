import asyncio

import pytest

from aio_retrying import ConditionError, retry


async def test_timeout_is_not_none_and_not_async():
    @retry(timeout=0.5)
    def not_coro():
        pass

    with pytest.raises(ConditionError):
        await not_coro()
