@echo off
REM OpenSati Installation Script for Windows
REM https://github.com/OpenSati-com/OpenSati

echo.
echo  OpenSati Installer
echo =====================
echo.

REM Check Python version
python --version > nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.10+
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYVER=%%i
echo V Python %PYVER% detected

REM Create virtual environment
if not exist "venv" (
    echo. Creating virtual environment...
    python -m venv venv
    echo V Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo. Installing OpenSati...
pip install --upgrade pip
pip install -e .

echo.
set /p AUDIO="Install audio support for breathing detection? (y/n): "
if /i "%AUDIO%"=="y" (
    echo. Installing audio dependencies...
    pip install -e ".[audio]"
)

REM Check for Ollama
echo.
echo. Checking for Ollama...
where ollama > nul 2>&1
if errorlevel 1 (
    echo ! Ollama not found. AI features will be disabled.
    echo   Install from: https://ollama.ai/
) else (
    echo V Ollama detected
    set /p MODELS="Download AI models? (llama3 + llava, ~8GB) (y/n): "
    if /i "!MODELS!"=="y" (
        echo. Downloading llama3...
        ollama pull llama3
        echo. Downloading llava...
        ollama pull llava
        echo V AI models ready
    )
)

echo.
echo V Installation complete!
echo.
echo To run OpenSati:
echo   venv\Scripts\activate
echo   opensati
echo.
pause
