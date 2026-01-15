@echo off
echo ==========================================
echo    Auto-Syncing to GitHub...
echo ==========================================
echo.

set GIT_PATH="C:\Program Files\Git\cmd\git.exe"

%GIT_PATH% add .
%GIT_PATH% commit -m "Auto-update from background job: %date% %time%"
%GIT_PATH% push origin main

echo.
echo ==========================================
echo    Sync Complete!
echo ==========================================
pause
