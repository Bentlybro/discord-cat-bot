@echo off
REM Discord Cat Bot - Windows Background Runner
REM This keeps the bot running in the background on Windows

echo Starting Discord Cat Bot...
echo Press Ctrl+C to stop the bot

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Keep restarting the bot if it crashes
:loop
echo [%date% %time%] Starting bot...
python bot.py
echo [%date% %time%] Bot stopped. Restarting in 10 seconds...
timeout /t 10 /nobreak
goto loop

