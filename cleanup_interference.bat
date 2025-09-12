@echo off
echo ==========================================
echo MELD Visualizer Interference Cleanup Tool
echo ==========================================
echo.

echo Step 1: Killing any running Python processes...
taskkill /F /IM python.exe 2>nul
if %errorlevel%==0 (
    echo    [OK] Python processes terminated
) else (
    echo    [INFO] No Python processes found
)

echo.
echo Step 2: Clearing Python bytecode cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo    Removing: %%d
    rd /s /q "%%d" 2>nul
)
echo    [OK] Python cache cleared

echo.
echo Step 3: Clearing pip cache...
pip cache purge 2>nul
echo    [OK] Pip cache cleared

echo.
echo Step 4: Browser Cache Instructions
echo ==========================================
echo Please clear your browser cache manually:
echo.
echo Chrome/Edge:
echo   1. Press Ctrl+Shift+Delete
echo   2. Select "Cached images and files"
echo   3. Click "Clear data"
echo.
echo Or use Developer Tools:
echo   1. Press F12
echo   2. Right-click the refresh button
echo   3. Select "Empty Cache and Hard Reload"
echo.

echo.
echo Step 5: Port 8050 Check...
netstat -an | findstr :8050 >nul
if %errorlevel%==0 (
    echo    [WARNING] Port 8050 may still be in use
    echo    Consider restarting your computer if issues persist
) else (
    echo    [OK] Port 8050 is free
)

echo.
echo ==========================================
echo Cleanup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Clear browser cache as instructed above
echo 2. Run your app with: python src/meld_visualizer/app.py
echo 3. If issues persist, restart your computer
echo.
pause
