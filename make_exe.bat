@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo GeoViewPlus 0.3 - Farbmoniker-Testbuild
echo ========================================
where py >nul 2>nul
if errorlevel 1 goto :no_python
if not exist "GeoViewPlus.py" goto :no_source
if not exist "geoworks_motif_icon.ico" goto :no_icon
echo Pruefe Python 3.15 ...
py -3.15 --version
if errorlevel 1 goto :error
echo Pruefe PyInstaller ...
py -3.15 -m PyInstaller --version
if errorlevel 1 goto :error
echo Erstelle GeoViewPlus.exe ...
py -3.15 -m PyInstaller --noconfirm --clean --onefile --windowed --name GeoViewPlus --icon "%~dp0geoworks_motif_icon.ico" "%~dp0GeoViewPlus.py"
if errorlevel 1 goto :error
if not exist "dist\GeoViewPlus.exe" goto :error
echo.
echo ERFOLG: dist\GeoViewPlus.exe wurde erstellt.
pause
exit /b 0
:no_python
echo FEHLER: Python Launcher "py" wurde nicht gefunden.
goto :error
:no_source
echo FEHLER: GeoViewPlus.py fehlt.
goto :error
:no_icon
echo FEHLER: geoworks_motif_icon.ico fehlt.
goto :error
:error
echo.
echo FEHLER: Der Build ist fehlgeschlagen.
pause
exit /b 1
