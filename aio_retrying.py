#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time        : 2023/12/29 22:30
# @Author      : Daoji
# @Email       : daoji.chang@gmail.com
# @File        : async_retrying.py
# @Description :
import asyncio
import inspect
import logging
from functools import wraps, partial
from typing import Callable, Coroutine, Type, Tuple, Optional, Any, Union

import async_timeout

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

propagate = forever = ...


class RetryError(Exception):
    pass


class ConditionError(Exception):
    pass


def is_exception(obj):
    return isinstance(obj, Exception) or (inspect.isclass(obj) and (issubclass(obj, Exception)))


def retry(
    fn: Callable = None,
    *,
    attempts: int = 3,
    callback: Optional[Callable] = None,
    fallback: Union[Callable, Type[BaseException], Any] = None,
    timeout: int = None,
    delay: int = 0,
    retry_exceptions: Tuple[Type[BaseException]] = (Exception,),
    fatal_exceptions: Tuple[Type[BaseException]] = (asyncio.CancelledError,),
):
    if fn is None:
        return partial(
            retry,
            attempts=attempts,
            callback=callback,
            fallback=fallback,
            timeout=timeout,
            delay=delay,
            retry_exceptions=retry_exceptions,
            fatal_exceptions=fatal_exceptions,
        )

    @wraps(fn)
    def wrapper(*args, **kwargs) -> Coroutine:
        async def wrapped(attempt: int = 0) -> Any:
            if not asyncio.iscoroutinefunction(fn):
                raise ConditionError(
                    "Only support coroutine function",
                )

            if timeout is not None and asyncio.TimeoutError not in retry_exceptions:
                _retry_exceptions = (asyncio.TimeoutError,) + retry_exceptions
            else:
                _retry_exceptions = retry_exceptions

            try:
                if timeout is None:
                    ret = await fn(*args, **kwargs)
                else:
                    with async_timeout.timeout(timeout):
                        ret = await fn(*args, **kwargs)
                return ret

            except ConditionError:
                raise
            except fatal_exceptions:
                raise
            except _retry_exceptions as exc:
                _attempts = "infinity" if attempts is forever else attempts
                context = {
                    "fn": fn,
                    "attempt": attempt,
                    "attempts": _attempts,
                }
                logger.debug(
                    exc.__class__.__name__ + " -> Tried attempt #%(attempt)d from total %(attempts)s for %(fn)r",
                    # noqa
                    context,
                    exc_info=exc,
                )
                if attempt < attempts:
                    await asyncio.sleep(delay)
                    return await wrapped(attempt=attempt + 1)

                ret = None
                if fallback is not None:
                    if fallback is propagate:
                        raise exc

                    if is_exception(fallback):
                        raise fallback from exc

                    if callable(fallback):
                        if asyncio.iscoroutinefunction(fallback):  # noqa
                            ret = await fallback(*args, **kwargs)
                        else:
                            ret = fallback(*args, **kwargs)
                    else:
                        ret = fallback

                if callback is not None:
                    if not callable(callback):
                        raise ConditionError(
                            "Callback must be callable",
                        )
                    if asyncio.iscoroutinefunction(callback):
                        await callback(attempt, exc, args, kwargs)
                    else:
                        callback(attempt, exc, args, kwargs)

                return ret

        return wrapped()

    return wrapper
