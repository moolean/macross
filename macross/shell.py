from __future__ import annotations

import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

from .config import APP_NAME, CONFIG_FILE, DEFAULT_GROUP, INVENTORY_FILE
from .inventory import Host, Inventory
from .utils import RED, YELLOW, GREEN, ask_yes_no, colorize, stable_color

DANGEROUS_PATTERNS = [
    "rm -rf",
    "rm -r",
    "find ",
    "reboot",
    "shutdown",
    "halt",
    "poweroff",
    "mkfs",
    "dd ",
    "diskutil eraseDisk",
    "diskutil partitionDisk",
    "chmod -R",
    "chown -R /",
]


@dataclass
class RemoteBlock:
    host: str
    status: str
    body: str


class MacrossShell:
    def __init__(self, inventory: Inventory, group: str = DEFAULT_GROUP, color: bool = True) -> None:
        self.inventory = inventory
        self.current_group = group if group in inventory.groups else (inventory.list_groups()[0] if inventory.list_groups() else DEFAULT_GROUP)
        self.mode = "all"
        self.focus_host: Optional[str] = None
        self.only_hosts: List[str] = []
        self.color = color
        self.env = os.environ.copy()
        self.env["ANSIBLE_CONFIG"] = str(CONFIG_FILE.parent / "ansible.cfg")

    def prompt(self) -> str:
        if self.mode == "focus" and self.focus_host:
            return f"{self.focus_host}> "
        if self.mode == "only" and self.only_hosts:
            return f"[{','.join(self.only_hosts)}]> "
        return "mx> " if self.current_group == DEFAULT_GROUP else f"{self.current_group}> "

    def run(self) -> int:
        self.print_banner()
        while True:
            try:
                line = input(self.prompt()).strip()
            except EOFError:
                print()
                return 0
            except KeyboardInterrupt:
                print()
                continue
            if not line:
                continue
            if self.handle_builtin(line):
                continue
            if self.should_confirm(line) and not ask_yes_no(f"This command looks dangerous and will run on {len(self.current_targets())} host(s):\n\n  {line}\n\nContinue?", default=False):
                print("Cancelled.")
                continue
            self.run_remote_command(line)

    def print_banner(self) -> None:
        hosts = ", ".join(h.alias for h in self.inventory.hosts_for_group(self.current_group))
        print(f"{APP_NAME} shell ready.")
        print(f"Group: {self.current_group}")
        print(f"Hosts: {hosts}")
        print("Type 'help' for commands.")

    def current_targets(self) -> List[str]:
        hosts = [h.alias for h in self.inventory.hosts_for_group(self.current_group)]
        if self.mode == "focus" and self.focus_host:
            return [self.focus_host]
        if self.mode == "only":
            return list(self.only_hosts)
        return hosts

    def handle_builtin(self, line: str) -> bool:
        parts = line.split()
        cmd = parts[0]
        if line in {"exit", "quit"}:
            raise SystemExit(0)
        if line == "help":
            self.print_help(); return True
        if line == "hosts":
            for h in self.inventory.hosts_for_group(self.current_group):
                print(f"- {h.alias}: {h.ansible_user}@{h.ansible_host}")
            return True
        if line == "targets":
            print(", ".join(self.current_targets())); return True
        if line == "groups":
            for g in self.inventory.list_groups(): print(g)
            return True
        if cmd == "use":
            if len(parts) != 2:
                print("Usage: use <group>"); return True
            if parts[1] not in self.inventory.groups:
                print(f"Unknown group: {parts[1]}"); return True
            self.current_group = parts[1]
            self.mode = "all"; self.focus_host = None; self.only_hosts = []
            print(f"Switched group to {self.current_group}.")
            return True
        if cmd == "focus":
            if len(parts) != 2:
                print("Usage: focus <host>"); return True
            if parts[1] not in [h.alias for h in self.inventory.hosts_for_group(self.current_group)]:
                print(f"Unknown host in current group: {parts[1]}"); return True
            self.mode = "focus"; self.focus_host = parts[1]; self.only_hosts = []
            print(f"Focused on {self.focus_host}.")
            return True
        if cmd == "only":
            if len(parts) < 2:
                print("Usage: only <host1> <host2> ..."); return True
            valid = [h.alias for h in self.inventory.hosts_for_group(self.current_group)]
            bad = [p for p in parts[1:] if p not in valid]
            if bad:
                print(f"Unknown host(s) in current group: {', '.join(bad)}"); return True
            self.mode = "only"; self.only_hosts = parts[1:]; self.focus_host = None
            print(f"Restricted to: {', '.join(self.only_hosts)}")
            return True
        if line == "all":
            self.mode = "all"; self.focus_host = None; self.only_hosts = []
            print("Switched to broadcast mode.")
            return True
        if line == "mode":
            print(f"Current mode: {self.mode} ({', '.join(self.current_targets())})"); return True
        if line == "inventory":
            print(INVENTORY_FILE); return True
        if line.startswith("!"):
            subprocess.run(line[1:].strip(), shell=True)
            return True
        return False

    def print_help(self) -> None:
        print("Built-in commands:\n  hosts\n  targets\n  groups\n  use <group>\n  focus <host>\n  only <host...>\n  all\n  mode\n  inventory\n  !<cmd>\n  help\n  exit / quit")

    def should_confirm(self, line: str) -> bool:
        if self.mode != "all":
            return False
        lowered = line.lower()
        return any(pat in lowered for pat in DANGEROUS_PATTERNS)

    def run_remote_command(self, command: str) -> None:
        target = ":".join(self.current_targets()) if self.mode == "only" else (self.focus_host if self.mode == "focus" else self.current_group)
        completed = subprocess.run(["ansible", target, "-m", "shell", "-a", command], capture_output=True, text=True, cwd=str(INVENTORY_FILE.parent), env=self.env)
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        blocks = self.parse_blocks(stdout)
        for block in blocks:
            host_color = stable_color(block.host)
            title = f"[{block.host}] {block.status}"
            if block.status == "ERROR":
                title = colorize(title, RED, self.color)
            elif block.status in {"WARN", "TIMEOUT", "UNREACHABLE"}:
                title = colorize(title, YELLOW, self.color)
            else:
                title = colorize(title, host_color, self.color)
            print(title)
            if block.body:
                print(block.body)
            print()
        if stderr:
            print(stderr, file=sys.stderr)
        statuses = [b.status for b in blocks]
        ok = sum(1 for s in statuses if s == "OK")
        failed = len(statuses) - ok
        if statuses:
            print(f"Summary: {ok} succeeded, {failed} failed, {len(statuses)} total")

    def parse_blocks(self, text: str) -> List[RemoteBlock]:
        if not text:
            return []
        lines = text.splitlines()
        blocks: List[RemoteBlock] = []
        current_host: Optional[str] = None
        current_status = "OK"
        current_lines: List[str] = []

        def flush() -> None:
            nonlocal current_host, current_status, current_lines
            if current_host is None:
                return
            body = "\n".join(current_lines).strip()
            blocks.append(RemoteBlock(current_host, current_status, body))
            current_host = None
            current_status = "OK"
            current_lines = []

        for line in lines:
            if " | " in line:
                flush()
                current_host = line.split(" | ", 1)[0].strip()
                if "FAILED" in line:
                    current_status = "ERROR"
                elif "UNREACHABLE" in line:
                    current_status = "UNREACHABLE"
                else:
                    current_status = "OK"
                maybe = line.split(">>", 1)
                if len(maybe) == 2 and maybe[1].strip():
                    current_lines.append(maybe[1].strip())
            else:
                current_lines.append(line)
        flush()
        return blocks
