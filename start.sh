#!/usr/bin/env bash
# 一键启动（Git Bash / macOS / Linux）：拉起前后端并打开浏览器。
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ===== 端口配置（本机 8000 被占用，默认用 8010；可用环境变量覆盖）=====
BACKEND_PORT="${BACKEND_PORT:-8010}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
BACKEND_URL="http://127.0.0.1:${BACKEND_PORT}"
APP_URL="http://127.0.0.1:${FRONTEND_PORT}"

# 选择 Python（优先 backend/.venv）
PY="python"
if [ -x "$DIR/backend/.venv/Scripts/python.exe" ]; then
  PY="$DIR/backend/.venv/Scripts/python.exe"
elif [ -x "$DIR/backend/.venv/bin/python" ]; then
  PY="$DIR/backend/.venv/bin/python"
fi

echo "[GPR-AI] 启动后端 (FastAPI) ${BACKEND_URL} ..."
( cd "$DIR/backend" && BACKEND_PORT="$BACKEND_PORT" PUBLIC_BASE_URL="$BACKEND_URL" "$PY" main.py ) &
BACK_PID=$!

echo "[GPR-AI] 启动前端 (Vite) ${APP_URL} ..."
( cd "$DIR/frontend" && VITE_PROXY_TARGET="$BACKEND_URL" npm run dev ) &
FRONT_PID=$!

echo "[GPR-AI] 等待服务就绪（约 8 秒）..."
sleep 8

echo "[GPR-AI] 打开浏览器 ${APP_URL}"
if command -v cmd.exe >/dev/null 2>&1; then cmd.exe /c start "" "$APP_URL" >/dev/null 2>&1
elif command -v open >/dev/null 2>&1; then open "$APP_URL"
elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$APP_URL"
fi

echo "================================================"
echo "  前端:  ${APP_URL}"
echo "  后端:  ${BACKEND_URL}/docs"
echo "  停止:  Ctrl+C"
echo "================================================"

trap 'kill $BACK_PID $FRONT_PID 2>/dev/null' INT TERM
wait
