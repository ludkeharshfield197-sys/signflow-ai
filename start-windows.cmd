@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\team\start.ps1" -OpenBrowser
set "SIGNFLOW_EXIT=%ERRORLEVEL%"
echo.
if not "%SIGNFLOW_EXIT%"=="0" echo 启动失败，请查看上面的错误信息和 .team-runtime 日志。
pause
exit /b %SIGNFLOW_EXIT%

