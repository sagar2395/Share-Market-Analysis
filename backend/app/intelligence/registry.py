"""Indicator plugin registry.

Indicators self-register via ``@register``; the API discovers them here. Adding a
new indicator never requires editing the core — just drop in a module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # avoid a circular import (indicators import this module to register)
    from app.intelligence.indicators.base import Indicator

_REGISTRY: dict[str, type["Indicator"]] = {}


def register(cls: type["Indicator"]) -> type["Indicator"]:
    _REGISTRY[cls.key] = cls
    return cls


def available() -> list[str]:
    # Ensure built-ins are imported/registered.
    import app.intelligence.indicators  # noqa: F401

    return sorted(_REGISTRY.keys())


def get_indicator(key: str) -> Indicator:
    import app.intelligence.indicators  # noqa: F401

    if key not in _REGISTRY:
        raise KeyError(f"Unknown indicator '{key}'. Available: {sorted(_REGISTRY)}")
    return _REGISTRY[key]()
