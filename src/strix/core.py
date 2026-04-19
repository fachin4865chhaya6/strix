"""Core module for Strix.

Provides the main Strix class and core functionality for managing
and orchestrating tasks.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class StrixError(Exception):
    """Base exception for Strix errors."""


class ConfigurationError(StrixError):
    """Raised when configuration is invalid or missing."""


class Strix:
    """Main Strix class.

    Provides a high-level interface for configuring and running Strix.

    Example::

        from strix import Strix

        app = Strix(name="my-app")
        app.run()
    """

    def __init__(
        self,
        name: str,
        debug: bool = False,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize Strix.

        Args:
            name: Application name.
            debug: Enable debug logging.
            config: Optional configuration dictionary.
        """
        self.name = name
        self.debug = debug
        self.config: dict[str, Any] = config or {}
        self._handlers: list[Callable[..., Any]] = []

        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.debug("Debug mode enabled for %s", self.name)
        else:
            logging.basicConfig(level=logging.INFO)

    def register(self, handler: Callable[..., Any]) -> Callable[..., Any]:
        """Register a handler function.

        Can be used as a decorator::

            @app.register
            def my_handler():
                ...

        Args:
            handler: Callable to register.

        Returns:
            The original handler unchanged.
        """
        if not callable(handler):
            raise ConfigurationError(f"Handler {handler!r} is not callable.")
        self._handlers.append(handler)
        logger.debug("Registered handler: %s", handler.__name__)
        return handler

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Execute all registered handlers in order.

        Args:
            *args: Positional arguments forwarded to each handler.
            **kwargs: Keyword arguments forwarded to each handler.

        Raises:
            StrixError: If no handlers are registered.
        """
        if not self._handlers:
            raise StrixError("No handlers registered. Use `app.register` to add handlers.")

        logger.info("Running %s with %d handler(s)", self.name, len(self._handlers))
        for i, handler in enumerate(self._handlers, start=1):
            logger.debug("Executing handler %d/%d: %s", i, len(self._handlers), handler.__name__)
            try:
                handler(*args, **kwargs)
            except Exception as exc:
                # Log the error with context instead of silently crashing mid-run
                logger.error("Handler %s raised an exception: %s", handler.__name__, exc)
                raise

    def __repr__(self) -> str:
        return f"Strix(name={self.name!r}, handlers={len(self._handlers)})"
