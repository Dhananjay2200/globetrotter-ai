"""
Logging configuration for GlobeTrotter AI.
Provides clean, formatted console logging for background agents and API requests.
"""

import logging
import sys


def setup_logger(name: str = "globetrotter") -> logging.Logger:
    """Configures and returns an application logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Standard clean formatting for Windows terminal
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger


logger = setup_logger()
