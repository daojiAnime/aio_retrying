aio_retrying
==============

:info: Simple retrying for asyncio

.. image:: https://img.shields.io/pypi/v/aio_retrying.svg
    :target: https://pypi.python.org/pypi/aio_retrying

Installation
------------

.. code-block:: shell

    pip install aio_retrying

Usage
-----

.. code-block:: python

    import asyncio

    import aiohttp

    from Utils.async_retrying import retry


    class Aio:
        def __init__(self):
            self.session = aiohttp.ClientSession()

        async def __aenter__(self):
            return self

        @retry(attempts=3, delay=1, fallback="daoji")
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.session.close()
            print("exit")

        async def main(self):
            for i in range(3):
                assert self.session.closed is False
                await asyncio.sleep(1)
                print(f"task - {i}")


    async def second_aio():
        aio = Aio()
        # task = asyncio.create_task(aio.main())
        # task.add_done_callback(lambda _: asyncio.create_task(aio.__aexit__(None, None, None)))
        ret = await aio.__aexit__(None, None, None)
        print(f"结果：{ret}")


    async def first_aio():
        await second_aio()
        while True:
            # print("first")
            await asyncio.sleep(3)


    def main():
        asyncio.run(first_aio())


    if __name__ == "__main__":
        main()


Python 3.8+ is required
