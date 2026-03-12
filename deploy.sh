#!/bin/bash
# Uni Dashboard 一键部署脚本
# 支持 SSH 映射模式（默认）和公网访问模式

set -e

PORT=${PORT:-18780}
INSTALL_DIR="/opt/uni-dashboard"
SERVICE_NAME="uni-dashboard"
PUBLIC_MODE=${1:-"ssh"}  # ssh 或 public

echo "╔══════════════════════════════════════════════╗"
echo "║       Uni Dashboard 一键部署脚本             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 root 权限运行：sudo bash $0"
    exit 1
fi

# 安装依赖
echo "📦 安装 Python 依赖..."
pip3 install fastapi uvicorn httpx -q

# 创建目录
echo "📁 创建目录..."
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/data

# 复制文件
echo "📋 复制文件..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp $SCRIPT_DIR/src/server.py $INSTALL_DIR/
cp $SCRIPT_DIR/config.json $INSTALL_DIR/
cp $SCRIPT_DIR/requirements.txt $INSTALL_DIR/

# 设置权限
chmod 600 $INSTALL_DIR/data
chmod +x $INSTALL_DIR/server.py

# 创建 systemd 服务
echo "🔧 创建 systemd 服务..."
if [ "$PUBLIC_MODE" = "public" ]; then
    # 公网模式
    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Uni Dashboard - 统一入口门户（公网模式）
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/server.py --public --port $PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    ACCESS_INFO="公网访问: http://公网IP:$PORT"
else
    # SSH 映射模式（默认）
    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Uni Dashboard - 统一入口门户（SSH 映射模式）
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/server.py --port $PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    ACCESS_INFO="SSH 映射: ssh -L $PORT:localhost:$PORT user@$(hostname)"
fi

# 启动服务
echo "🚀 启动服务..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 等待启动
sleep 2

# 检查状态
if systemctl is-active --quiet $SERVICE_NAME; then
    echo ""
    echo "✅ 部署成功！"
    echo ""
    echo "══════════════════════════════════════════════"
    echo "  模式: $([ "$PUBLIC_MODE" = "public" ] && echo "公网访问" || echo "SSH 映射")"
    echo "  端口: $PORT"
    echo "  $ACCESS_INFO"
    echo "══════════════════════════════════════════════"
    echo ""
    echo "管理命令:"
    echo "  查看状态: systemctl status $SERVICE_NAME"
    echo "  查看日志: journalctl -u $SERVICE_NAME -f"
    echo "  重启服务: systemctl restart $SERVICE_NAME"
    echo ""
    if [ "$PUBLIC_MODE" = "ssh" ]; then
        echo "⚠️  SSH 映射模式下，请在本地执行："
        echo "   ssh -L $PORT:localhost:$PORT user@服务器IP"
        echo "   然后浏览器访问: http://localhost:$PORT"
    fi
else
    echo "❌ 服务启动失败，请检查日志："
    echo "   journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi