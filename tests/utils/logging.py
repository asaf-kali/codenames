import logging
import sys
from logging.config import dictConfig


def configure_logging():
    config = {
        "version": 1,
        "level": logging.WARNING,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s [%(name)s:%(lineno)d]",
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": logging.DEBUG,
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "codenames": {
                "level": logging.DEBUG,
                "handlers": ["console"],
                "propagate": False,
            }
        },
    }
    dictConfig(config)
