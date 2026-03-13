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

### 🖥️ Local Deployment

If Uni Dashboard is deployed on your **local machine**, access directly via `localhost` without SSH tunneling.

```bash
# 1. Start service (local listening)
python src/server.py --public
# Or specify port
python src/server.py --public --port 18780

# 2. Access directly
# Open browser: http://localhost:18780
# Or: http://127.0.0.1:18780
```

**Prerequisites:**
- Service must listen on `0.0.0.0` or `127.0.0.1`
- Local firewall must allow the port
- Port must not be occupied by other processes

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

### 🔀 Multi-Port SSH Forwarding

When you need to access **multiple services** on the server simultaneously, you can forward multiple ports at once.

#### Method 1: Single Command with Multiple Ports

```bash
# Use multiple -L parameters
ssh -L 18780:localhost:18780 \
    -L 18789:localhost:18789 \
    -L 18799:localhost:18799 \
    user@server

# After forwarding, access:
# http://localhost:18780  (Uni Dashboard)
# http://localhost:18789  (Gateway Dashboard)
# http://localhost:18799  (Memory Viewer)
```

#### Method 2: SSH Config File (Recommended)

Edit `~/.ssh/config`:

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
    # Keep connection alive
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Usage:
```bash
# Just type
ssh myserver

# All ports are automatically forwarded!
```

#### Method 3: Persistent Background Forwarding

```bash
# Use autossh for persistent connection (install first: apt install autossh)
autossh -M 0 -f -N \
  -L 18780:localhost:18780 \
  -L 18789:localhost:18789 \
  -L 18799:localhost:18799 \
  user@server
```

#### Common Ports Reference

| Local Port | Remote Port | Service | Access URL |
|-----------|-------------|---------|------------|
| 18780 | 18780 | Uni Dashboard | http://localhost:18780 |
| 18789 | 18789 | Gateway Dashboard | http://localhost:18789 |
| 18799 | 18799 | Memory Viewer | http://localhost:18799 |

#### Common SSH Parameters

| Parameter | Description |
|-----------|-------------|
| `-L` | Local port forwarding |
| `-N` | Do not execute remote command, forwarding only |
| `-f` | Run in background |
| `-C` | Enable compression |
| `-v` | Verbose mode (for debugging) |

```bash
# Complete example: background + compression + forwarding only
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

## ❓ FAQ

### Q1: Cannot access after local deployment?

```bash
# Check if service is running
netstat -tlnp | grep 18780

# Check firewall
sudo ufw status
sudo ufw allow 18780/tcp  # If needed

# Ensure using --public parameter
python src/server.py --public
```

### Q2: SSH tunnel disconnects immediately?

```bash
# Add keep-alive parameters
ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=3 \
    -L 18780:localhost:18780 user@server
```

### Q3: Port already in use?

```bash
# Check process using the port
lsof -i :18780
# Or
netstat -tlnp | grep 18780

# Solutions:
# 1. Kill the process occupying the port
# 2. Or start with different port
python src/server.py --port 8080
```

### Q4: How to check established SSH tunnels?

```bash
# Check SSH processes
ps aux | grep ssh

# Check port listening
netstat -tlnp | grep 18780
```

### Q5: How to close SSH tunnel?

```bash
# Find PID and terminate
kill <PID>

# Or press Ctrl+C if running in foreground
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
