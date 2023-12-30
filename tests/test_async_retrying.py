import asyncio

from aio_retrying import retry


async def test_smoke():
    counter = 0

    @retry(retry_exceptions=(RuntimeError,), attempts=2)
    async def fn():
        nonlocal counter
        counter += 1

        if counter == 1:
            raise RuntimeError

        return counter

    ret = await fn()
    print(f"{ret=} | {counter=}")
    assert ret == counter


async def test_callback_delay(mocker):
    mocker.patch("asyncio.sleep")
    counter = 0

    @retry(delay=5, retry_exceptions=(RuntimeError,), attempts=2)
    async def fn():
        nonlocal counter

        counter += 1

        if counter <= 2:
            raise RuntimeError

        return counter

    ret = await fn()

    assert ret == counter

    expected = [
        ((5,),),
        ((5,),),
    ]

    assert asyncio.sleep.call_args_list == expected
