@echo off
REM ─────────────────────────────────────────────────────────────────────────
REM  tiktok-collection-dl launcher
REM
REM  IMPORTANT: use  set "VAR=value"  (quotes around the whole assignment).
REM  This prevents the & in TikTok URLs from being treated as a command
REM  separator by cmd.exe.
REM
REM  Option A — single collection:  set COLLECTION_URL to the full URL.
REM  Option B — batch from list.txt: leave COLLECTION_URL blank and create
REM             OUTPUT_DIR\list.txt with one URL per line (# = comment).
REM ─────────────────────────────────────────────────────────────────────────

REM TikTok collection URL  (leave blank to use list.txt instead)
set "COLLECTION_URL="

REM Destination folder
set "OUTPUT_DIR=D:\Music\TikTok"

REM ─────────────────────────────────────────────────────────────────────────
REM  Nothing to edit below this line
REM ─────────────────────────────────────────────────────────────────────────

echo.
echo  tiktok-collection-dl launcher
if not "%COLLECTION_URL%"=="" echo  URL : %COLLECTION_URL%
if     "%COLLECTION_URL%"=="" echo  Mode: batch from %OUTPUT_DIR%\list.txt
echo  OUT : %OUTPUT_DIR%
echo.

if "%OUTPUT_DIR%"=="" (
    if "%COLLECTION_URL%"=="" (
        tiktok-collection-dl
    ) else (
        tiktok-collection-dl "%COLLECTION_URL%"
    )
) else (
    if "%COLLECTION_URL%"=="" (
        tiktok-collection-dl "%OUTPUT_DIR%"
    ) else (
        tiktok-collection-dl "%COLLECTION_URL%" "%OUTPUT_DIR%"
    )
)

echo.
if %ERRORLEVEL% EQU 0 (
    echo  Done! All tracks downloaded successfully.
) else (
    echo  Finished with errors ^(exit code %ERRORLEVEL%^). Check output above.
)

echo.
pause
