# Uni Dashboard

OpenClaw 的多个 Web UI 分布在不同端口（Gateway Dashboard: 18789, Memory Viewer: 18799 等），SSH 端口转发一次只能映射一个端口，访问不便。Uni Dashboard 提供统一入口门户，支持密码保护、SSH 映射、公网访问和动态入口管理。

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

```bash
# SSH 映射模式（默认）
sudo bash deploy.sh

# 公网访问模式
sudo bash deploy.sh public
```

### 方式二：手动运行

```bash
# SSH 映射模式
python src/server.py

# 公网访问模式
python src/server.py --public

# 自定义端口
python src/server.py --port 8080
```

### 方式三：系统服务

```bash
sudo cp uni-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable uni-dashboard
sudo systemctl start uni-dashboard
```

---

## 访问

### SSH 映射模式

```bash
ssh -L 18780:localhost:18780 user@server
# 访问 http://localhost:18780
```

### 公网访问模式

```bash
# 访问 http://公网IP:18780
```

---

## 模式对比

| 模式 | 监听地址 | 访问方式 | 安全性 |
|------|---------|---------|--------|
| SSH 映射 | `127.0.0.1` | SSH 端口转发 | ✅ 最安全 |
| 公网访问 | `0.0.0.0` | 直接公网 IP | ⚠️ 需密码 |

---

## 动态入口管理

### 添加入口
1. 点击"➕ 添加入口"按钮
2. 输入名称、端口、描述
3. 点击"添加"

### 删除入口
- 鼠标悬停在非默认入口上，点击 ×

---

## 配置

编辑 `config.json`：

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
      "desc": "网关控制面板",
      "is_default": true
    }
  ]
}
```

---

## 故障排查

```bash
systemctl status uni-dashboard
journalctl -u uni-dashboard -f
ss -tlnp | grep 18780
```

---

## 许可证

[MIT 许可证](LICENSE)