#!/usr/bin/env python3
"""
Uni Dashboard - 统一入口门户
FastAPI 反向代理，支持多 Web UI 整合 + 密码保护 + 动态添加入口

两种模式：
  SSH 映射模式（默认）：
    python server.py
    # 监听 127.0.0.1:18780，需要 SSH 端口转发访问

  公网访问模式：
    python server.py --public
    # 监听 0.0.0.0:18780，直接公网访问

注意：两种模式打开页面后流程一致，都需要输入密码。
"""

import os
import sys
import json
import hashlib
import argparse
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

try:
    from fastapi import FastAPI, Request, Response, HTTPException, Form
    from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
    import httpx
    from uvicorn import run as uvicorn_run
except ImportError:
    print("请先安装依赖：pip install fastapi uvicorn httpx")
    sys.exit(1)

# === 配置 ===
PORT = 18780
GATEWAY_URL = "http://localhost:18789"
MEMORY_URL = "http://localhost:18799"
COOKIE_NAME = "uni_dashboard_auth"
COOKIE_EXPIRE_DAYS = 7
PASSWORD_FILE = Path("/opt/uni-dashboard/.password")
DATA_DIR = Path("/opt/uni-dashboard/data")
SERVICES_FILE = DATA_DIR / "services.json"

# === 初始化 ===
app = FastAPI(title="Uni Dashboard")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 默认服务配置
DEFAULT_SERVICES = {
    "gateway": {
        "name": "Gateway Dashboard",
        "url": GATEWAY_URL,
        "icon": "⚡",
        "desc": "网关控制面板 - 管理会话、查看日志、配置服务",
        "color": "#e94560",
        "is_default": True
    }
}

# === 服务管理 ===
def load_services() -> Dict[str, Any]:
    """加载服务配置"""
    if SERVICES_FILE.exists():
        try:
            return json.loads(SERVICES_FILE.read_text())
        except:
            pass
    return DEFAULT_SERVICES.copy()

def save_services(services: Dict[str, Any]):
    """保存服务配置"""
    SERVICES_FILE.write_text(json.dumps(services, indent=2, ensure_ascii=False))

def add_service(key: str, name: str, port: int, icon: str = "🔗", desc: str = "", color: str = "#4ecdc4") -> bool:
    """添加新服务"""
    services = load_services()
    if key in services:
        return False
    services[key] = {
        "name": name,
        "url": f"http://localhost:{port}",
        "icon": icon,
        "desc": desc or f"{name} - 端口 {port}",
        "color": color,
        "is_default": False
    }
    save_services(services)
    return True

def remove_service(key: str) -> bool:
    """删除服务"""
    services = load_services()
    if key not in services:
        return False
    if services[key].get("is_default"):
        return False  # 不能删除默认服务
    del services[key]
    save_services(services)
    return True

# === 密码管理 ===
def hash_password(password: str) -> str:
    """SHA256 哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def password_exists() -> bool:
    """检查是否已设置密码"""
    return PASSWORD_FILE.exists() and PASSWORD_FILE.read_text().strip()

def save_password(password: str):
    """保存密码（哈希后）"""
    PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)
    PASSWORD_FILE.write_text(hash_password(password))
    PASSWORD_FILE.chmod(0o600)

def verify_password(password: str) -> bool:
    """验证密码"""
    if not password_exists():
        return False
    stored = PASSWORD_FILE.read_text().strip()
    return stored == hash_password(password)

# === Token 管理 ===
def create_auth_token() -> str:
    """创建认证 token"""
    return secrets.token_urlsafe(32)

def save_auth_token(token: str):
    """保存认证 token"""
    token_file = DATA_DIR / "auth_tokens.json"
    tokens = {}
    if token_file.exists():
        tokens = json.loads(token_file.read_text())
    tokens[token] = datetime.now().isoformat()
    token_file.write_text(json.dumps(tokens))

def validate_auth_token(token: str) -> bool:
    """验证认证 token"""
    token_file = DATA_DIR / "auth_tokens.json"
    if not token_file.exists():
        return False
    tokens = json.loads(token_file.read_text())
    if token not in tokens:
        return False
    created = datetime.fromisoformat(tokens[token])
    return datetime.now() - created < timedelta(days=COOKIE_EXPIRE_DAYS)

# === 依赖项 ===
def get_current_user(request: Request) -> Optional[str]:
    """获取当前用户（通过 Cookie）"""
    token = request.cookies.get(COOKIE_NAME)
    if token and validate_auth_token(token):
        return "authenticated"
    return None

# === 页面模板 ===
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uni Dashboard - 登录</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            text-align: center;
            padding: 40px;
        }}
        .logo {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        h1 {{
            color: #e94560;
            font-size: 2em;
            margin-bottom: 5px;
        }}
        .subtitle {{
            color: #888;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 30px 40px;
            backdrop-filter: blur(10px);
        }}
        .form-group {{
            margin-bottom: 15px;
            text-align: left;
        }}
        label {{
            display: block;
            color: #aaa;
            margin-bottom: 5px;
            font-size: 0.9em;
        }}
        input {{
            width: 100%;
            padding: 12px 16px;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 1em;
            transition: border-color 0.3s;
        }}
        input:focus {{
            outline: none;
            border-color: #e94560;
        }}
        .btn {{
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #e94560, #c23a51);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 10px;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(233, 69, 96, 0.3);
        }}
        .error {{
            color: #ff6b6b;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .hint {{
            color: #666;
            font-size: 0.8em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🛡️</div>
        <h1>Uni Dashboard</h1>
        <p class="subtitle">{subtitle}</p>

        <div class="card">
            <form action="/auth" method="post">
                <div class="form-group">
                    <label>{label1}</label>
                    <input type="password" name="password" placeholder="输入密码" required>
                </div>
                {confirm_field}
                <button type="submit" class="btn">{button_text}</button>
            </form>
            {error}
        </div>

        <p class="hint">Powered by OpenClaw</p>
    </div>
</body>
</html>
"""

def get_login_page(error: str = "", is_setup: bool = False) -> str:
    if is_setup:
        subtitle = "首次访问，请设置密码"
        label1 = "设置密码"
        confirm_field = """
                <div class="form-group">
                    <label>确认密码</label>
                    <input type="password" name="confirm_password" placeholder="再次输入密码" required>
                </div>
        """
        button_text = "设置密码并登录"
    else:
        subtitle = "请输入密码访问"
        label1 = "密码"
        confirm_field = ""
        button_text = "登录"

    error_html = f'<p class="error">{error}</p>' if error else ''

    return LOGIN_PAGE.format(
        subtitle=subtitle,
        label1=label1,
        confirm_field=confirm_field,
        button_text=button_text,
        error=error_html
    )

INDEX_PAGE = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uni Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            text-align: center;
            padding: 40px;
            width: 100%;
            max-width: 1200px;
        }}
        h1 {{
            color: #e94560;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(233, 69, 96, 0.3);
        }}
        .subtitle {{
            color: #a0a0a0;
            margin-bottom: 50px;
            font-size: 1.1em;
        }}
        .cards {{
            display: flex;
            gap: 30px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .card {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 40px 30px;
            width: 280px;
            text-decoration: none;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            position: relative;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }}
        .card-icon {{
            font-size: 48px;
            margin-bottom: 20px;
        }}
        .card h2 {{
            color: #fff;
            font-size: 1.5em;
            margin-bottom: 10px;
        }}
        .card p {{
            color: #888;
            font-size: 0.9em;
            line-height: 1.5;
        }}
        .card .delete-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: rgba(255,0,0,0.3);
            border: none;
            color: #fff;
            cursor: pointer;
            font-size: 14px;
            display: none;
            transition: background 0.2s;
        }}
        .card:hover .delete-btn {{
            display: block;
        }}
        .card .delete-btn:hover {{
            background: rgba(255,0,0,0.6);
        }}
        .card.add-card {{
            border: 2px dashed rgba(255,255,255,0.2);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }}
        .card.add-card:hover {{
            border-color: #e94560;
        }}
        .add-icon {{
            font-size: 48px;
            color: #e94560;
            margin-bottom: 10px;
        }}
        .add-text {{
            color: #888;
            font-size: 1em;
        }}
        .footer {{
            margin-top: 50px;
            color: #555;
            font-size: 0.85em;
        }}
        .header-actions {{
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
        }}
        .header-btn {{
            padding: 8px 16px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #aaa;
            text-decoration: none;
            font-size: 0.9em;
            transition: all 0.3s;
            cursor: pointer;
        }}
        .header-btn:hover {{
            background: rgba(255,255,255,0.2);
            color: #fff;
        }}
        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}
        .modal.active {{
            display: flex;
        }}
        .modal-content {{
            background: #1a1a2e;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 30px;
            width: 400px;
            max-width: 90%;
        }}
        .modal h2 {{
            color: #fff;
            margin-bottom: 20px;
        }}
        .modal input {{
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 1em;
            margin-bottom: 15px;
        }}
        .modal input:focus {{
            outline: none;
            border-color: #e94560;
        }}
        .modal-actions {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        .modal-btn {{
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
        }}
        .modal-btn.cancel {{
            background: rgba(255,255,255,0.1);
            color: #aaa;
        }}
        .modal-btn.confirm {{
            background: linear-gradient(135deg, #e94560, #c23a51);
            color: #fff;
        }}
    </style>
</head>
<body>
    <div class="header-actions">
        <button class="header-btn" onclick="openAddModal()">➕ 添加入口</button>
        <a href="/logout" class="header-btn">退出</a>
    </div>

    <div class="container">
        <h1>🛡️ Uni Dashboard</h1>
        <p class="subtitle">选择要访问的服务</p>

        <div class="cards" id="cards-container">
            {cards}
            <div class="card add-card" onclick="openAddModal()">
                <div class="add-icon">➕</div>
                <div class="add-text">添加新入口</div>
            </div>
        </div>

        <p class="footer">Powered by OpenClaw</p>
    </div>

    <!-- Add Modal -->
    <div class="modal" id="addModal">
        <div class="modal-content">
            <h2>添加新入口</h2>
            <input type="text" id="serviceName" placeholder="入口名称（如：Grafana）">
            <input type="number" id="servicePort" placeholder="端口号（如：3000）">
            <input type="text" id="serviceDesc" placeholder="描述（可选）">
            <div class="modal-actions">
                <button class="modal-btn cancel" onclick="closeAddModal()">取消</button>
                <button class="modal-btn confirm" onclick="addService()">添加</button>
            </div>
        </div>
    </div>

    <script>
        function openAddModal() {{
            document.getElementById('addModal').classList.add('active');
        }}

        function closeAddModal() {{
            document.getElementById('addModal').classList.remove('active');
            document.getElementById('serviceName').value = '';
            document.getElementById('servicePort').value = '';
            document.getElementById('serviceDesc').value = '';
        }}

        async function addService() {{
            const name = document.getElementById('serviceName').value.trim();
            const port = document.getElementById('servicePort').value;
            const desc = document.getElementById('serviceDesc').value.trim();

            if (!name || !port) {{
                alert('请填写名称和端口号');
                return;
            }}

            try {{
                const response = await fetch('/api/services', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ name, port: parseInt(port), desc }})
                }});

                if (response.ok) {{
                    window.location.reload();
                }} else {{
                    const data = await response.json();
                    alert(data.message || '添加失败');
                }}
            }} catch (err) {{
                alert('添加失败: ' + err.message);
            }}
        }}

        async function deleteService(key) {{
            if (!confirm('确定要删除这个入口吗？')) return;

            try {{
                const response = await fetch('/api/services/' + key, {{
                    method: 'DELETE'
                }});

                if (response.ok) {{
                    window.location.reload();
                }} else {{
                    alert('删除失败');
                }}
            }} catch (err) {{
                alert('删除失败: ' + err.message);
            }}
        }}
    </script>
</body>
</html>
"""

def get_index_page() -> str:
    services = load_services()
    cards_html = ""
    for key, service in services.items():
        is_default = service.get("is_default", False)
        delete_btn = "" if is_default else f'<button class="delete-btn" onclick="event.preventDefault(); deleteService(\'{key}\')">×</button>'
        cards_html += f"""
            <a href="/{key}/" class="card" style="border-color: {service['color']}40;"
               onmouseover="this.style.borderColor='{service['color']}'"
               onmouseout="this.style.borderColor='{service['color']}40'">
                {delete_btn}
                <div class="card-icon">{service['icon']}</div>
                <h2>{service['name']}</h2>
                <p>{service['desc']}</p>
            </a>
        """
    return INDEX_PAGE.format(cards=cards_html)

# === 路由 ===
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """入口页"""
    if not password_exists():
        return RedirectResponse(url="/setup", status_code=302)

    if not get_current_user(request):
        return RedirectResponse(url="/login", status_code=302)

    return get_index_page()

@app.get("/setup", response_class=HTMLResponse)
async def setup_page():
    """首次设置密码页面"""
    if password_exists():
        return RedirectResponse(url="/login", status_code=302)
    return get_login_page(is_setup=True)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    if not password_exists():
        return RedirectResponse(url="/setup", status_code=302)

    if get_current_user(request):
        return RedirectResponse(url="/", status_code=302)

    error = request.query_params.get("error", "")
    return get_login_page(error=error, is_setup=False)

@app.post("/auth")
async def auth(
    request: Request,
    password: str = Form(...),
    confirm_password: Optional[str] = Form(default=None)
):
    """认证处理"""
    if not password_exists():
        if not confirm_password or password != confirm_password:
            return HTMLResponse(content=get_login_page(error="两次密码不一致", is_setup=True), status_code=400)
        if len(password) < 4:
            return HTMLResponse(content=get_login_page(error="密码至少 4 位", is_setup=True), status_code=400)
        save_password(password)
        token = create_auth_token()
        save_auth_token(token)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(COOKIE_NAME, token, max_age=COOKIE_EXPIRE_DAYS * 24 * 60 * 60)
        return response

    if verify_password(password):
        token = create_auth_token()
        save_auth_token(token)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(COOKIE_NAME, token, max_age=COOKIE_EXPIRE_DAYS * 24 * 60 * 60)
        return response
    else:
        return HTMLResponse(content=get_login_page(error="密码错误", is_setup=False), status_code=401)

@app.get("/logout")
async def logout():
    """退出登录"""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(COOKIE_NAME)
    return response

# === API 路由 ===
@app.post("/api/services")
async def api_add_service(request: Request):
    """添加新服务"""
    if not get_current_user(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()
    name = data.get("name", "").strip()
    port = data.get("port")
    desc = data.get("desc", "").strip()

    if not name or not port:
        raise HTTPException(status_code=400, detail="Name and port are required")

    # 生成 key
    key = name.lower().replace(" ", "-").replace("/", "-")

    if add_service(key, name, port, desc=desc):
        return {"success": True, "key": key}
    else:
        raise HTTPException(status_code=400, detail="Service already exists")

@app.delete("/api/services/{key}")
async def api_remove_service(key: str, request: Request):
    """删除服务"""
    if not get_current_user(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if remove_service(key):
        return {"success": True}
    else:
        raise HTTPException(status_code=400, detail="Cannot delete this service")

# === 代理路由 ===
async def proxy_service(service_key: str, request: Request):
    """代理到指定服务"""
    services = load_services()
    if service_key not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    if not get_current_user(request):
        raise HTTPException(status_code=302, headers={"Location": "/login"})

    service = services[service_key]
    target_url = service["url"]

    path = request.url.path[len(f"/{service_key}"):]
    if request.url.query:
        path += f"?{request.url.query}"
    url = f"{target_url}{path}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            headers = dict(request.headers)
            headers.pop("host", None)

            if request.headers.get("upgrade", "").lower() == "websocket":
                return HTMLResponse(
                    content="<h1>WebSocket 连接</h1><p>请直接访问后端服务，或使用 SSH 端口转发。</p>",
                    status_code=200
                )

            body = await request.body()
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                follow_redirects=False
            )

            excluded_headers = ["content-encoding", "content-length", "transfer-encoding"]
            response_headers = [
                (k, v) for k, v in response.headers.items()
                if k.lower() not in excluded_headers
            ]

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response_headers)
            )
        except httpx.ConnectError:
            return HTMLResponse(
                content=f"<h1>服务不可用</h1><p>无法连接到 {service['name']}，请检查服务是否运行。</p><p>目标地址：{target_url}</p>",
                status_code=502
            )
        except Exception as e:
            return HTMLResponse(
                content=f"<h1>代理错误</h1><p>{str(e)}</p>",
                status_code=500
            )

# 动态代理路由处理
@app.route("/{service_key}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def dynamic_proxy(request: Request):
    service_key = request.path_params.get("service_key")
    return await proxy_service(service_key, request)

@app.route("/{service_key}/", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def dynamic_proxy_root(request: Request):
    service_key = request.path_params.get("service_key")
    return await proxy_service(service_key, request)

# === 启动 ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uni Dashboard - 统一入口门户")
    parser.add_argument("--public", action="store_true", help="公网访问模式（监听 0.0.0.0）")
    parser.add_argument("--port", type=int, default=PORT, help=f"端口号（默认 {PORT}）")
    args = parser.parse_args()

    host = "0.0.0.0" if args.public else "127.0.0.1"

    print(f"""
╔══════════════════════════════════════════════╗
║          🛡️  Uni Dashboard v1.1.0           ║
╠══════════════════════════════════════════════╣
║  监听: {host}:{args.port}
║  模式: {"公网访问" if args.public else "SSH 映射"}
║  认证: 密码保护（两种模式一致）
║  功能: 支持动态添加入口
╠══════════════════════════════════════════════╣
║  访问方式:
║  {"http://公网IP:" + str(args.port) if args.public else "ssh -L " + str(args.port) + ":localhost:" + str(args.port) + " user@server"}
╚══════════════════════════════════════════════╝
    """)

    uvicorn_run(app, host=host, port=args.port)