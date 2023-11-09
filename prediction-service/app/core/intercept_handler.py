import logging
from typing import Optional
from types import FrameType
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelname

        frame: Optional[FrameType] = logging.currentframe()
        depth: int = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        if frame:
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
        else:
            logger.opt(exception=record.exc_info).log(level, record.getMessage())
