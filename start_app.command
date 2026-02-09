#!/bin/bash

# === 1. 定位文件夹 ===
#这一步是为了确保 Mac 知道 main.py 就在当前目录下
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo "🍱 Vibe Food App is Starting..."
echo "=========================================="

# === 2. 检查依赖 (可选，防止朋友没装库) ===
# 如果没有安装 uvicorn，尝试自动安装
if ! python3 -c "import uvicorn" &> /dev/null; then
    echo "📦 Installing required libraries..."
    pip3 install fastapi uvicorn google-generativeai googlemaps
fi

# === 3. 启动 Python 后端 ===
# 使用 nohup 让它在后台运行，并把日志输出到 backend.log
echo "🚀 Launching Backend Server..."
nohup python3 -m uvicorn main:app --reload --port 8000 > backend.log 2>&1 &
SERVER_PID=$! # 记住这个进程号，一会儿好关闭它

# 等待 3 秒，确保服务器跑起来了
echo "⏳ Waiting for server..."
sleep 3

# === 4. 打开浏览器 ===
# 调用 Mac 系统默认浏览器打开你的网页
echo "✨ Opening App Interface..."
open "http://localhost:8000/static/index.html"

# === 5. 保持运行直到关闭 ===
echo "✅ App is running! "
echo "📝 (Logs are being saved to backend.log)"
echo ""
echo "👉 Press [ENTER] to close the App and stop the server."
echo "=========================================="

# 等待用户按回车
read

# === 6. 清理退出 ===
echo "🛑 Stopping Server..."
kill $SERVER_PID
echo "👋 Bye Bye!"
