@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title GeoViewPlus 0.7.0 - EXE erstellen

echo ==========================================================
echo  GeoViewPlus 0.7.0 - Windows-EXE erstellen
echo ==========================================================
echo.
echo Suche eine vorhandene Python-Installation ...
set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    py -3 --version >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        python --version >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo FEHLER: Python 3 wurde nicht gefunden.
    echo Installiere Python 3 oder aktiviere den Python Launcher.
    goto :failed
)

echo Gefundene Python-Umgebung:
%PYTHON_CMD% --version
echo.

if not exist "GeoViewPlus.py" (
    echo FEHLER: GeoViewPlus.py fehlt.
    goto :failed
)
if not exist "gvpexport.py" (
    echo FEHLER: gvpexport.py fehlt.
    goto :failed
)
if not exist "geoscore.py" (
    echo FEHLER: geoscore.py fehlt.
    goto :failed
)
if not exist "geoworks_motif_icon.ico" (
    echo FEHLER: geoworks_motif_icon.ico fehlt.
    goto :failed
)

echo Pruefe Tkinter ...
%PYTHON_CMD% -c "import tkinter; print('Tkinter OK')"
if errorlevel 1 (
    echo FEHLER: Diese Python-Installation enthaelt kein funktionierendes Tkinter.
    goto :failed
)

echo.
echo Pruefe Pillow (Bildverarbeitung) ...
%PYTHON_CMD% -c "import PIL; print('Pillow OK')" >nul 2>nul
if errorlevel 1 (
    echo Pillow ist nicht installiert. GeoViewPlus 0.5 braucht Pillow fuer die Icons.
    choice /c JN /n /m "Pillow jetzt in dieser Python-Umgebung installieren? [J/N] "
    if errorlevel 2 goto :failed
    %PYTHON_CMD% -m pip install --user --upgrade pillow
    if errorlevel 1 (
        echo FEHLER: Pillow konnte nicht installiert werden.
        goto :failed
    )
)
:pillow_skipped

echo.
echo Pruefe tkinterdnd2 (optional, fuer Ziehen und Ablegen aus dem Explorer) ...
%PYTHON_CMD% -c "import tkinterdnd2" >nul 2>nul
if not errorlevel 1 goto :dnd_ok
choice /c JN /n /m "tkinterdnd2 jetzt installieren? [J/N] "
if errorlevel 2 goto :dnd_check
%PYTHON_CMD% -m pip install --user --upgrade tkinterdnd2
:dnd_check
%PYTHON_CMD% -c "import tkinterdnd2" >nul 2>nul
if errorlevel 1 goto :dnd_none
:dnd_ok
set "DND_OPT=--collect-all tkinterdnd2"
echo tkinterdnd2 OK - Ziehen und Ablegen wird eingebaut.
goto :dnd_done
:dnd_none
set "DND_OPT="
echo Ohne tkinterdnd2: Ziehen und Ablegen ist in der EXE nicht verfuegbar.
:dnd_done

echo.
echo Pruefe PyInstaller ...
%PYTHON_CMD% -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo PyInstaller ist in dieser Python-Umgebung noch nicht installiert.
    echo Soll PyInstaller jetzt fuer diese Python-Installation installiert werden?
    choice /c JN /n /m "Ja oder Nein? [J/N] "
    if errorlevel 2 goto :failed
    %PYTHON_CMD% -m pip install --user --upgrade pyinstaller
    if errorlevel 1 (
        echo FEHLER: PyInstaller konnte nicht installiert werden.
        goto :failed
    )
)

echo.
echo Starte den EXE-Bau ...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --windowed --name GeoViewPlus --icon "%~dp0geoworks_motif_icon.ico" --add-data "%~dp0geoworks_motif_icon.ico;." --add-data "%~dp0JME-Spirallogo.png;." --hidden-import PIL.ImageTk %DND_OPT% "%~dp0GeoViewPlus.py"
if errorlevel 1 goto :failed

if not exist "dist\GeoViewPlus.exe" (
    echo FEHLER: Die EXE wurde nicht im dist-Ordner gefunden.
    goto :failed
)

echo.
echo ==========================================================
echo ERFOLG: dist\GeoViewPlus.exe wurde erstellt.
echo ==========================================================
echo.
pause
exit /b 0

:failed
echo.
echo ==========================================================
echo FEHLER: Der EXE-Bau wurde nicht erfolgreich abgeschlossen.
echo ==========================================================
echo.
pause
exit /b 1
