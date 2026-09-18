import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

COLOR_RESET = "\x1b[0m"
COLOR_RED = "\x1b[31m"
COLOR_YELLOW = "\x1b[33m"
COLOR_GREEN = "\x1b[32m"
COLOR_CYAN = "\x1b[36m"

class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: COLOR_CYAN,
        logging.INFO: COLOR_GREEN,
        logging.WARNING: COLOR_YELLOW,
        logging.ERROR: COLOR_RED,
        logging.CRITICAL: COLOR_RED,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, COLOR_RESET)
        record.levelname = f"{color}{record.levelname}{COLOR_RESET}"
        record.msg = f"{color}{record.msg}{COLOR_RESET}"
        return super().format(record)

def setup_console_logging(level=logging.DEBUG):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
    file_fmt = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"

    # File logging — always active, works in both dev and EXE mode
    try:
        log_dir = Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / "RAMURI"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / "ramuri.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(file_fmt, datefmt="%Y-%m-%d %H:%M:%S"))
        root_logger.addHandler(file_handler)
    except Exception:
        pass  # If we can't write logs, continue silently

    # Console logging — only if stderr is available (not in windowed EXE mode)
    if sys.stderr is not None:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(ColorFormatter(fmt, datefmt="%H:%M:%S"))
        root_logger.addHandler(console_handler)
    root_logger.addHandler(console_handler)