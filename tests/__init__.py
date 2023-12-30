import logging
import os

import structlog

os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["PYTHONASYNCIODEBUG"] = "1"

logging.basicConfig(level=logging.DEBUG)
test_logger = structlog.stdlib.get_logger("aio_retrying_test")
