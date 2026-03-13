# Uni Dashboard

OpenClaw exposes multiple web UIs on different ports (Gateway Dashboard: 18789, Memory Viewer: 18799, etc.). SSH port forwarding only maps one port at a time, making multi-service access inconvenient. Uni Dashboard provides a unified portal for all web UIs with password protection, supporting SSH tunneling, public access modes, and dynamic entry management.

## Features

- 🚀 **Single Port Access** - One port for all web UIs
- 🔐 **Password Protection** - First-time setup, subsequent verification
- 🌐 **Dual Mode Support** - SSH tunneling (default) or public access
- ➕ **Dynamic Entries** - Add/remove service entries via UI
- 🎨 **Modern UI** - Clean interface with service cards
- 🍪 **Session Persistence** - 7-day cookie-based authentication
- ⚡ **Lightweight** - FastAPI-based, minimal dependencies

---

## Installation

### Requirements

- Python 3.9+
- pip

### Install Dependencies

```bash
pip install fastapi uvicorn httpx
```

### Download

```bash
git clone https://github.com/enzowyf/uni-dashboard.git
cd uni-dashboard
```

---

## Deployment

### Option 1: Quick Deploy (Recommended)

```bash
# SSH tunneling mode (default)
sudo bash deploy.sh

# Public access mode
sudo bash deploy.sh public
```

### Option 2: Manual Run

```bash
# SSH tunneling mode
python src/server.py

# Public access mode
python src/server.py --public

# Custom port
python src/server.py --port 8080
```

### Option 3: Systemd Service

```bash
sudo cp uni-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable uni-dashboard
sudo systemctl start uni-dashboard
```

---

## Access

### 🖥️ 本机部署 (Local Deployment)

如果 Uni Dashboard 部署在**本机**，直接通过 `localhost` 访问，**无需 SSH 映射**。

```bash
# 1. 启动服务（本机监听）
python src/server.py --public
# 或指定端口
python src/server.py --public --port 18780

# 2. 直接访问
# 浏览器打开：http://localhost:18780
# 或：http://127.0.0.1:18780
```

**前提条件：**
- 服务需监听 `0.0.0.0` 或 `127.0.0.1`
- 本地防火墙允许对应端口
- 端口未被其他程序占用

---

### 🔐 SSH Tunneling Mode (Default)

**Step 1: Create SSH tunnel on your local machine**
```bash
ssh -L 18780:localhost:18780 user@server
```

**Step 2: Open browser**
```
http://localhost:18780
```

**How it works:**
- `-L 18780:localhost:18780` forwards local port 18780 to server's localhost:18780
- Server listens on `127.0.0.1:18780` (not exposed to public)
- Traffic is encrypted via SSH tunnel

**Tip:** Add to `~/.ssh/config` for convenience:
```
Host myserver
    HostName 43.139.54.146
    User root
    LocalForward 18780 localhost:18780
```
Then just `ssh myserver` to connect with tunnel.

---

### 🔀 多端口 SSH 映射 (Multi-Port SSH Forwarding)

当需要同时访问服务器上**多个服务**时，可以一次性映射多个端口。

#### 方法一：单条命令映射多个端口

```bash
# 使用多个 -L 参数
ssh -L 18780:localhost:18780 \
    -L 18789:localhost:18789 \
    -L 18799:localhost:18799 \
    user@server

# 映射后访问：
# http://localhost:18780  (Uni Dashboard)
# http://localhost:18789  (Gateway Dashboard)
# http://localhost:18799  (Memory Viewer)
```

#### 方法二：SSH 配置文件（推荐）

编辑 `~/.ssh/config`：

```bash
Host myserver
    HostName your-server-ip
    User your-username
    # Uni Dashboard
    LocalForward 18780 localhost:18780
    # Gateway Dashboard
    LocalForward 18789 localhost:18789
    # Memory Viewer
    LocalForward 18799 localhost:18799
    # 保持连接
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

使用配置：
```bash
# 只需输入
ssh myserver

# 所有端口自动映射完成！
```

#### 方法三：后台持久化映射

```bash
# 使用 autossh 保持连接持久（需先安装：apt install autossh）
autossh -M 0 -f -N \
  -L 18780:localhost:18780 \
  -L 18789:localhost:18789 \
  -L 18799:localhost:18799 \
  user@server
```

#### 常用端口参考

| 本地端口 | 远程端口 | 服务 | 访问地址 |
|---------|---------|------|---------|
| 18780 | 18780 | Uni Dashboard | http://localhost:18780 |
| 18789 | 18789 | Gateway Dashboard | http://localhost:18789 |
| 18799 | 18799 | Memory Viewer | http://localhost:18799 |

#### 常用 SSH 参数

| 参数 | 说明 |
|-----|------|
| `-L` | 本地端口转发 (Local Forward) |
| `-N` | 不执行远程命令，仅转发 |
| `-f` | 后台运行 |
| `-C` | 启用压缩 |
| `-v` | 详细模式（调试用） |

```bash
# 完整示例：后台 + 压缩 + 不执行命令
ssh -f -N -C -L 18780:localhost:18780 user@server
```

### Public Access Mode

```bash
# Open browser directly
http://your-public-ip:18780
```

**Requires:** Cloud security group allows TCP:18780

---

## Modes Comparison

| Mode | Listen Address | Access Method | Security |
|------|---------------|---------------|----------|
| SSH Tunneling | `127.0.0.1` | SSH port forwarding | ✅ Most secure |
| Public Access | `0.0.0.0` | Direct public IP | ⚠️ Password required |

---

## Dynamic Entry Management

### Add Entry
1. Click "➕ Add Entry" button
2. Enter name, port, description
3. Click "Add"

### Delete Entry
- Hover over non-default entries, click ×

---

## Configuration

Edit `config.json`:

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

## ❓ 常见问题 (FAQ)

### Q1: 本机部署后无法访问？

```bash
# 检查服务是否启动
netstat -tlnp | grep 18780

# 检查防火墙
sudo ufw status
sudo ufw allow 18780/tcp  # 如需开放

# 确保使用 --public 参数启动
python src/server.py --public
```

### Q2: SSH 隧道连接后立刻断开？

```bash
# 添加保持连接参数
ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=3 \
    -L 18780:localhost:18780 user@server
```

### Q3: 提示端口已被占用？

```bash
# 查看占用端口的进程
lsof -i :18780
# 或
netstat -tlnp | grep 18780

# 解决方案：
# 1. 关闭占用端口的进程
# 2. 或更换端口启动
python src/server.py --port 8080
```

### Q4: 如何查看已建立的 SSH 隧道？

```bash
# 查看 SSH 进程
ps aux | grep ssh

# 查看端口监听
netstat -tlnp | grep 18780
```

### Q5: 如何关闭 SSH 隧道？

```bash
# 找到进程 ID 后终止
kill <PID>

# 或前台运行时按 Ctrl+C
```

---

## Troubleshooting

### Environment Issues

**1. Missing dependency: python-multipart**
```
RuntimeError: Form data requires "python-multipart" to be installed.
```
Fix: 
```bash
pip install python-multipart
```

**2. Port already in use**
```
OSError: [Errno 98] Address already in use
```
Fix: 
```bash
# Check what's using the port
netstat -tlnp | grep 18780
# Kill process or change port in config.json
```

**3. Permission denied**
```
PermissionError: [Errno 13] Permission denied: '/opt/uni-dashboard/data'
```
Fix:
```bash
sudo mkdir -p /opt/uni-dashboard/data
sudo chown $USER:$USER /opt/uni-dashboard/data
```

### Configuration Issues

**4. Invalid config.json**
```bash
# Validate JSON syntax
python3 -c "import json; json.load(open('config.json'))"
```

**5. Service won't start**
```bash
# Check logs
journalctl -u uni-dashboard -n 50

# Restart service
sudo systemctl restart uni-dashboard
```

---

## License

[MIT License](LICENSE)