"""Use HA's schema library on each supported release, without a dependency."""

from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["schema"]

if TYPE_CHECKING:
    import probatio as schema
else:
    # Since HA 2026.9, startup aliases this public name to Probatio.
    # On older HA it resolves to the original Voluptuous package.
    schema = import_module("voluptuous")
