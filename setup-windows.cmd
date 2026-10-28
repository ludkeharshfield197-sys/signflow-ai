@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\team\setup.ps1"
set "SIGNFLOW_EXIT=%ERRORLEVEL%"
echo.
if not "%SIGNFLOW_EXIT%"=="0" echo 安装失败，请查看上面的错误信息。
pause
exit /b %SIGNFLOW_EXIT%

