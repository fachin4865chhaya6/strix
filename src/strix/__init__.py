"""Strix - A fork of usestrix/strix.

A lightweight Python library for structured logging and observability.

Personal fork notes:
- Using this for my own projects; may tweak defaults over time.
"""

from strix.logger import Logger
from strix.config import StrixConfig

__version__ = "0.1.0"
__author__ = "Strix Contributors"
__license__ = "MIT"

# Also expose __author__ and __license__ for introspection
__all__ = [
    "Logger",
    "StrixConfig",
    "__version__",
    "__author__",
    "__license__",
]
