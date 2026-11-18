@echo off
setlocal
cd /d "%~dp0\.."
echo GeoViewPlus 0.5 - Alpha99 regression tests
if not defined GEOVIEWPLUS_TOKEN_DB_SAMPLE (
  echo Optional: set GEOVIEWPLUS_TOKEN_DB_SAMPLE to the local token_da(2).000 path for the integration test.
)
python -m unittest -v tests.test_token_db_v2_vm_directory tests.test_token_db_v2_database test_token_db_detection
if errorlevel 1 exit /b 1
echo All Alpha99 regression tests passed.
