"""Tests for connection configuration parsing."""

import pytest

from python_1c_mcp.connection import (
    ConfigError,
    load_config,
    parse_onec_url,
    validate_config,
)


def test_parse_onec_url_splits_credentials_and_publication():
    cfg = parse_onec_url("http://alice:pa%40ss@1c.example:8080/trade/extra")
    assert cfg.server == "http://1c.example:8080"
    assert cfg.infobase == "trade"
    assert cfg.username == "alice"
    assert cfg.password == "pa@ss"


def test_load_config_from_individual_env_vars(monkeypatch):
    monkeypatch.setenv("ONEC_SERVER", "http://host")
    monkeypatch.setenv("ONEC_INFOBASE", "base")
    monkeypatch.setenv("ONEC_USER", "u")
    monkeypatch.setenv("ONEC_PASSWORD", "p")
    cfg = load_config()
    assert cfg.server == "http://host"
    assert cfg.infobase == "base"
    assert cfg.username == "u"
    assert cfg.password == "p"
    assert cfg.format == "json"
    assert cfg.debug is False


def test_onec_url_overrides_individual_vars(monkeypatch):
    monkeypatch.setenv("ONEC_URL", "http://u:p@host/ib")
    monkeypatch.setenv("ONEC_SERVER", "http://ignored")
    monkeypatch.setenv("ONEC_INFOBASE", "ignored")
    monkeypatch.setenv("ONEC_USER", "ignored")
    monkeypatch.setenv("ONEC_PASSWORD", "ignored")
    cfg = load_config()
    assert cfg.server == "http://host"
    assert cfg.infobase == "ib"


def test_missing_env_raises_config_error(monkeypatch):
    monkeypatch.delenv("ONEC_URL", raising=False)
    with pytest.raises(ConfigError, match="ONEC_SERVER"):
        load_config()


def test_invalid_format_raises(monkeypatch):
    monkeypatch.setenv("ONEC_SERVER", "http://host")
    monkeypatch.setenv("ONEC_INFOBASE", "base")
    monkeypatch.setenv("ONEC_USER", "u")
    monkeypatch.setenv("ONEC_PASSWORD", "p")
    monkeypatch.setenv("ONEC_FORMAT", "xml")
    with pytest.raises(ConfigError, match="ONEC_FORMAT"):
        load_config()


def test_validate_config_caches(monkeypatch):
    monkeypatch.setenv("ONEC_URL", "http://u:p@host/base")
    cfg = validate_config()
    assert cfg.infobase == "base"

    import python_1c_mcp.connection as conn

    assert conn._config is not None
    assert conn._config.infobase == "base"


def test_onec_url_without_credentials_raises():
    with pytest.raises(ConfigError, match="user:pass"):
        parse_onec_url("http://host/base")
