# Uni Dashboard

统一入口门户 - 将多个 Web UI 整合到单一端口，支持密码保护。支持 SSH 映射和公网访问两种模式。

## 功能特点

- 🚀 **单端口访问** - 一个端口搞定所有 Web UI
- 🔐 **密码保护** - 首次访问设置密码，后续验证
- 🌐 **双模式支持** - SSH 映射（默认）或公网访问
- 🎨 **现代界面** - 简洁优雅的服务卡片
- 🍪 **会话持久** - 7 天 Cookie 免登录
- ⚡ **轻量实现** - 基于 FastAPI，依赖极少

## 快速开始

### SSH 映射模式（默认，推荐）

```bash
# 克隆并部署
git clone https://github.com/enzowyf/uni-dashboard.git
cd uni-dashboard
sudo bash deploy.sh

# 本地创建 SSH 隧道
ssh -L 18780:localhost:18780 user@server

# 浏览器访问
http://localhost:18780
```

### 公网访问模式

```bash
# 克隆并部署
git clone https://github.com/enzowyf/uni-dashboard.git
cd uni-dashboard
sudo bash deploy.sh public

# 浏览器访问
http://公网IP:18780
```

## 模式对比

| 模式 | 监听地址 | 访问方式 | 安全性 |
|------|---------|---------|--------|
| SSH 映射 | `127.0.0.1` | SSH 端口转发 | ✅ 最安全 |
| 公网访问 | `0.0.0.0` | 直接公网 IP | ⚠️ 需密码 |

**注意**：两种模式打开页面后流程完全一致，都需要输入密码。

## 页面流程

```
首次访问                          后续访问
   │                                │
   ▼                                ▼
设置密码页 ──────────────────────▶ 登录页
   │                                │
   │ 输入密码 + 确认                 │ 输入密码
   ▼                                ▼
入口页 ◀──────────────────────── 入口页
   │
   ├─→ Gateway Dashboard
   └─→ Memory Viewer
```

## 配置说明

编辑 `server.py` 自定义配置：

```python
PORT = 18780                    # 门户端口
GATEWAY_URL = "http://localhost:18789"   # Gateway Dashboard
MEMORY_URL = "http://localhost:18799"    # Memory Viewer
COOKIE_EXPIRE_DAYS = 7          # Cookie 有效期
PASSWORD_FILE = "/opt/uni-dashboard/.password"
```

## 扩展服务

编辑 `server.py` 中的 `SERVICES` 字典：

```python
SERVICES = {
    "gateway": {...},
    "memory": {...},
    "grafana": {
        "name": "Grafana",
        "url": "http://localhost:3000",
        "icon": "📊",
        "desc": "监控面板",
        "color": "#f46800"
    }
}
```

## 端口规划

| 服务 | 端口 |
|------|------|
| Uni Dashboard | 18780 |
| Gateway Dashboard | 18789 |
| Memory Viewer | 18799 |

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
```

## 技术栈

- **后端**: FastAPI + uvicorn
- **HTTP 客户端**: httpx
- **认证**: SHA256 哈希 + UUID 令牌

## 许可证

[MIT 许可证](LICENSE)

## 作者

Enzo（骁骑）- CTO @ Enzo