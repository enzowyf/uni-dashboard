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

## Dynamic Entry Management

### Default Entry
- **Gateway Dashboard** (port 18789) - Pre-configured, cannot be deleted

### Add New Entry
1. Click "➕ Add Entry" button on the portal page
2. Enter entry name (e.g., "Grafana")
3. Enter port number (e.g., 3000)
4. Enter description (optional)
5. Click "Add" to save

### Delete Entry
- Hover over non-default entries to reveal the × button
- Click × to delete (default entry cannot be deleted)

### Configuration Storage
- Entries are stored in `/opt/uni-dashboard/data/services.json`
- Survives service restarts

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
   ├─→ Gateway Dashboard (default)
   ├─→ Memory Viewer
   └─→ Custom entries...
```

## Configuration

Edit `config.json` to customize:

```json
{
  "port": 18780,
  "host": "127.0.0.1",
  "gateway": {
    "name": "Gateway Dashboard",
    "url": "http://localhost:18789",
    "icon": "⚡",
    "desc": "网关控制面板 - 管理会话、查看日志、配置服务",
    "color": "#e94560"
  },
  "cookie_expire_days": 7
}
```

| Field | Description |
|-------|-------------|
| `port` | Portal port (default: 18780) |
| `host` | Default host for SSH mode (default: 127.0.0.1) |
| `gateway` | Default entry configuration |
| `cookie_expire_days` | Session validity in days |

## Port Planning

| Service | Port |
|---------|------|
| Uni Dashboard | 18780 |
| Gateway Dashboard | 18789 |
| Memory Viewer | 18799 |
| Custom entries | User-defined |

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

## Tech Stack

- **Backend**: FastAPI + uvicorn
- **HTTP Client**: httpx
- **Authentication**: SHA256 hashing + UUID tokens
- **Storage**: JSON files (no database required)

## Changelog

### v1.1.0
- ➕ Dynamic entry management (add/remove via UI)
- 🔒 Gateway Dashboard as default non-deletable entry
- 💾 Persistent configuration storage

### v1.0.0
- Initial release
- SSH tunneling and public access modes
- Password protection
- Gateway Dashboard and Memory Viewer entries

## License

[MIT License](LICENSE)

## Author

Enzo (骁骑) - CTO @ Enzo