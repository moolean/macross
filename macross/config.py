from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "Macross"
CLI_NAME = "mx"
DEFAULT_GROUP = "macs"
VERSION = "0.1.0-alpha"
CONFIG_DIR = Path.home() / ".macross"
CONFIG_FILE = CONFIG_DIR / "config.toml"
INVENTORY_FILE = CONFIG_DIR / "inventory.ini"
LOG_DIR = CONFIG_DIR / "logs"
BACKUP_DIR = CONFIG_DIR / "backups"
EXAMPLES_DIR = CONFIG_DIR / "examples"
LOCAL_SHARE_DIR = Path.home() / ".local" / "share" / "macross"
LOCAL_BIN_DIR = Path.home() / ".local" / "bin"
DEFAULT_CONFIG = """[general]\ninventory = \"~/.macross/inventory.ini\"\ndefault_group = \"macs\"\ncolor = true\nask_before_install = true\n\n[shell]\ndefault_mode = \"all\"\nshow_banner = true\ndanger_confirm = true\n"""
DEFAULT_INVENTORY = """[macs]\n# Example:\n# mac1 ansible_host=192.168.1.10 ansible_user=yourname\n"""


def ensure_dirs() -> None:
    for path in (CONFIG_DIR, LOG_DIR, BACKUP_DIR, EXAMPLES_DIR):
        path.mkdir(parents=True, exist_ok=True)


def expand_home(value: str) -> Path:
    return Path(os.path.expanduser(value)).resolve()
