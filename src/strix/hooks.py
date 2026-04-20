"""Hook system for strix — allows plugins and middleware to react to lifecycle events."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)


class HookError(Exception):
    """Raised when a hook registration or execution fails."""


class HookRegistry:
    """Registry that manages named hooks and their listeners.

    Hooks are simple named events. Any callable can be registered as a
    listener for a hook. When a hook is fired, all listeners are called
    in registration order with the provided arguments.

    Example::

        hooks = HookRegistry()

        @hooks.on("app.startup")
        def on_startup(context):
            print("App started", context)

        hooks.fire("app.startup", context={"env": "prod"})
    """

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[..., Any]]] = defaultdict(list)

    def on(self, event: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator that registers a listener for *event*."""

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.register(event, fn)
            return fn

        return decorator

    def register(self, event: str, listener: Callable[..., Any]) -> None:
        """Register *listener* for *event*.

        Args:
            event: The hook name (e.g. ``"app.startup"``).
            listener: Any callable; receives the keyword arguments passed to
                :meth:`fire`.

        Raises:
            HookError: If *listener* is not callable.
        """
        if not callable(listener):
            raise HookError(f"Listener for '{event}' must be callable, got {type(listener)!r}")
        self._listeners[event].append(listener)
        logger.debug("Registered listener '%s' for hook '%s'", getattr(listener, "__name__", listener), event)

    def unregister(self, event: str, listener: Callable[..., Any]) -> None:
        """Remove *listener* from *event*. Silent no-op if not registered."""
        try:
            self._listeners[event].remove(listener)
        except ValueError:
            pass

    def fire(self, event: str, **kwargs: Any) -> list[Any]:
        """Fire *event*, calling all registered listeners with *kwargs*.

        Args:
            event: The hook name to fire.
            **kwargs: Arbitrary keyword arguments forwarded to each listener.

        Returns:
            A list of return values from each listener (``None`` values included).

        Raises:
            HookError: If any listener raises an exception (wraps the original).
        """
        results: list[Any] = []
        for listener in self._listeners.get(event, []):
            try:
                result = listener(**kwargs)
                results.append(result)
            except Exception as exc:
                name = getattr(listener, "__name__", repr(listener))
                raise HookError(f"Listener '{name}' raised an error on hook '{event}': {exc}") from exc
        logger.debug("Fired hook '%s' — %d listener(s) called", event, len(results))
        return results

    def listeners(self, event: str) -> list[Callable[..., Any]]:
        """Return a copy of the listener list for *event*."""
        return list(self._listeners.get(event, []))

    def clear(self, event: str | None = None) -> None:
        """Remove all listeners for *event*, or every hook if *event* is ``None``."""
        if event is None:
            self._listeners.clear()
        else:
            self._listeners.pop(event, None)


# Module-level default registry — mirrors the pattern used in plugins.py
_default_registry = HookRegistry()

on = _default_registry.on
register = _default_registry.register
unregister = _default_registry.unregister
fire = _default_registry.fire
listeners = _default_registry.listeners
clear = _default_registry.clear
