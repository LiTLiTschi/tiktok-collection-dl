@echo off
REM ─────────────────────────────────────────────────────────────────────────
REM  tiktok-collection-dl launcher
REM
REM  Option A — single collection:
REM    Set COLLECTION_URL below. OUTPUT_DIR is where the file(s) land.
REM
REM  Option B — batch from list.txt:
REM    Leave COLLECTION_URL blank and create OUTPUT_DIR\list.txt
REM    with one TikTok collection URL per line (# lines are comments).
REM ─────────────────────────────────────────────────────────────────────────

REM TikTok collection URL  (leave blank to use list.txt instead)
set COLLECTION_URL=

REM Destination folder
set OUTPUT_DIR=D:\Music\TikTok

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
