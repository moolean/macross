[English](./README.md) | [简体中文](./README.zh-CN.md)

# Macross

**Control multiple Macs like one shell.**

Macross is a terminal-first control plane for your Macs. It wraps SSH + Ansible in a simpler interactive shell so you can work with multiple machines without juggling multiple terminal windows.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_NAME/macross/main/install.sh | bash
```

Or from a local checkout:

```bash
bash install.sh
```

## Quick start

```bash
mx
mx add-host
mx doctor
mx
```

## What `mx` does

- first run: initializes `~/.macross/`
- if no hosts exist: tells you to run `mx add-host`
- if hosts exist: enters the interactive shell

## Commands

```bash
mx
mx init
mx doctor
mx add-host
mx hosts
mx shell
mx version
```

## Interactive shell

```text
mx> hostname
mx> focus mac2
mac2> uptime
mac2> all
mx> only mac1 mac3
[mac1,mac3]> sw_vers
```

Built-ins:

- `hosts`
- `targets`
- `groups`
- `use <group>`
- `focus <host>`
- `only <host...>`
- `all`
- `mode`
- `inventory`
- `!<local command>`
- `help`
- `exit`

## Config

Macross stores user data in:

```text
~/.macross/
├── config.toml
├── inventory.ini
├── logs/
├── backups/
└── examples/
```

You can use `mx add-host`, or edit `~/.macross/inventory.ini` directly.

## Doctor

`mx doctor` checks:

- local environment (`python3`, `ssh`, `ansible`)
- config files
- host reachability
- SSH connectivity
- key-based auth status
- ansible ping

## Safety

In broadcast mode, Macross asks for confirmation before a small set of obviously dangerous commands, such as:

- `rm -rf`
- `reboot`
- `shutdown`
- `dd`
- `diskutil eraseDisk`

## Scope

Macross is:
- a multi-Mac CLI shell
- good for personal setups and small machine groups

Macross is not:
- MDM
- remote desktop
- enterprise device management

## Development

This repo is intentionally small. The goal is to ship the core experience and keep maintenance light.
