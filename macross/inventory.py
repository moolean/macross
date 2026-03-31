from __future__ import annotations

import re
import shutil
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .config import BACKUP_DIR, DEFAULT_GROUP, DEFAULT_INVENTORY, INVENTORY_FILE

ALIAS_RE = re.compile(r"^[A-Za-z0-9_-]+$")


@dataclass
class Host:
    alias: str
    group: str
    ansible_host: str
    ansible_user: str


class Inventory:
    def __init__(self, path: Path = INVENTORY_FILE):
        self.path = path
        self.groups: Dict[str, List[Host]] = self.load()

    def exists(self) -> bool:
        return self.path.exists()

    def ensure_exists(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(DEFAULT_INVENTORY, encoding="utf-8")

    def load(self) -> Dict[str, List[Host]]:
        groups: Dict[str, List[Host]] = {}
        if not self.path.exists():
            return groups
        current_group: str | None = None
        for raw_line in self.path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_group = line[1:-1]
                groups.setdefault(current_group, [])
                continue
            if current_group is None:
                continue
            parts = shlex.split(line)
            if not parts:
                continue
            alias = parts[0]
            attrs: dict[str, str] = {}
            for part in parts[1:]:
                if "=" in part:
                    k, v = part.split("=", 1)
                    attrs[k] = v
            if "ansible_host" in attrs and "ansible_user" in attrs:
                groups.setdefault(current_group, []).append(
                    Host(alias=alias, group=current_group, ansible_host=attrs["ansible_host"], ansible_user=attrs["ansible_user"])
                )
        return groups

    def save(self) -> None:
        lines: List[str] = []
        for group, hosts in self.groups.items():
            lines.append(f"[{group}]")
            for host in hosts:
                lines.append(
                    f"{host.alias} ansible_host={host.ansible_host} ansible_user={host.ansible_user}"
                )
            lines.append("")
        self.path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def backup(self) -> None:
        if self.path.exists():
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            dst = BACKUP_DIR / f"inventory.{self.path.stat().st_mtime_ns}.bak"
            shutil.copy2(self.path, dst)

    def list_groups(self) -> List[str]:
        return list(self.groups.keys())

    def hosts_for_group(self, group: str = DEFAULT_GROUP) -> List[Host]:
        return list(self.groups.get(group, []))

    def all_hosts(self) -> List[Host]:
        result: List[Host] = []
        for hosts in self.groups.values():
            result.extend(hosts)
        return result

    def find_host(self, alias: str, group: str | None = None) -> Host | None:
        if group:
            for host in self.groups.get(group, []):
                if host.alias == alias:
                    return host
            return None
        for host in self.all_hosts():
            if host.alias == alias:
                return host
        return None

    def add_host(self, alias: str, ansible_host: str, ansible_user: str, group: str = DEFAULT_GROUP) -> Host:
        if not ALIAS_RE.match(alias):
            raise ValueError("Host alias may contain only letters, numbers, '-' and '_'.")
        if self.find_host(alias, group=group):
            raise ValueError(f"Host alias '{alias}' already exists in group '{group}'.")
        self.groups.setdefault(group, []).append(Host(alias=alias, group=group, ansible_host=ansible_host, ansible_user=ansible_user))
        return self.groups[group][-1]
