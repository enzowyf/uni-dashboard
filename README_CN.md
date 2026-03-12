# Uni Dashboard

统一入口门户 - 将多个 Web UI 整合到单一端口，支持密码保护和动态入口管理。支持 SSH 映射和公网访问两种模式。

## 功能特点

- 🚀 **单端口访问** - 一个端口搞定所有 Web UI
- 🔐 **密码保护** - 首次访问设置密码，后续验证
- 🌐 **双模式支持** - SSH 映射（默认）或公网访问
- ➕ **动态入口** - 通过界面添加/删除服务入口
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

## 动态入口管理

### 默认入口
- **Gateway Dashboard**（端口 18789）- 预配置，不可删除

### 添加新入口
1. 在门户页面点击"➕ 添加入口"按钮
2. 输入入口名称（如：Grafana）
3. 输入端口号（如：3000）
4. 输入描述（可选）
5. 点击"添加"保存

### 删除入口
- 鼠标悬停在非默认入口上，显示 × 按钮
- 点击 × 删除（默认入口无删除按钮）

### 配置存储
- 入口配置保存在 `/opt/uni-dashboard/data/services.json`
- 服务重启后配置不丢失

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
   ├─→ Gateway Dashboard（默认）
   ├─→ Memory Viewer
   └─→ 自定义入口...
```

## 配置说明

编辑 `config.json` 自定义配置：

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

| 字段 | 说明 |
|------|------|
| `port` | 门户端口（默认：18780） |
| `host` | SSH 模式默认监听地址（默认：127.0.0.1） |
| `gateway` | 默认入口配置 |
| `cookie_expire_days` | Session 有效期（天） |

## 端口规划

| 服务 | 端口 |
|------|------|
| Uni Dashboard | 18780 |
| Gateway Dashboard | 18789 |
| Memory Viewer | 18799 |
| 自定义入口 | 用户指定 |

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

## 技术栈

- **后端**: FastAPI + uvicorn
- **HTTP 客户端**: httpx
- **认证**: SHA256 哈希 + UUID 令牌
- **存储**: JSON 文件（无需数据库）

## 更新日志

### v1.1.0
- ➕ 动态入口管理（通过界面添加/删除）
- 🔒 Gateway Dashboard 作为默认不可删除入口
- 💾 配置持久化存储

### v1.0.0
- 初始版本
- SSH 映射和公网访问模式
- 密码保护
- Gateway Dashboard 和 Memory Viewer 入口

## 许可证

[MIT 许可证](LICENSE)

## 作者

Enzo（骁骑）- CTO @ Enzo