[English](./README.md) | [简体中文](./README.zh-CN.md)

# Macross

**像使用一个 shell 一样控制多台 Mac。**

Macross 是一个面向终端的多 Mac 控制工具。它用 SSH + Ansible 做底层，把多机控制包装成更顺手的交互式 shell，让你不用开一堆终端窗口。

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/moolean/macross/main/install.sh | bash
```

或者在本地仓库里执行：

```bash
bash install.sh
```

## 快速开始

```bash
mx
mx add-host
mx doctor
mx
```

## `mx` 的默认行为

- 第一次运行：初始化 `~/.macross/`
- 如果还没有主机：提示你先运行 `mx add-host`
- 如果已经有主机：进入交互 shell

## 命令

```bash
mx
mx init
mx doctor
mx add-host
mx hosts
mx shell
mx version
```

## 交互 shell

```text
mx> hostname
mx> focus mac2
mac2> uptime
mac2> all
mx> only mac1 mac3
[mac1,mac3]> sw_vers
```

内建命令：

- `hosts`
- `targets`
- `groups`
- `use <group>`
- `focus <host>`
- `only <host...>`
- `all`
- `mode`
- `inventory`
- `!<本地命令>`
- `help`
- `exit`

## 配置目录

Macross 把用户数据放在：

```text
~/.macross/
├── config.toml
├── inventory.ini
├── logs/
├── backups/
└── examples/
```

你可以使用 `mx add-host`，也可以直接手动编辑 `~/.macross/inventory.ini`。

## Doctor 检查内容

`mx doctor` 会检查：

- 本地环境（`python3`、`ssh`、`ansible`）
- 配置文件
- 主机是否可达
- SSH 连通性
- 是否已配置免密
- ansible ping 是否通过

## 安全策略

在广播模式下，Macross 会对少数明显危险的命令做确认，例如：

- `rm -rf`
- `reboot`
- `shutdown`
- `dd`
- `diskutil eraseDisk`

## 这是什么 / 不是什么

Macross 是：
- 多 Mac 的 CLI shell
- 适合个人和小规模机器组

Macross 不是：
- MDM
- 远程桌面
- 企业级设备管理平台

## 开发说明

这个仓库会保持很轻。目标是把核心体验做完整，后续主要是修 bug 和少量优化。
