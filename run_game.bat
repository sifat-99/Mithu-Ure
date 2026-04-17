@echo off
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set PYTHON="%SCRIPT_DIR%.venv\Scripts\python.exe"
if not exist %PYTHON% (
    echo Virtual environment Python not found.
    echo Run "powershell -ExecutionPolicy RemoteSigned -File .\run_game.ps1" after creating the venv.
    exit /b 1
)
cd /d "%SCRIPT_DIR%"
%PYTHON% "%SCRIPT_DIR%main.py" %*
