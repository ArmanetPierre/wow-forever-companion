@echo off
rem Double-clic : installe ou met a jour WoW Forever Companion (Windows).
rem Double-click: installs or updates WoW Forever Companion (Windows).
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0files\install\install.ps1" %*
set CODE=%ERRORLEVEL%
echo.
pause
exit /b %CODE%
