@echo off
rem Double-click to test the Hall of Records preview on this PC and on your phone (same Wi-Fi).
cd /d "%~dp0"
echo.
echo   Hall of Records preview is running.
echo   On this computer:  http://localhost:8000
echo   On your phone:     http://YOUR-PC-IP:8000   (find it with: ipconfig, "IPv4 Address")
echo.
echo   Leave this window open while you test. Close it to stop.
echo.
start "" http://localhost:8000
py -m http.server 8000 --bind 0.0.0.0 2>nul || python -m http.server 8000 --bind 0.0.0.0
pause
