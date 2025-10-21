@echo off
chcp 65001 > nul
echo Конвертор MP3 в M4A
echo.

:: Перевірка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не знайдено. Завантаження...
    echo Відкриваю сторінку завантаження Python...
    start https://www.python.org/downloads/
    echo.
    echo Встановіть Python та запустіть скрипт знову
    pause
    exit
)

python mp3_to_m4a_converter.py