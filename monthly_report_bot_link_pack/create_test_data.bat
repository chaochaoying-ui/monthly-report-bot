@echo off
cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python create_test_tasks.py
) else (
    python create_test_tasks.py
)

pause

