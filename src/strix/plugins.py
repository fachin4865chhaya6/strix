"""Plugin system for Strix.

Provides a base class and registry for extending Strix functionality
through a consistent plugin interface.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from strix.core import Strix

logger = logging.getLogger(__name__)


class PluginError(Exception):
    """Raised when a plugin encounters an error."""


class PluginRegistry:
    """Central registry for all loaded plugins."""

    _plugins: ClassVar[dict[str, type[BasePlugin]]] = {}

    @classmethod
    def register(cls, plugin_cls: type[BasePlugin]) -> type[BasePlugin]:
        """Register a plugin class by its name."""
        name = plugin_cls.name
        if not name:
            raise PluginError(f"Plugin {plugin_cls.__qualname__} must define a non-empty 'name' attribute.")
        if name in cls._plugins:
            raise PluginError(f"A plugin named '{name}' is already registered.")
        cls._plugins[name] = plugin_cls
        logger.debug("Registered plugin: %s", name)
        return plugin_cls

    @classmethod
    def get(cls, name: str) -> type[BasePlugin]:
        """Retrieve a registered plugin class by name."""
        try:
            return cls._plugins[name]
        except KeyError:
            raise PluginError(f"No plugin registered with name '{name}'.") from None

    @classmethod
    def all(cls) -> dict[str, type[BasePlugin]]:
        """Return a copy of all registered plugins."""
        return dict(cls._plugins)

    @classmethod
    def clear(cls) -> None:
        """Unregister all plugins. Primarily useful for testing."""
        cls._plugins.clear()


class BasePlugin:
    """Base class for all Strix plugins.

    Subclasses must define a unique ``name`` class attribute and may
    override ``setup`` / ``teardown`` lifecycle hooks.

    Example::

        @PluginRegistry.register
        class MyPlugin(BasePlugin):
            name = "my_plugin"

            def setup(self, app: Strix) -> None:
                app.register("my_service", MyService())
    """

    #: Unique identifier for this plugin. Must be set by subclasses.
    name: ClassVar[str] = ""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Auto-register only concrete subclasses that provide a name.
        if cls.name:
            try:
                PluginRegistry.register(cls)
            except PluginError as exc:
                logger.warning("Auto-registration skipped: %s", exc)

    def setup(self, app: Strix) -> None:  # noqa: B027
        """Called when the plugin is attached to a Strix application.

        Override this method to perform initialisation work such as
        registering services or attaching middleware.
        """

    def teardown(self, app: Strix) -> None:  # noqa: B027
        """Called when the Strix application is shutting down.

        Override this method to release resources held by the plugin.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
