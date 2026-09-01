@echo off
echo Starting AI Agent...

start cmd /k "python app.py"

timeout /t 2 /nobreak >nul

start index.html