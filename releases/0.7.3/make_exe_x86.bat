@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title GeoViewPlus 0.7.3 - 32-bit EXE

echo ==========================================================
echo  GeoViewPlus 0.7.3 - 32-bit Windows-EXE
echo ==========================================================
echo.
echo This build requires a 32-bit (x86) Python installation.
echo The resulting EXE will be named GeoViewPlus_x86.exe.
echo.

set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    py -3-32 --version >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3-32"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import struct,sys; sys.exit(0 if struct.calcsize('P')*8==32 else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo ERROR: No 32-bit Python 3 installation was found.
    echo Install x86 Python 3 with Tkinter, then run this script again.
    goto :failed
)

%PYTHON_CMD% -c "import struct,sys; print('Python',sys.version); print('Architecture:',struct.calcsize('P')*8,'bit'); sys.exit(0 if struct.calcsize('P')*8==32 else 1)"
if errorlevel 1 (
    echo ERROR: The selected Python is not 32-bit.
    goto :failed
)

if not exist "GeoViewPlus.py" (
    echo ERROR: GeoViewPlus.py is missing.
    goto :failed
)
if not exist "gvpexport.py" (
    echo ERROR: gvpexport.py is missing.
    goto :failed
)
if not exist "geoscore.py" (
    echo ERROR: geoscore.py is missing.
    goto :failed
)
if not exist "geoworks_motif_icon.ico" (
    echo ERROR: geoworks_motif_icon.ico is missing.
    goto :failed
)

%PYTHON_CMD% -c "import tkinter; import PIL; import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo ERROR: Tkinter, Pillow, or PyInstaller is missing in this x86 Python.
    echo Install the x86-compatible packages in this same Python environment:
    echo   %PYTHON_CMD% -m pip install pillow pyinstaller
    echo Optional Explorer drag-and-drop:
    echo   %PYTHON_CMD% -m pip install tkinterdnd2
    goto :failed
)

set "DND_OPT="
%PYTHON_CMD% -c "import tkinterdnd2" >nul 2>nul
if not errorlevel 1 set "DND_OPT=--collect-all tkinterdnd2"

echo.
echo Building the 32-bit executable ...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --windowed --name GeoViewPlus_x86 --distpath "dist-x86" --workpath "build-x86" --specpath "build-x86" --icon "%~dp0geoworks_motif_icon.ico" --add-data "%~dp0geoworks_motif_icon.ico;." --add-data "%~dp0JME-Spirallogo.png;." --hidden-import PIL.ImageTk %DND_OPT% "%~dp0GeoViewPlus.py"
if errorlevel 1 goto :failed

if not exist "dist-x86\GeoViewPlus_x86.exe" (
    echo ERROR: The executable was not found in dist-x86.
    goto :failed
)

echo.
echo SUCCESS: dist-x86\GeoViewPlus_x86.exe
echo Confirm the executable on a 32-bit Windows system before release.
pause
exit /b 0

:failed
echo.
echo BUILD FAILED. No working 32-bit executable is claimed.
pause
exit /b 1
