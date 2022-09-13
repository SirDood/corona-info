import logging
import os
import sys
from datetime import datetime

from coronainfo.enums import Date, Paths

FILE_NAME = str(Paths.STATE_DIR / f"coronainfo_log_{datetime.now().strftime(Date.FILE_FORMAT)}.log")
FORMAT = "[%(levelname)s] %(asctime)s: %(message)s"
DATE_FORMAT = Date.RAW_FORMAT
LEVEL = logging.DEBUG if os.environ.get("CORONAINFO_DEBUG") else logging.INFO

FORMATTER = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)

FILE_HANDLER = logging.FileHandler(filename=FILE_NAME, mode="w", encoding="utf-8")
FILE_HANDLER.setLevel(LEVEL)
FILE_HANDLER.setFormatter(FORMATTER)

STREAM_HANDLER = logging.StreamHandler(stream=sys.stdout)
STREAM_HANDLER.setLevel(LEVEL)
STREAM_HANDLER.setFormatter(FORMATTER)

logging.basicConfig(
    level=LEVEL,
    format=FORMAT,
    handlers=[
        FILE_HANDLER,
        STREAM_HANDLER
    ]
)

logging.debug(f"Log file: {FILE_NAME}")
