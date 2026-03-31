#!/usr/bin/env python3
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INVENTORY = BASE_DIR / "inventory.ini"
DEFAULT_ANSIBLE_CFG = BASE_DIR / "ansible.cfg"


class FleetShell:
    def __init__(self, inventory_path: Path = DEFAULT_INVENTORY) -> None:
        self.inventory_path = inventory_path
        self.hosts = self._parse_inventory(inventory_path)
        if not self.hosts:
            raise SystemExit(f"No hosts found in inventory: {inventory_path}")
        self.current_target = "all"
        self.env = os.environ.copy()
        self.env.setdefault("ANSIBLE_CONFIG", str(DEFAULT_ANSIBLE_CFG))

    def _parse_inventory(self, path: Path) -> Dict[str, Dict[str, str]]:
        hosts: Dict[str, Dict[str, str]] = {}
        in_macs = False
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                in_macs = line == "[macs]"
                continue
            if not in_macs:
                continue
            parts = shlex.split(line)
            if not parts:
                continue
            alias = parts[0]
            attrs: Dict[str, str] = {"alias": alias}
            for part in parts[1:]:
                if "=" in part:
                    key, value = part.split("=", 1)
                    attrs[key] = value
            hosts[alias] = attrs
        return hosts

    def prompt(self) -> str:
        return "fleet> " if self.current_target == "all" else f"{self.current_target}> "

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

            self.run_remote_command(line)

    def print_banner(self) -> None:
        print("Fleet shell ready.")
        print(f"Inventory: {self.inventory_path}")
        print(f"Hosts: {', '.join(self.hosts.keys())}")
        print("Type 'help' for commands.")

    def handle_builtin(self, line: str) -> bool:
        parts = line.split()
        cmd = parts[0]

        if line in {"exit", "quit"}:
            raise SystemExit(0)
        if line == "help":
            self.print_help()
            return True
        if line == "hosts":
            self.print_hosts()
            return True
        if line == "mode":
            print(f"Current mode: {self.current_target}")
            return True
        if line == "all":
            self.current_target = "all"
            print("Switched to broadcast mode.")
            return True
        if cmd == "focus":
            if len(parts) != 2:
                print("Usage: focus <host>")
                return True
            host = parts[1]
            if host not in self.hosts:
                print(f"Unknown host: {host}")
                return True
            self.current_target = host
            print(f"Focused on {host}.")
            return True
        if line == "inventory":
            print(self.inventory_path)
            return True
        if line.startswith("!"):
            self.run_local_command(line[1:].strip())
            return True
        return False

    def print_help(self) -> None:
        print(
            """
Built-in commands:
  hosts            List all hosts
  focus <host>     Switch to one host
  all              Switch back to all hosts
  mode             Show current mode
  inventory        Show inventory path
  !<cmd>           Run local shell command
  help             Show this help
  exit / quit      Exit fleet shell

Anything else is treated as a remote shell command.
Examples:
  hostname
  uptime
  mkdir -p ~/demo
  cat ~/demo/file.txt
""".strip()
        )

    def print_hosts(self) -> None:
        for alias, attrs in self.hosts.items():
            host = attrs.get("ansible_host", "?")
            user = attrs.get("ansible_user", "?")
            print(f"- {alias}: {user}@{host}")

    def run_local_command(self, command: str) -> None:
        if not command:
            print("Usage: !<local command>")
            return
        completed = subprocess.run(command, shell=True, env=self.env)
        if completed.returncode != 0:
            print(f"[local] exit code: {completed.returncode}")

    def run_remote_command(self, command: str) -> None:
        target = self.current_target
        ansible_cmd = [
            "ansible",
            target,
            "-m",
            "shell",
            "-a",
            command,
        ]

        try:
            completed = subprocess.run(
                ansible_cmd,
                capture_output=True,
                text=True,
                env=self.env,
                cwd=str(BASE_DIR),
            )
        except FileNotFoundError:
            print("ansible command not found. Please ensure Ansible is installed.")
            return

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()

        if stdout:
            print(self._format_ansible_output(stdout, target))
        if stderr:
            print(stderr, file=sys.stderr)
        if completed.returncode != 0 and not stdout and not stderr:
            print(f"Command failed with exit code {completed.returncode}")

    def _format_ansible_output(self, text: str, target: str) -> str:
        if target != "all":
            return self._strip_single_host_wrapper(text, target)

        lines = text.splitlines()
        blocks: List[str] = []
        current_host: Optional[str] = None
        current_lines: List[str] = []

        def flush() -> None:
            nonlocal current_host, current_lines
            if current_host is None:
                return
            body = "\n".join(current_lines).strip()
            if body:
                blocks.append(f"[{current_host}]\n{body}")
            else:
                blocks.append(f"[{current_host}]")
            current_host = None
            current_lines = []

        for line in lines:
            if " | " in line:
                flush()
                current_host = line.split(" | ", 1)[0].strip()
                maybe = line.split(">>", 1)
                if len(maybe) == 2 and maybe[1].strip():
                    current_lines.append(maybe[1].strip())
            else:
                current_lines.append(line)
        flush()
        return "\n\n".join(blocks)

    def _strip_single_host_wrapper(self, text: str, host: str) -> str:
        lines = text.splitlines()
        if not lines:
            return text
        first = lines[0]
        if first.startswith(host + " | "):
            maybe = first.split(">>", 1)
            body: List[str] = []
            if len(maybe) == 2 and maybe[1].strip():
                body.append(maybe[1].strip())
            body.extend(lines[1:])
            return "\n".join(body).strip()
        return text


def main() -> int:
    inventory_path = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DEFAULT_INVENTORY
    shell = FleetShell(inventory_path)
    return shell.run()


if __name__ == "__main__":
    raise SystemExit(main())
