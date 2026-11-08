@echo off
setlocal
set "PYTHONIOENCODING=utf-8"
set "MEMORY_CORE_URL=http://127.0.0.1:18080"
set "MEMORY_DATA_DIR=%~dp0..\examples\data"
set "MEMORY_CLIENTS=%~dp0..\examples\clients.example.json"
set "MEMORY_POLICY=%~dp0..\examples\policy.example.json"
set "MEMORY_ADAPTER_PORT=18081"
python "%~dp0..\adapter\adapter.py"
endlocal
