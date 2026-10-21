@echo off
setlocal
python "%~dp0tools\translation-menu.py" %*
set "result=%errorlevel%"
echo.
if not "%result%"=="0" pause
exit /b %result%
