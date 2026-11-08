@echo off
setlocal
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
rem Bridge is disabled unless explicitly enabled.
rem MEMORY_BRIDGE_ENABLED=1
rem MEMORY_ADAPTER_URL=http://127.0.0.1:18081
rem MEMORY_CLIENT_TOKEN should come from the environment, never a committed file.
python "%~dp0..\bridge\memory_bridge.py"
endlocal
