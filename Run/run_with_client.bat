@echo off
cd /d "D:\projects\ShowdownServer"
start cmd /k npm run start -- --no-security

:waitloop
timeout /t 2 >nul
netstat -ano | findstr ":8000" | findstr "LISTENING" > nul
if errorlevel 1 goto waitloop

echo Server is up!

cd /d "D:\myprograms\Python\ShowdownClient"
start cmd /k python .\src\main.py