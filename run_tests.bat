@echo off
REM =============================================
REM Activate Conda Environment, Run Pytest, Open Report if Success
REM =============================================

REM Change to script's own directory
cd /d %~dp0

REM Activate conda environment
CALL conda activate myenv

REM Run pytest with coverage and HTML report
pytest --cov=src --cov-report=html tests/
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Tests or coverage failed. Skipping report open.
    pause
    EXIT /B %ERRORLEVEL%
)

REM Open HTML report in browser if tests passed
start coverage_html_report\index.html

echo.
echo ✅ Coverage report opened in your default browser.
pause
