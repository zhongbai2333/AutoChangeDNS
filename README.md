# AutoChangeDNS

AutoChangeDNS 是一个基于 Python 的自动化故障切换工具，用于实时监控主服务器的丢包率并在网络质量下降时，自动修改阿里云 DNS 记录指向备用服务器，网络恢复后再切回主服务器。

## 目录

* [功能特性](#功能特性)
* [架构设计](#架构设计)
* [安装与依赖](#安装与依赖)
* [配置说明](#配置说明)
* [快速开始](#快速开始)
* [模块说明](#模块说明)
* [示例](#示例)
* [贡献与反馈](#贡献与反馈)
* [许可证](#许可证)

---

## 功能特性

* **实时丢包监控**：通过 `ping` 命令循环检测目标主机丢包率，并计算滑动窗口内的丢包百分比。
* **自动故障切换**：当丢包率超过阈值时，调用阿里云 API 切换 DNS 记录至 `failover_ip`；当恢复时再切回 `server_ip`。
* **泛解析支持**：若配置 `rr="*"`，同时更新根记录 `@`，保证主域名生效。
* **灵活配置**：使用 Pydantic 定义 `config.yaml`，支持类型校验与自动补全。
* **轻量依赖**：仅需少量第三方库即可运行。

---

## 架构设计

```txt
auto_change_dns/
├─ base_system/          # 全局上下文、日志与存储
│   ├ __init__.py
│   ├ context.py         # 读取配置、初始化日志 & 存储
│   ├ log_system.py      # 日志封装
│   └ storage_system.py  # 可选：持久化切换状态
├─ network_system/       # 核心网络与 DNS 操作
│   ├ change_dns.py      # 调用阿里云 SDK 更新 DNS
│   ├ while_ping.py      # 跨平台丢包率监控
│   └ __init__.py
└─ config.yaml           # 用户自定义配置
```

该设计将**配置**、**监控**、**DNS 更新**解耦，每部分各司其职，便于维护和扩展。

---

## 安装与依赖

1. 克隆仓库

   ```bash
   git clone https://github.com/YourUser/AutoChangeDNS.git
   cd AutoChangeDNS
   ```

2. 创建并激活虚拟环境（可选）

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```

   * `aliyun-python-sdk-core`、`aliyun-python-sdk-alidns20150109`：阿里云 DNS 操作 SDK
   * `pydantic`：配置模型与校验

---

## 配置说明

在根目录编辑 `config.yaml`，示例：

```yaml
server_ip:        xxx.xxx.xxx.xxx   # 主服务器 IP
check_time:       60                # 检测窗口（秒）
failover_threshold: 20              # 丢包阈值（%）
failover_ip:      xxx.xxx.xxx.xxx   # 备用服务器 IP

domain:           example.com       # 域名
rr:               www               # 记录前缀，泛解析用 "*"
record_type:      A
ttl:              600               # DNS TTL

ali_access_key_id:     YOUR_KEY_ID   # 阿里云 RAM 凭证
ali_access_key_secret: YOUR_KEY_SECRET
```

Pydantic 会在启动时进行字段验证，确保配置合法。

---

## 快速开始

```bash
# 启动程序
python main.py
```

* 日志会显示每个窗口的丢包率；
* 丢包率超阈值时自动切换 DNS，并记录切换状态；
* 网络恢复时自动回切。

---

## 模块说明

### `while_ping.py`

采用滑动窗口技术，每 `check_time` 秒内循环 `ping`，统计丢包率并返回一个数值。

### `change_dns.py`

封装了 `AcsClient` 与 `AddDomainRecord`/`UpdateDomainRecord` 操作，调用阿里云 DNS API 实现记录的增删改查。

### `context.py`

负责全局单例上下文：读取 `config.yaml`、初始化日志、持久化存储等。

---

## 示例

```bash
# 第一次运行，网络正常，输出：
[2025-06-20 10:00:00] 60s 窗口: 共发 60 包，丢 0 包，丢包率 0.00%

# 模拟丢包率 30%，超过阈值 20%，切换 DNS：
[2025-06-20 10:01:00] 60s 窗口: 共发 60 包，丢 18 包，丢包率 30.00%
WARNING: Loss rate exceeded threshold; switching DNS → failover_ip

# 网络恢复，丢包率 < 20%，自动回切：
[2025-06-20 10:02:00] 60s 窗口: 共发 60 包，丢 5 包，丢包率 8.33%
WARNING: Loss rate recovered; switching DNS → server_ip
```

---

## 贡献与反馈

* 欢迎提交 Issues 与 PR；
* 若需扩展或支持其他 DNS 提供商，可在 `network_system/change_dns.py` 中添加新实现；

---

## 许可证

本项目采用 GPLv3 许可证，详见 [LICENSE](LICENSE) 文件。
