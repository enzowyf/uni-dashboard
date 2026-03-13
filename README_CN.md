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

### 🖥️ 本机部署

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

### 🔐 SSH 映射模式（默认）

**步骤 1：在本地电脑创建 SSH 隧道**
```bash
ssh -L 18780:localhost:18780 user@server
```

**步骤 2：浏览器访问**
```
http://localhost:18780
```

**原理：**
- `-L 18780:localhost:18780` 将本地 18780 端口转发到服务器的 localhost:18780
- 服务器监听 `127.0.0.1:18780`（不暴露公网）
- 流量通过 SSH 隧道加密传输

**技巧：** 添加到 `~/.ssh/config` 简化操作：
```
Host myserver
    HostName 43.139.54.146
    User root
    LocalForward 18780 localhost:18780
```
之后只需 `ssh myserver` 即可连接并建立隧道。

---

### 🔀 多端口 SSH 映射

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

### 公网访问模式

```bash
# 浏览器直接访问
http://公网 IP:18780
```

**前提：** 云安全组已开放 TCP:18780 端口

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

## 故障排查

### 环境问题

**1. 缺少依赖：python-multipart**
```
RuntimeError: Form data requires "python-multipart" to be installed.
```
解决：
```bash
pip install python-multipart
```

**2. 端口被占用**
```
OSError: [Errno 98] Address already in use
```
解决：
```bash
# 查看端口占用
netstat -tlnp | grep 18780
# 终止进程或修改 config.json 中的端口
```

**3. 权限不足**
```
PermissionError: [Errno 13] Permission denied: '/opt/uni-dashboard/data'
```
解决：
```bash
sudo mkdir -p /opt/uni-dashboard/data
sudo chown $USER:$USER /opt/uni-dashboard/data
```

### 配置问题

**4. config.json 格式错误**
```bash
# 验证 JSON 语法
python3 -c "import json; json.load(open('config.json'))"
```

**5. 服务无法启动**
```bash
# 查看日志
journalctl -u uni-dashboard -n 50

# 重启服务
sudo systemctl restart uni-dashboard
```

---

## 许可证

[MIT 许可证](LICENSE)
