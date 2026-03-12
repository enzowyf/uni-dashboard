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

### SSH Tunneling Mode

```bash
ssh -L 18780:localhost:18780 user@server
# Open http://localhost:18780
```

### Public Access Mode

```bash
# Open http://your-public-ip:18780
```

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