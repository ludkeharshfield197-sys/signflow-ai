@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\team\check.ps1"
set "SIGNFLOW_EXIT=%ERRORLEVEL%"
echo.
pause
exit /b %SIGNFLOW_EXIT%

