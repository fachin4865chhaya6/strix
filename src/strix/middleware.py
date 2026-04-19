"""Middleware support for Strix.

Provides base classes and utilities for building middleware
that can be registered with a Strix application instance.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class MiddlewareError(Exception):
    """Raised when a middleware encounters an unrecoverable error."""


class BaseMiddleware(ABC):
    """Abstract base class for all Strix middleware.

    Subclass this and implement :meth:`process` to create custom
    middleware.  Middleware instances are called in the order they
    were registered on the :class:`~strix.core.Strix` application.

    Example::

        class LoggingMiddleware(BaseMiddleware):
            async def process(self, context, call_next):
                logger.info("before: %s", context)
                result = await call_next(context)
                logger.info("after: %s", context)
                return result
    """

    #: Human-readable name used in logs and error messages.
    name: str = ""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not cls.name:
            cls.name = cls.__name__

    @abstractmethod
    async def process(self, context: dict[str, Any], call_next: Callable) -> Any:
        """Process the context and delegate to the next middleware.

        Args:
            context: Mutable mapping shared across the middleware chain.
            call_next: Coroutine that invokes the remainder of the chain.

        Returns:
            The final result produced by the chain.
        """

    async def on_error(self, exc: Exception, context: dict[str, Any]) -> None:
        """Called when an unhandled exception propagates through this middleware.

        Override to add custom error handling or cleanup logic.
        The default implementation logs the error and re-raises.

        Args:
            exc: The exception that was raised.
            context: The context at the time of the error.
        """
        logger.error(
            "Middleware '%s' encountered an error: %s",
            self.name,
            exc,
            exc_info=True,
        )
        raise exc


class MiddlewareChain:
    """Builds and executes an ordered chain of :class:`BaseMiddleware` instances."""

    def __init__(self, middlewares: Optional[list[BaseMiddleware]] = None) -> None:
        self._middlewares: list[BaseMiddleware] = list(middlewares or [])

    def add(self, middleware: BaseMiddleware) -> None:
        """Append a middleware to the end of the chain."""
        if not isinstance(middleware, BaseMiddleware):
            raise TypeError(
                f"Expected a BaseMiddleware instance, got {type(middleware).__name__!r}"
            )
        self._middlewares.append(middleware)
        logger.debug("Registered middleware: %s", middleware.name)

    async def run(self, context: dict[str