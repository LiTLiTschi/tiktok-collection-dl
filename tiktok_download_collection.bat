@echo off
REM ─────────────────────────────────────────────────────────────────────────
REM  tiktok-collection-dl launcher
REM
REM  This bat just activates the venv and runs tiktok-collection-dl.
REM  All config (output dir, format, quality, etc.) is read from:
REM
REM    ~/.config/tiktok_collection_dl_config.yaml       <- global default
REM    ./.config/tiktok_collection_dl_config.yaml       <- next to this bat
REM    ./tiktok_collection_dl_config.yaml               <- next to this bat (wins)
REM
REM  To download a specific collection, set COLLECTION_URL below.
REM  Leave it blank to use list.txt in your configured output directory.
REM
REM  NOTE: use  set "VAR=value"  so & in URLs doesn't break cmd.exe.
REM ─────────────────────────────────────────────────────────────────────────

REM Path to your venv
set "VENV=%USERPROFILE%\.venv"

REM Optional: set a collection URL here, or leave blank to use list.txt
set "COLLECTION_URL="

REM ─────────────────────────────────────────────────────────────────────────
REM  Nothing to edit below this line
REM ─────────────────────────────────────────────────────────────────────────

set "PATH=%VENV%\Scripts;%PATH%"

echo.
echo  tiktok-collection-dl launcher
echo  venv : %VENV%
if not "%COLLECTION_URL%"=="" echo  URL  : %COLLECTION_URL%
if     "%COLLECTION_URL%"=="" echo  Mode : list.txt / config default_output_dir
echo.

if "%COLLECTION_URL%"=="" (
    tiktok-collection-dl
) else (
    tiktok-collection-dl "%COLLECTION_URL%"
)

echo.
if %ERRORLEVEL% EQU 0 (
    echo  Done!
) else (
    echo  Finished with errors ^(exit code %ERRORLEVEL%^). Check output above.
)

echo.
pause
