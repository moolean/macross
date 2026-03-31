[English](./README.md) | [简体中文](./README.zh-CN.md)

# Macross

**Control multiple Macs like one shell.**

Macross is a terminal-first control layer for small groups of Macs.  
It uses SSH + Ansible under the hood, then wraps them in a simpler interactive shell so you can operate multiple machines without juggling multiple windows or remembering long commands.

## Why Macross

If you have 2–10 Macs and want them to feel easier to manage, Macross gives you a clean middle ground between manual SSH and heavyweight device management.

With Macross, you can:

- run one command across multiple Macs
- focus on one Mac without leaving the shell
- target only a subset of machines
- diagnose connectivity and SSH issues with one command
- keep using plain inventory files when you want full control

## What makes it different

### 1. Shell-first experience
Macross is designed to feel like entering a shell, not running a pile of one-off automation commands.

```text
mx> hostname
mx> focus mac2
mac2> uptime
mac2> all
mx> only mac1 mac3
[mac1,mac3]> sw_vers
```

### 2. Simple setup for real users
On first launch, `mx` initializes your workspace automatically.
You do not need to understand Ansible before getting started.

### 3. Built for small Mac fleets
Macross is ideal for:

- your own machines
- a desk full of Mac minis or MacBook Airs
- a small lab
- a lightweight personal control plane

### 4. Still transparent underneath
Macross does not hide everything behind a proprietary format.
You can still inspect and edit your inventory directly.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/moolean/macross/main/install.sh | bash
```

Or from a local checkout:

```bash
bash install.sh
```

If `~/.local/bin` is not already on your PATH, add:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Quick start

```bash
mx
mx add-host
mx doctor
mx
```

### First run behavior

When you run `mx`:

- if Macross is not initialized yet, it sets up `~/.macross/`
- if no hosts are configured yet, it tells you what to do next
- if hosts already exist, it enters the interactive shell

## Core commands

```bash
mx              # start Macross
mx init         # run setup again
mx doctor       # check local environment + remote hosts
mx add-host     # add one host interactively
mx hosts        # list configured hosts
mx shell        # explicitly enter the shell
mx version      # show version
```

## Interactive shell

Once hosts are configured, `mx` drops you into a multi-machine shell.

### Broadcast to all hosts

```text
mx> hostname
mx> uptime
```

### Focus on one host

```text
mx> focus mac2
mac2> pwd
mac2> hostname
```

### Target only some hosts

```text
mx> only mac1 mac3
[mac1,mac3]> sw_vers
```

### Switch back to all hosts

```text
[mac1,mac3]> all
mx>
```

## Shell built-ins

Inside the shell, these commands are built in:

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

Everything else is treated as a remote shell command.

## Output model

Macross is built for clarity, not terminal gimmicks.

- output is grouped by host
- each host is color-coded
- failures are clearly marked
- every command ends with a short summary

Example:

```text
[mac1] OK
60328160M

[mac2] OK
60328370M

Summary: 2 succeeded, 0 failed, 2 total
```

## Doctor mode

`mx doctor` is the fastest way to understand what is broken.

It checks:

- `python3`
- `ssh`
- `ansible`
- Macross config files
- host reachability
- SSH connectivity
- key-based auth status
- ansible ping

This makes it useful both for setup and for support.

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

You can:

- use `mx add-host`
- or edit `~/.macross/inventory.ini` directly

## Safety

In broadcast mode, Macross asks for confirmation before a small set of obviously dangerous commands, such as:

- `rm -rf`
- `reboot`
- `shutdown`
- `dd`
- `diskutil eraseDisk`

The goal is not to block power users. It is to prevent obvious multi-host mistakes.

## What Macross is

- a multi-Mac CLI shell
- a lightweight control plane for small machine groups
- fast to install and easy to explain

## What Macross is not

- MDM
- remote desktop
- enterprise device management
- a replacement for full orchestration platforms

## Best fit

Macross is a strong fit if you want to:

- manage several Macs on the same network
- keep a simple SSH-based workflow
- avoid opening four terminals just to run the same command
- hand a small tool to other users without teaching them Ansible first

## Project status

Macross is currently **alpha**.
The goal is simple: ship the core experience, fix bugs, and keep the project small.
