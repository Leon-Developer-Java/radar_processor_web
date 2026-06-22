#!/usr/bin/env bash
# 一键安装（Git Bash / macOS / Linux）：后端虚拟环境 + 依赖，前端 npm 依赖。
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 是否安装 torch（YOLO 识别需要；只跑其它功能可设 0）
INSTALL_TORCH="${INSTALL_TORCH:-1}"

echo "================================================"
echo "  GPR-AI 环境一键安装（后端 + 前端）"
echo "================================================"

command -v python >/dev/null 2>&1 || { echo "[错误] 未找到 python（需 3.10+）"; exit 1; }
command -v npm    >/dev/null 2>&1 || { echo "[错误] 未找到 npm（需 Node 18+）"; exit 1; }

echo
echo "[1/2] 安装后端环境（backend）..."
cd "$DIR/backend"
if [ ! -d ".venv" ]; then
  echo "  创建虚拟环境 .venv ..."
  python -m venv .venv
fi
# 兼容 Windows(Git Bash) 与 *nix 的 venv 路径
if [ -f ".venv/Scripts/activate" ]; then source ".venv/Scripts/activate"; else source ".venv/bin/activate"; fi
python -m pip install --upgrade pip
if [ "$INSTALL_TORCH" = "1" ]; then
  echo "  安装 torch（CPU 版；GPU 加速请参考 README 手动装 cu118 版）..."
  pip install torch torchvision
fi
echo "  安装其余依赖（requirements.txt）..."
pip install -r requirements.txt

echo
echo "[2/2] 安装前端依赖（frontend）..."
cd "$DIR/frontend"
npm install

echo
echo "================================================"
echo "  安装完成！运行 ./start.sh 启动系统。"
echo "================================================"
