import logging
from logging.config import dictConfig

from pickemApi.core.config import config


def obfuscated(email: str, obfuscated_length: int) -> str:
    first_letters = email[:obfuscated_length]
    first, last = email.split("@")
    return first_letters + "*" * (len(first) - obfuscated_length) + "@" + last


class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if config.ENV_STATE == "development" else 32,
                    "default_value": "-",
                },
                "obfucation_email": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if config.ENV_STATE == "development" else 0,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(levelname)-8s %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s %(msecs)03d %(levelname)-8s %(correlation_id)s %(name)s %(lineno)d %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "obfucation_email"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "pickemapi.log",
                    "maxBytes": 1024 * 1024,  # 1MB
                    "backupCount": 5,
                    "encoding": "utf8",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default", "rotating_file"], "level": "INFO"},
                "pickemapi": {
                    "handlers": ["default", "rotating_file"],
                    "level": "DEBUG" if config.ENV_STATE == "development" else "INFO",
                    "propagate": False,
                },
                "aiosqlite": {"handlers": ["default"], "level": "INFO"},
                "fastapi": {"handlers": ["default"], "level": "INFO"},
            },
        }
    )
