[English](./README.md) | [简体中文](./README.zh-CN.md)

# Macross

**像使用一个 shell 一样控制多台 Mac。**

Macross 是一个面向终端的多 Mac 控制层。  
它底层使用 SSH + Ansible，但把它们包装成一个更简单的交互式 shell，让你不用在多台机器之间反复 SSH、开很多窗口、记很多长命令。

## 为什么是 Macross

如果你手里有 2–10 台 Mac，想用一种更轻、更直接的方式管理它们，Macross 正好处在手动 SSH 和重型设备管理平台之间。

用 Macross，你可以：

- 一条命令同时发到多台 Mac
- 在 shell 里随时切到单台机器
- 只操作某几个指定机器
- 用一条命令检查 SSH 和连通性问题
- 想手动改配置时，仍然可以直接编辑 inventory 文件

## 它的特点

### 1. 真正偏 shell 的体验
Macross 更像“进入一个多机 shell”，而不是去记一堆零散自动化命令。

```text
mx> hostname
mx> focus mac2
mac2> uptime
mac2> all
mx> only mac1 mac3
[mac1,mac3]> sw_vers
```

### 2. 对真实用户友好
第一次运行 `mx` 会自动初始化工作目录。  
不要求用户一上来就先理解 Ansible。

### 3. 专为小规模 Mac 机器组设计
Macross 很适合：

- 你自己的几台 Mac
- 一桌子的 Mac mini / MacBook Air
- 小实验室
- 个人级别的轻量控制平面

### 4. 底层依然透明
Macross 不会把一切都藏进私有格式里。  
如果你愿意，仍然可以直接查看和编辑 inventory。

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/moolean/macross/main/install.sh | bash
```

或者在本地仓库里执行：

```bash
bash install.sh
```

如果 `~/.local/bin` 还没有在你的 PATH 中，请加上：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## 快速开始

```bash
mx
mx add-host
mx doctor
mx
```

### `mx` 的首次运行行为

当你执行 `mx` 时：

- 如果 Macross 还没初始化，会自动创建 `~/.macross/`
- 如果还没有主机，会提示你下一步怎么做
- 如果已经配置了主机，会直接进入交互 shell

## 核心命令

```bash
mx              # 启动 Macross
mx init         # 重新运行初始化
mx doctor       # 检查本地环境和远程主机
mx add-host     # 交互式添加一台主机
mx hosts        # 查看已配置主机
mx shell        # 显式进入 shell
mx version      # 查看版本
```

## 交互 shell

配置好主机后，`mx` 会进入一个多机 shell。

### 对全部主机广播命令

```text
mx> hostname
mx> uptime
```

### 切到单台机器

```text
mx> focus mac2
mac2> pwd
mac2> hostname
```

### 只操作某几个主机

```text
mx> only mac1 mac3
[mac1,mac3]> sw_vers
```

### 切回全部主机

```text
[mac1,mac3]> all
mx>
```

## shell 内建命令

在 shell 里支持这些内建命令：

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

除此之外，其他输入默认都会被当作远程 shell 命令执行。

## 输出体验

Macross 追求的是清晰，而不是花哨。

- 输出按主机分块
- 每台机器用颜色区分
- 错误会明确标出来
- 每条命令最后有 summary 汇总

例如：

```text
[mac1] OK
60328160M

[mac2] OK
60328370M

Summary: 2 succeeded, 0 failed, 2 total
```

## Doctor 模式

`mx doctor` 是最快看清问题出在哪的方式。

它会检查：

- `python3`
- `ssh`
- `ansible`
- Macross 配置文件
- 主机是否可达
- SSH 是否连通
- 是否已配置免密
- ansible ping 是否通过

所以它既适合首次配置，也适合后续排障。

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

你可以：

- 使用 `mx add-host`
- 或者直接手动编辑 `~/.macross/inventory.ini`

## 安全策略

在广播模式下，Macross 会对少数明显危险的命令做确认，例如：

- `rm -rf`
- `reboot`
- `shutdown`
- `dd`
- `diskutil eraseDisk`

目标不是限制高级用户，而是防止明显的多机误操作。

## Macross 是什么

- 一个多 Mac CLI shell
- 一个适合小规模机器组的轻量控制平面
- 安装快、解释成本低、容易交给别人直接用

## Macross 不是什么

- 不是 MDM
- 不是远程桌面
- 不是企业级设备管理平台
- 不是完整的编排系统替代品

## 最适合谁

如果你想：

- 管理同一网络下的几台 Mac
- 保留简单的 SSH 工作流
- 不想为了同一条命令开 4 个终端
- 想把一个轻量工具交给别人用，而不用先教 Ansible

那 Macross 就很适合。

## 项目状态

Macross 当前是 **alpha**。  
目标很简单：把核心体验做好，修 bug，保持项目轻量。
