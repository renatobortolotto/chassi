"""
Local shim for the internal 'atomic' package used by this chassis.
This provides just enough surface for unit tests and simple dev runs.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Callable


class Environments:
    """Tiny env helper compatible with tests."""

    def get_env(self, key: str, default: Any | None = None) -> Any:
        return os.environ.get(key, default)


class Atomic:
    """Minimal app container with routing hooks and logging."""

    def __init__(self, name: str, prefix: str = "/api") -> None:
        self.name = name
        self.prefix = prefix
        self.logger = logging.getLogger(name)
        # Keep config as a simple dict as tests expect .config.update(...)
        self.config: dict[str, Any] = {}
        self._routes: list[tuple[type, str]] = []

    def create_app(self) -> "Atomic":
        # In the real lib this would return a Flask app; here we just return self
        return self

    def create_route(self, resource_cls: type, path: str) -> None:
        self._routes.append((resource_cls, path))
        try:
            name = getattr(resource_cls, "__name__", str(resource_cls))
        except Exception:
            name = str(resource_cls)
        self.logger.info("Initializing route name=%s path=%s", name, path)

    # Optional convenience for local debug; tests don't invoke this meaningfully
    def run(self, host: str = "127.0.0.1", port: int = 8080) -> None:  # pragma: no cover
        self.logger.info("Atomic shim running at http://%s:%s prefix=%s", host, port, self.prefix)


class Resource:
    """Base class for resources; no behavior required for tests."""

    pass


# Proxy request from Flask when available; tests install Flask in dev deps
try:  # pragma: no cover - trivial import proxy
    from flask import request  # type: ignore
except Exception:  # Fallback dummy when Flask missing
    class _DummyRequest:
        def get_json(self, force: bool = False) -> Any:
            return None

        @property
        def values(self) -> dict:
            return {}

    request = _DummyRequest()  # type: ignore
