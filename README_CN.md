# Uni Dashboard

统一入口门户 - 将多个 Web UI 整合到单一端口，支持密码保护和动态入口管理。支持 SSH 映射和公网访问两种模式。

## 背景

在远程服务器部署 OpenClaw 时，多个 Web UI 分布在不同端口：
- **Gateway Dashboard**（端口 18789）- 会话管理、日志、配置
- **Memory Viewer**（端口 18799）- 记忆搜索和管理
- 其他服务...

**痛点：**
- SSH 端口转发一次只能映射一个端口
- 访问多个服务需要开多个 SSH 隧道
- 直接公网暴露缺乏认证保护

**解决方案：** Uni Dashboard 提供统一入口：
- 映射一个端口即可访问所有 Web UI
- 支持 SSH 映射模式（安全）和公网访问模式（便捷）
- 添加密码保护确保安全
- 支持动态入口管理，无需修改代码

## 功能特点

- 🚀 **单端口访问** - 一个端口搞定所有 Web UI
- 🔐 **密码保护** - 首次访问设置密码，后续验证
- 🌐 **双模式支持** - SSH 映射（默认）或公网访问
- ➕ **动态入口** - 通过界面添加/删除服务入口
- 🎨 **现代界面** - 简洁优雅的服务卡片
- 🍪 **会话持久** - 7 天 Cookie 免登录
- ⚡ **轻量实现** - 基于 FastAPI，依赖极少

---

## 安装

### 环境要求

- Python 3.9+
- pip

### 安装依赖

```bash
pip install fastapi uvicorn httpx
```

### 下载

```bash
git clone https://github.com/enzowyf/uni-dashboard.git
cd uni-dashboard
```

---

## 部署

### 方式一：一键部署（推荐）

使用部署脚本：

```bash
# SSH 映射模式（默认）
sudo bash deploy.sh

# 公网访问模式
sudo bash deploy.sh public
```

### 方式二：手动运行

直接运行，不使用 systemd：

```bash
# SSH 映射模式
python server.py

# 公网访问模式
python server.py --public

# 自定义端口
python server.py --port 8080
```

### 方式三：系统服务

安装为系统服务：

```bash
# 复制服务文件
sudo cp uni-dashboard.service /etc/systemd/system/

# 启用并启动
sudo systemctl daemon-reload
sudo systemctl enable uni-dashboard
sudo systemctl start uni-dashboard

# 查看状态
sudo systemctl status uni-dashboard
```

---

## 访问

### SSH 映射模式

```bash
# 本地创建 SSH 隧道
ssh -L 18780:localhost:18780 user@server

# 浏览器访问
http://localhost:18780
```

### 公网访问模式

```bash
# 浏览器直接访问
http://公网IP:18780
```

---

## 模式对比

| 模式 | 监听地址 | 访问方式 | 安全性 |
|------|---------|---------|--------|
| SSH 映射 | `127.0.0.1` | SSH 端口转发 | ✅ 最安全 |
| 公网访问 | `0.0.0.0` | 直接公网 IP | ⚠️ 需密码 |

**注意**：两种模式打开页面后流程完全一致，都需要输入密码。

---

## 动态入口管理

### 添加入口
1. 在门户页面点击"➕ 添加入口"按钮
2. 输入入口名称（如：Grafana）
3. 输入端口号（如：3000）
4. 输入描述（可选）
5. 点击"添加"保存

### 删除入口
- 鼠标悬停在非默认入口上，显示 × 按钮
- 点击 × 删除（默认入口无删除按钮）

---

## 配置

编辑 `config.json` 自定义配置：

```json
{
  "port": 18780,
  "host": "127.0.0.1",
  "cookie_expire_days": 7,
  "entries": [
    {
      "key": "gateway",
      "name": "Gateway Dashboard",
      "url": "http://localhost:18789",
      "desc": "网关控制面板 - 管理会话、查看日志、配置服务",
      "is_default": true
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| `port` | 门户端口（默认：18780） |
| `host` | SSH 模式默认监听地址（默认：127.0.0.1） |
| `cookie_expire_days` | Session 有效期（天） |
| `entries` | 入口列表 |
| `entries[].key` | 入口唯一标识 |
| `entries[].name` | 显示名称 |
| `entries[].url` | 目标地址 |
| `entries[].desc` | 描述 |
| `entries[].is_default` | 是否为默认入口（不可删除） |

---

## 故障排查

```bash
# 查看状态
systemctl status uni-dashboard

# 查看日志
journalctl -u uni-dashboard -f

# 检查端口
ss -tlnp | grep 18780

# 重启服务
sudo systemctl restart uni-dashboard

# 查看保存的入口
cat /opt/uni-dashboard/data/services.json
```

---

## 技术栈

- **后端**: FastAPI + uvicorn
- **HTTP 客户端**: httpx
- **认证**: SHA256 哈希 + UUID 令牌
- **存储**: JSON 文件（无需数据库）

---

## 更新日志

### v1.1.0
- ➕ 动态入口管理（通过界面添加/删除）
- 🔒 Gateway Dashboard 作为默认不可删除入口
- 💾 配置持久化存储
- 📝 列表式配置格式

### v1.0.0
- 初始版本
- SSH 映射和公网访问模式
- 密码保护

---

## 许可证

[MIT 许可证](LICENSE)

## 作者

Enzo（骁骑）- CTO @ Enzo