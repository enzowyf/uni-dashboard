# Uni Dashboard

A unified portal for multiple web UIs with password protection. Supports SSH tunneling and public access modes.

## Features

- 🚀 **Single Port Access** - One port for all web UIs
- 🔐 **Password Protection** - First-time setup, subsequent verification
- 🌐 **Dual Mode Support** - SSH tunneling (default) or public access
- 🎨 **Modern UI** - Clean interface with service cards
- 🍪 **Session Persistence** - 7-day cookie-based authentication
- ⚡ **Lightweight** - FastAPI-based, minimal dependencies

## Quick Start

### SSH Tunneling Mode (Default, Recommended)

```bash
# Clone and deploy
git clone https://github.com/enzowyf/uni-dashboard.git
cd uni-dashboard
sudo bash deploy.sh

# Create SSH tunnel on your local machine
ssh -L 18780:localhost:18780 user@server

# Open browser
http://localhost:18780
```

### Public Access Mode

```bash
# Clone and deploy
git clone https://github.com/enzowyf/uni-dashboard.git
cd uni-dashboard
sudo bash deploy.sh public

# Open browser
http://your-public-ip:18780
```

## Modes Comparison

| Mode | Listen Address | Access Method | Security |
|------|---------------|---------------|----------|
| SSH Tunneling | `127.0.0.1` | SSH port forwarding | ✅ Most secure |
| Public Access | `0.0.0.0` | Direct public IP | ⚠️ Password required |

**Note:** Both modes require password verification after opening the page.

## Page Flow

```
First Visit                          Subsequent Visits
   │                                        │
   ▼                                        ▼
Set Password ─────────────────────────▶ Login Page
   │                                        │
   │ Enter + Confirm                        │ Enter Password
   ▼                                        ▼
Portal Page ◀───────────────────────── Portal Page
   │
   ├─→ Gateway Dashboard
   └─→ Memory Viewer
```

## Configuration

Edit `server.py` to customize:

```python
PORT = 18780                    # Portal port
GATEWAY_URL = "http://localhost:18789"   # Gateway Dashboard
MEMORY_URL = "http://localhost:18799"    # Memory Viewer
COOKIE_EXPIRE_DAYS = 7          # Cookie validity
PASSWORD_FILE = "/opt/uni-dashboard/.password"
```

## Add More Services

Edit `SERVICES` dict in `server.py`:

```python
SERVICES = {
    "gateway": {...},
    "memory": {...},
    "grafana": {
        "name": "Grafana",
        "url": "http://localhost:3000",
        "icon": "📊",
        "desc": "Monitoring Dashboard",
        "color": "#f46800"
    }
}
```

## Port Planning

| Service | Port |
|---------|------|
| Uni Dashboard | 18780 |
| Gateway Dashboard | 18789 |
| Memory Viewer | 18799 |

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
```

## Tech Stack

- **Backend**: FastAPI + uvicorn
- **HTTP Client**: httpx
- **Authentication**: SHA256 hashing + UUID tokens

## License

[MIT License](LICENSE)

## Author

Enzo (骁骑) - CTO @ Enzo