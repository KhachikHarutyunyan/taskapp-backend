import json
import logging
import logging.config
import time
import traceback
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "level": record.levelname,
            "timestamp": time.strftime(
                "%Y-%m-%d %H:%M:%S,%f", time.localtime(record.created)
            )[:-3],
            "message": record.getMessage(),
        }

        excluded_keys = {
            "args",
            "exc_info",
            "exc_text",
            "stack_info",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "taskName",
            "name",
            "msg",
            "levelname",
            "levelno",
            "filename",
            "funcName",
            "created",
            "lineno",
            "module",
            "pathname",
        }

        for key, value in record.__dict__.items():
            if key not in excluded_keys and not key.startswith("_"):
                log_data[key] = value

        if record.exc_info:
            tb = traceback.extract_tb(record.exc_info[2])
            if tb:
                frame = tb[-1]
                log_data.update(
                    {
                        "error_file": frame.filename,
                        "error_line": frame.lineno,
                        "error_function": frame.name,
                    }
                )
        else:
            log_data.update(
                {
                    "module": record.module,
                    "lineno": record.lineno,
                    "funcname": record.funcName,
                    "pathname": record.pathname,
                }
            )

        return json.dumps(log_data)


class LevelFilter(logging.Filter):
    """Filter for desiding which log level to write."""

    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": JsonFormatter,
        },
    },
    "filters": {
        "info_filter": {
            "()": LevelFilter,
            "level": logging.INFO,
        },
        "warn_filter": {
            "()": LevelFilter,
            "level": logging.WARNING,
        },
        "error_filter": {
            "()": LevelFilter,
            "level": logging.ERROR,
        },
        "critical_filter": {
            "()": LevelFilter,
            "level": logging.CRITICAL,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "json",
        },
        "file_info": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": str(LOG_DIR / "info.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "filters": ["info_filter"],
        },
        "file_warning": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "json",
            "filename": str(LOG_DIR / "warning.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "filters": ["warn_filter"],
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filename": str(LOG_DIR / "error.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "filters": ["error_filter"],
        },
        "file_critical": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "CRITICAL",
            "formatter": "json",
            "filename": str(LOG_DIR / "critical.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "filters": ["critical_filter"],
        },
    },
    "loggers": {
        "app_logger": {
            "level": "DEBUG",
            "handlers": [
                "console",
                "file_info",
                "file_warning",
                "file_error",
                "file_critical",
            ],
            "propagate": False,
        },
    },
}


logging.config.dictConfig(logger_config)
logger = logging.getLogger("app_logger")
