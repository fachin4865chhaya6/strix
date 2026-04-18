"""Strix - A fork of usestrix/strix.

A lightweight Python library for structured logging and observability.
"""

from strix.logger import Logger
from strix.config import StrixConfig

__version__ = "0.1.0"
__author__ = "Strix Contributors"
__license__ = "MIT"

__all__ = [
    "Logger",
    "StrixConfig",
    "__version__",
]
