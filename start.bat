@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

REM ============ 端口配置（本机 8000 被占用，默认用 8010；如空闲可改回 8000）============
set BACKEND_PORT=8010
set FRONTEND_PORT=5173
set BACKEND_URL=http://127.0.0.1:%BACKEND_PORT%
set APP_URL=http://127.0.0.1:%FRONTEND_PORT%

REM ============ 选择 Python（优先用 backend\.venv）============
if exist "backend\.venv\Scripts\python.exe" (
  set PY=.venv\Scripts\python.exe
) else (
  set PY=python
)

echo [GPR-AI] 启动后端 (FastAPI) %BACKEND_URL% ...
start "GPR-AI Backend" cmd /k "cd /d %~dp0backend && set BACKEND_PORT=%BACKEND_PORT% && set PUBLIC_BASE_URL=%BACKEND_URL% && %PY% main.py"

echo [GPR-AI] 启动前端 (Vite) %APP_URL% ...
start "GPR-AI Frontend" cmd /k "cd /d %~dp0frontend && set VITE_PROXY_TARGET=%BACKEND_URL% && npm run dev"

echo [GPR-AI] 等待服务就绪（约 8 秒）...
timeout /t 8 /nobreak >nul

echo [GPR-AI] 打开浏览器 %APP_URL%
start "" "%APP_URL%"

echo.
echo ================================================
echo   前端:  %APP_URL%
echo   后端:  %BACKEND_URL%/docs
echo   关闭:  直接关掉弹出的两个命令行窗口即可
echo ================================================
endlocal
