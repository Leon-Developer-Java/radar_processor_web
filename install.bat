@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

REM ====== 是否安装 torch（YOLO 识别需要；只想跑其它功能可设为 0）======
set INSTALL_TORCH=1

echo ================================================
echo   GPR-AI 环境一键安装（后端 + 前端）
echo ================================================

REM ---------- 环境检查 ----------
where python >nul 2>nul || (echo [错误] 未找到 python，请先安装 Python 3.10+ 并加入 PATH & pause & exit /b 1)
where npm >nul 2>nul || (echo [错误] 未找到 npm，请先安装 Node.js 18+ 并加入 PATH & pause & exit /b 1)

REM ---------- 后端 ----------
echo.
echo [1/2] 安装后端环境（backend）...
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
  echo   创建虚拟环境 .venv ...
  python -m venv .venv
)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if "%INSTALL_TORCH%"=="1" (
  echo   安装 torch（CPU 版；需 GPU 加速请参考 README 手动装 cu118 版）...
  pip install torch torchvision
)
echo   安装其余依赖（requirements.txt）...
pip install -r requirements.txt
if errorlevel 1 (echo [错误] 后端依赖安装失败 & pause & exit /b 1)

REM ---------- 前端 ----------
echo.
echo [2/2] 安装前端依赖（frontend）...
cd /d "%~dp0frontend"
call npm install
if errorlevel 1 (echo [错误] 前端依赖安装失败 & pause & exit /b 1)

echo.
echo ================================================
echo   安装完成！双击 start.bat 即可启动系统。
echo ================================================
pause
endlocal
