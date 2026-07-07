@echo off
chcp 65001 >nul
title AI求职面试助手 - 启动脚本

echo ================================================
echo          AI求职面试助手 - 一键启动
echo ================================================
echo.

if not exist backend\.env (
    echo [提示] 检测到 backend/.env 文件不存在
    echo [提示] 正在从 .env.example 复制...
    copy backend\.env.example backend\.env >nul
    echo [成功] 已创建 backend/.env 文件
    echo [提示] 请编辑 backend/.env 文件，填写你的 API Key
    echo.
)

echo [步骤1/3] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo        下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [成功] Python环境已就绪

echo.
echo [步骤2/3] 检查并安装后端依赖...
cd backend
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 部分依赖安装失败，请手动检查
)
echo [成功] 后端依赖安装完成
cd ..

echo.
echo [步骤3/3] 启动服务...
echo [提示] 后端服务将在 http://localhost:8000 启动
echo [提示] 前端服务将在 http://localhost:5173 启动
echo.
echo [提示] 按 Ctrl+C 停止服务
echo ================================================
echo.

start "" cmd /k "cd backend && echo [后端] 启动中... && python -m uvicorn app.main:app --reload"
timeout /t 3 /nobreak >nul
start "" cmd /k "cd frontend && echo [前端] 启动中... && npm run dev"

echo.
echo [成功] 服务启动中...
echo [提示] 请等待几秒后打开浏览器访问 http://localhost:5173
echo [提示] 如需停止服务，请关闭弹出的终端窗口
pause