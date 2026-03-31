from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import List

from .config import APP_NAME, CONFIG_DIR, CONFIG_FILE, INVENTORY_FILE
from .inventory import Inventory, Host
from .utils import command_exists


@dataclass
class HostCheck:
    alias: str
    status: str
    details: str


class Doctor:
    def __init__(self, inventory: Inventory):
        self.inventory = inventory

    def run(self) -> int:
        print(f"{APP_NAME} Doctor\n")
        env = self.check_environment()
        cfg = self.check_config()
        host_checks = self.check_hosts()
        self.print_environment(env)
        self.print_config(cfg)
        self.print_hosts(host_checks)
        self.print_next_steps(host_checks)
        failures = sum(1 for _, ok in env if not ok) + sum(1 for _, ok in cfg if not ok) + sum(1 for h in host_checks if h.status != "OK")
        return 0 if failures == 0 else 1

    def check_environment(self):
        return [
            ("python3", command_exists("python3")),
            ("ssh", command_exists("ssh")),
            ("ansible", command_exists("ansible")),
        ]

    def check_config(self):
        return [
            (str(CONFIG_DIR), CONFIG_DIR.exists()),
            (str(CONFIG_FILE), CONFIG_FILE.exists()),
            (str(INVENTORY_FILE), INVENTORY_FILE.exists()),
        ]

    def check_hosts(self) -> List[HostCheck]:
        hosts = self.inventory.all_hosts()
        if not hosts:
            return []
        results: List[HostCheck] = []
        failed = 0
        for host in hosts:
            check = self._check_host(host)
            results.append(check)
            if check.status != "OK":
                failed += 1
            if failed >= 3:
                results.append(HostCheck(alias="SYSTEM", status="FAIL", details="Too many hosts failed connectivity checks (>=3). Please fix network / SSH issues first."))
                break
        return results

    def _check_host(self, host: Host) -> HostCheck:
        ssh_base = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=5",
            f"{host.ansible_user}@{host.ansible_host}",
        ]
        probe = subprocess.run(ssh_base + ["true"], capture_output=True, text=True)
        if probe.returncode == 0:
            ping = subprocess.run(["ansible", host.alias, "-m", "ping"], capture_output=True, text=True, cwd=str(INVENTORY_FILE.parent))
            if ping.returncode == 0 and "pong" in ping.stdout:
                return HostCheck(host.alias, "OK", "ssh, key-auth, ansible")
            return HostCheck(host.alias, "WARN", "ssh ok, ansible ping failed")
        stderr = (probe.stderr or "").lower()
        if "permission denied" in stderr:
            return HostCheck(host.alias, "WARN", "ssh ok, password required or key auth not configured")
        if "operation timed out" in stderr or "timed out" in stderr:
            return HostCheck(host.alias, "FAIL", "unreachable (timeout)")
        if "could not resolve hostname" in stderr:
            return HostCheck(host.alias, "FAIL", "hostname resolution failed")
        if stderr.strip():
            return HostCheck(host.alias, "FAIL", stderr.strip().splitlines()[-1])
        return HostCheck(host.alias, "FAIL", "unreachable")

    def print_environment(self, checks):
        print("[Environment]")
        for name, ok in checks:
            print(f"{name:<20} {'OK' if ok else 'FAIL'}")
        print()

    def print_config(self, checks):
        print("[Config]")
        for name, ok in checks:
            print(f"{name:<20} {'OK' if ok else 'FAIL'}")
        print()

    def print_hosts(self, checks: List[HostCheck]):
        print("[Hosts]")
        if not checks:
            print("No hosts configured.")
            print()
            return
        for item in checks:
            print(f"{item.alias:<20} {item.status:<5} {item.details}")
        healthy = sum(1 for item in checks if item.status == 'OK')
        warning = sum(1 for item in checks if item.status == 'WARN')
        failed = sum(1 for item in checks if item.status == 'FAIL')
        print()
        print(f"Summary: {healthy} healthy, {warning} warning, {failed} failed")
        print()

    def print_next_steps(self, checks: List[HostCheck]):
        actions = []
        for item in checks:
            if item.alias == 'SYSTEM':
                actions.append(item.details)
            elif item.status == 'WARN':
                actions.append(f"- {item.alias}: check SSH key-based auth")
            elif item.status == 'FAIL':
                actions.append(f"- {item.alias}: check IP / network / Remote Login")
        if actions:
            print("Next steps:")
            for action in actions:
                print(action)
