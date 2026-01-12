"""Configuration and path management."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".hidemyemail"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir() -> None:
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_config() -> dict:
    """Get the full configuration dictionary."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_config(config: dict) -> None:
    """Save the configuration dictionary."""
    ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_default_username() -> str | None:
    """Get the default Apple ID from config."""
    return get_config().get("default_username")


def set_default_username(username: str) -> None:
    """Set the default Apple ID."""
    config = get_config()
    config["default_username"] = username
    save_config(config)


def clear_default_username() -> None:
    """Clear the default Apple ID."""
    config = get_config()
    config.pop("default_username", None)
    save_config(config)
