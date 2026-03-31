from __future__ import annotations

import shutil
import subprocess
from typing import Iterable, Tuple

RESET = "\033[0m"
COLORS = ["\033[34m", "\033[32m", "\033[33m", "\033[35m", "\033[36m", "\033[94m"]
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, **kwargs)


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    raw = input(f"{prompt} {suffix} ").strip().lower()
    if not raw:
        return default
    return raw in {"y", "yes"}


def colorize(text: str, color: str, enabled: bool = True) -> str:
    if not enabled:
        return text
    return f"{color}{text}{RESET}"


def stable_color(name: str) -> str:
    return COLORS[sum(ord(c) for c in name) % len(COLORS)]


def summarize_counts(statuses: Iterable[str]) -> Tuple[int, int, int]:
    ok = 0
    failed = 0
    total = 0
    for status in statuses:
        total += 1
        if status == "OK":
            ok += 1
        else:
            failed += 1
    return ok, failed, total
