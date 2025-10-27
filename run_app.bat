@echo off
REM Script para ejecutar la aplicacion en Windows

echo ============================================
echo   Analizador Bursatil - Iniciando...
echo ============================================
echo.

REM Verificar que Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado
    echo    Instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Ejecutar la aplicacion
python run_app.py

pause
