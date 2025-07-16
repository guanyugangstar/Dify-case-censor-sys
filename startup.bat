@echo off
REM 一键启动脚本：自动创建虚拟环境、安装依赖并启动Flask服务

REM 1. 检查并创建虚拟环境
if not exist .venv (
    echo 正在创建Python虚拟环境...
    python -m venv .venv
)

REM 2. 激活虚拟环境
call .venv\Scripts\activate.bat

REM 3. 安装依赖（使用清华源）
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

REM 4. 用pythonw.exe后台无窗口启动Flask服务
start /b .venv\Scripts\pythonw.exe app.py

REM 5. 等待服务启动
timeout /t 1 >nul

REM 6. 打开默认浏览器访问首页   
start http://127.0.0.1:5000

REM 7. 退出当前窗口
exit 