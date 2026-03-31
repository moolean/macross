from __future__ import annotations

import sys
from pathlib import Path

from .config import APP_NAME, CLI_NAME, CONFIG_DIR, CONFIG_FILE, DEFAULT_CONFIG, DEFAULT_GROUP, INVENTORY_FILE, LOCAL_BIN_DIR, LOCAL_SHARE_DIR, VERSION, ensure_dirs
from .doctor import Doctor
from .inventory import Inventory
from .setup_wizard import SetupWizard
from .shell import MacrossShell


def ensure_runtime_files(base_dir: Path) -> None:
    ensure_dirs()
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(DEFAULT_CONFIG, encoding="utf-8")
    ansible_cfg = CONFIG_DIR / "ansible.cfg"
    if not ansible_cfg.exists():
        ansible_cfg.write_text("[defaults]\ninventory = ~/.macross/inventory.ini\nhost_key_checking = False\ninterpreter_python = /usr/bin/python3\nstdout_callback = default\nretry_files_enabled = False\ntimeout = 20\n\n[ssh_connection]\npipelining = True\n", encoding="utf-8")


def is_initialized() -> bool:
    return CONFIG_DIR.exists() and CONFIG_FILE.exists() and INVENTORY_FILE.exists()


def cmd_init() -> int:
    return SetupWizard().run()


def cmd_hosts() -> int:
    inv = Inventory(INVENTORY_FILE)
    hosts = inv.hosts_for_group(DEFAULT_GROUP)
    if not hosts:
        print("No hosts configured in default group.")
        return 1
    for host in hosts:
        print(f"{host.alias:<12} {host.ansible_user}@{host.ansible_host}")
    return 0


def cmd_add_host() -> int:
    ensure_runtime_files(Path.cwd())
    inv = Inventory(INVENTORY_FILE)
    inv.ensure_exists()
    alias = input("Host alias: ").strip()
    address = input("IP or hostname: ").strip()
    user = input("SSH username: ").strip()
    default_group = DEFAULT_GROUP
    group = input(f"Group [{default_group}]: ").strip() or default_group
    try:
        inv.backup()
        inv.add_host(alias=alias, ansible_host=address, ansible_user=user, group=group)
        inv.save()
    except ValueError as exc:
        print(exc)
        return 1
    print(f"Added host '{alias}' to group '{group}'.")
    test_now = input("Test SSH now? [Y/n] ").strip().lower()
    if test_now in {"", "y", "yes"}:
        from subprocess import run
        result = run(["ssh", f"{user}@{address}", "exit"], text=True)
        if result.returncode == 0:
            print("SSH connectivity looks good.")
        else:
            print("SSH test failed.")
            print("Possible reasons:")
            print("- Remote Login is disabled")
            print("- username / host is wrong")
            print("- network is unreachable")
            print("- key-based auth is not configured yet")
    return 0


def cmd_doctor() -> int:
    ensure_runtime_files(Path.cwd())
    inv = Inventory(INVENTORY_FILE)
    return Doctor(inv).run()


def cmd_shell() -> int:
    ensure_runtime_files(Path.cwd())
    inv = Inventory(INVENTORY_FILE)
    if not inv.all_hosts():
        print(f"{APP_NAME} is installed, but no hosts are configured yet.\n")
        print("Next steps:")
        print(f"  {CLI_NAME} add-host   # add your first machine")
        print(f"  {CLI_NAME} doctor     # check your environment")
        return 1
    return MacrossShell(inv, group=DEFAULT_GROUP, color=True).run()


def cmd_version() -> int:
    print(f"{APP_NAME} {VERSION}")
    return 0


def print_help() -> int:
    print(f"{APP_NAME} ({CLI_NAME})\n\nCommands:\n  mx               Start shell, or run setup on first launch\n  mx init          Run setup wizard\n  mx doctor        Check environment and hosts\n  mx add-host      Add one host interactively\n  mx hosts         List hosts in default group\n  mx shell         Enter interactive shell\n  mx version       Show version\n  mx help          Show this help")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    ensure_runtime_files(Path.cwd())
    if not argv:
        if not is_initialized():
            return cmd_init()
        return cmd_shell()
    cmd = argv[0]
    if cmd in {"help", "-h", "--help"}:
        return print_help()
    if cmd in {"version", "-V", "--version"}:
        return cmd_version()
    if cmd == "init":
        return cmd_init()
    if cmd == "doctor":
        return cmd_doctor()
    if cmd == "add-host":
        return cmd_add_host()
    if cmd == "hosts":
        return cmd_hosts()
    if cmd == "shell":
        return cmd_shell()
    print(f"Unknown command: {cmd}\n")
    return print_help()


if __name__ == "__main__":
    raise SystemExit(main())
