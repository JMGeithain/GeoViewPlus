# GeoViewPlus 0.7.3 – 32-bit Windows build

The x86 build is experimental. It has not yet been built or tested on 32-bit Windows.

## Requirements

- A 32-bit (x86) Python 3 installation for Windows, including Tkinter.
- Pillow and PyInstaller installed into that same x86 Python environment.
- Optional: `tkinterdnd2` for Explorer drag-and-drop support.

A 32-bit executable must be built with a 32-bit Python environment and compatible packages. A successful build on 64-bit Python produces a 64-bit executable instead.

## Build

1. Open the `releases/0.7.3` folder in the Windows source package.
2. Install the required packages into the x86 Python environment if they are not already installed:
   ```bat
   py -3-32 -m pip install pillow pyinstaller
   ```
   Optional drag-and-drop:
   ```bat
   py -3-32 -m pip install tkinterdnd2
   ```
3. Run `make_exe_x86.bat`.

The script checks that Python is 32-bit and writes the executable to `dist-x86\GeoViewPlus_x86.exe`. Its temporary build files go to `build-x86`; the normal 64-bit build output is not overwritten.

If the Python launcher does not recognize `-3-32`, install x86 Python and make its `python.exe` the active `python` command before running the script.

## Verification status

The script and documentation are committed on the `feature/32bit-windows` branch. No x86 build was run in this environment, so **the executable's compatibility and runtime behavior on 32-bit Windows remain unverified**. Test the resulting EXE on a real 32-bit Windows installation before distributing it.
