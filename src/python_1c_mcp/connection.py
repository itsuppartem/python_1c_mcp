"""Environment-based Infobase connection (one shared session per process)."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from urllib.parse import unquote, urlparse

from python_1c_odata import Infobase

_FORMATS = frozenset({"json", "atom", "auto"})
_TRUTHY = frozenset({"1", "true", "yes", "on"})


class ConfigError(ValueError):
    """Missing or invalid connection settings."""


@dataclass(frozen=True)
class ConnectionConfig:
    server: str
    infobase: str
    username: str
    password: str
    format: str = "json"
    debug: bool = False


_lock = asyncio.Lock()
_infobase: Infobase | None = None
_config: ConnectionConfig | None = None


def parse_onec_url(url: str) -> ConnectionConfig:
    """Parse ``http://user:pass@host:port/publication`` into connection fields."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ConfigError(f"ONEC_URL scheme must be http or https, got {parsed.scheme!r}")
    if not parsed.hostname:
        raise ConfigError("ONEC_URL must include a host")
    if not parsed.username or parsed.password is None:
        raise ConfigError("ONEC_URL must include user:pass@ in the authority")
    path = parsed.path.strip("/")
    if not path:
        raise ConfigError("ONEC_URL must include the infobase publication path")
    port = f":{parsed.port}" if parsed.port else ""
    server = f"{parsed.scheme}://{parsed.hostname}{port}"
    return ConnectionConfig(
        server=server,
        infobase=path.split("/")[0],
        username=unquote(parsed.username),
        password=unquote(parsed.password),
        format=os.environ.get("ONEC_FORMAT", "json"),
        debug=os.environ.get("ONEC_DEBUG", "").lower() in _TRUTHY,
    )


def load_config() -> ConnectionConfig:
    """Load connection settings from environment variables."""
    url = os.environ.get("ONEC_URL")
    if url:
        cfg = parse_onec_url(url)
    else:
        missing = [
            name
            for name, value in (
                ("ONEC_SERVER", os.environ.get("ONEC_SERVER")),
                ("ONEC_INFOBASE", os.environ.get("ONEC_INFOBASE")),
                ("ONEC_USER", os.environ.get("ONEC_USER")),
                ("ONEC_PASSWORD", os.environ.get("ONEC_PASSWORD")),
            )
            if not value
        ]
        if missing:
            raise ConfigError(
                "Missing required environment variable(s): "
                + ", ".join(missing)
                + ". Set them individually or use ONEC_URL=http://user:pass@host/base"
            )
        fmt = os.environ.get("ONEC_FORMAT", "json")
        cfg = ConnectionConfig(
            server=os.environ["ONEC_SERVER"].strip(),
            infobase=os.environ["ONEC_INFOBASE"].strip(),
            username=os.environ["ONEC_USER"],
            password=os.environ["ONEC_PASSWORD"],
            format=fmt,
            debug=os.environ.get("ONEC_DEBUG", "").lower() in _TRUTHY,
        )
    if cfg.format not in _FORMATS:
        raise ConfigError(f"ONEC_FORMAT must be one of {sorted(_FORMATS)}, got {cfg.format!r}")
    return cfg


def validate_config() -> ConnectionConfig:
    """Validate env at startup; cache config for lazy Infobase init."""
    global _config
    _config = load_config()
    return _config


def _build_infobase(cfg: ConnectionConfig) -> Infobase:
    return Infobase(
        cfg.server,
        cfg.infobase,
        cfg.username,
        cfg.password,
        format=cfg.format,
        debug=cfg.debug,
    )


async def get_infobase() -> Infobase:
    """Return the shared Infobase, creating the HTTP session on first use."""
    global _infobase
    async with _lock:
        if _infobase is None:
            cfg = _config if _config is not None else load_config()
            _infobase = _build_infobase(cfg)
        await _infobase._ensure_session()
        return _infobase


async def close_infobase() -> None:
    """Close the shared HTTP session."""
    global _infobase
    async with _lock:
        if _infobase is not None:
            await _infobase.aclose()
            _infobase = None
