@echo off
REM Script para ejecutar la aplicacion en Windows
REM Activa automaticamente el entorno virtual si existe

echo ============================================
echo   Analizador Bursatil - Iniciando...
echo ============================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "run_app.py" (
    echo [ERROR] No se encontro run_app.py
    echo         Ejecuta este script desde el directorio del proyecto
    pause
    exit /b 1
)

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo [*] Activando entorno virtual...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo [WARNING] No se pudo activar el entorno virtual
        echo           Continuando con Python global...
    ) else (
        echo [OK] Entorno virtual activado
    )
) else (
    echo [*] No se encontro entorno virtual, usando Python global
    echo     Tip^: Ejecuta install.bat para crear un entorno virtual
)

REM Verificar que Python esta instalado
echo [*] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo         Instala Python desde^: https^://www.python.org/downloads/
    echo         O ejecuta^: install.bat
    pause
    exit /b 1
)

REM Mostrar version de Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION%

REM Verificar que las dependencias estan instaladas
echo [*] Verificando dependencias...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [ERROR] Las dependencias no estan instaladas
    echo         Ejecuta^: install.bat
    echo         O manualmente^: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencias verificadas

echo.
echo ============================================
echo   Ejecutando aplicacion...
echo ============================================
echo.
echo La aplicacion se abrira en tu navegador
echo URL^: http^://localhost^:8501
echo.
echo Presiona Ctrl+C para detener la aplicacion
echo.

REM Ejecutar la aplicacion
python run_app.py

REM Si la aplicacion termina con error, pausar para ver el mensaje
if errorlevel 1 (
    echo.
    echo [ERROR] La aplicacion termino con errores
    pause
    exit /b 1
)

REM No hacer pausa si todo salio bien (el usuario presiono Ctrl+C)
