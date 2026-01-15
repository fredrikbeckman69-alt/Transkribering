@echo off
echo Startar lokal server for Svensk Transkribering...
echo.
echo Detta kravs for att undvika problem med "Failed to fetch" / CORS.
echo.
start "" "http://localhost:8000"
python server.py
pause
