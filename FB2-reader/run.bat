@echo off
if "%~1"=="" (
    python "%~dp0fb2reader.py"
) else (
    python "%~dp0fb2reader.py" "%~1"
)
