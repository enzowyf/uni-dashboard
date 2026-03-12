# Uni Dashboard

A unified portal for multiple web UIs with password protection. Supports SSH tunneling, public access modes, and dynamic entry management.

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

Use the deployment script:

```bash
# SSH tunneling mode (default)
sudo bash deploy.sh

# Public access mode
sudo bash deploy.sh public
```

### Option 2: Manual Deploy

Run directly without systemd:

```bash
# SSH tunneling mode
python server.py

# Public access mode
python server.py --public

# Custom port
python server.py --port 8080
```

### Option 3: Systemd Service

Install as a system service:

```bash
# Copy service file
sudo cp uni-dashboard.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable uni-dashboard
sudo systemctl start uni-dashboard

# Check status
sudo systemctl status uni-dashboard
```

---

## Access

### SSH Tunneling Mode

```bash
# Create SSH tunnel on your local machine
ssh -L 18780:localhost:18780 user@server

# Open browser
http://localhost:18780
```

### Public Access Mode

```bash
# Open browser directly
http://your-public-ip:18780
```

---

## Modes Comparison

| Mode | Listen Address | Access Method | Security |
|------|---------------|---------------|----------|
| SSH Tunneling | `127.0.0.1` | SSH port forwarding | ✅ Most secure |
| Public Access | `0.0.0.0` | Direct public IP | ⚠️ Password required |

**Note:** Both modes require password verification after opening the page.

---

## Dynamic Entry Management

### Add Entry
1. Click "➕ Add Entry" button on the portal page
2. Enter entry name (e.g., "Grafana")
3. Enter port number (e.g., 3000)
4. Enter description (optional)
5. Click "Add" to save

### Delete Entry
- Hover over non-default entries to reveal the × button
- Click × to delete (default entry cannot be deleted)

---

## Configuration

Edit `config.json` to customize:

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

| Field | Description |
|-------|-------------|
| `port` | Portal port (default: 18780) |
| `host` | Default host for SSH mode (default: 127.0.0.1) |
| `cookie_expire_days` | Session validity in days |
| `entries` | List of service entries |
| `entries[].key` | Unique identifier for the entry |
| `entries[].name` | Display name |
| `entries[].url` | Target URL |
| `entries[].desc` | Description |
| `entries[].is_default` | If true, cannot be deleted |

---

## Troubleshooting

```bash
# Check status
systemctl status uni-dashboard

# View logs
journalctl -u uni-dashboard -f

# Check port
ss -tlnp | grep 18780

# Restart service
sudo systemctl restart uni-dashboard

# View saved entries
cat /opt/uni-dashboard/data/services.json
```

---

## Tech Stack

- **Backend**: FastAPI + uvicorn
- **HTTP Client**: httpx
- **Authentication**: SHA256 hashing + UUID tokens
- **Storage**: JSON files (no database required)

---

## Changelog

### v1.1.0
- ➕ Dynamic entry management (add/remove via UI)
- 🔒 Gateway Dashboard as default non-deletable entry
- 💾 Persistent configuration storage
- 📝 List-based config format

### v1.0.0
- Initial release
- SSH tunneling and public access modes
- Password protection

---

## License

[MIT License](LICENSE)

## Author

Enzo (骁骑) - CTO @ Enzo