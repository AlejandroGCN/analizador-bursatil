@echo off
REM ============================================================================
REM Script de Instalacion - Analizador Bursatil
REM IMPORTANTE: Ejecuta este archivo desde CMD de Windows, NO desde Git Bash
REM ============================================================================

setlocal EnableDelayedExpansion

echo.
echo ========================================================================
echo     INSTALADOR - ANALIZADOR BURSATIL
echo ========================================================================
echo.
echo IMPORTANTE: Este script debe ejecutarse desde CMD de Windows
echo Si estas en Git Bash, abre CMD y ejecuta este archivo.
echo.
pause

REM ============================================================================
REM 1. VERIFICAR DIRECTORIO DEL PROYECTO
REM ============================================================================
echo.
echo [PASO 1/8] Verificando directorio del proyecto...
if not exist "pyproject.toml" (
    echo [ERROR] No se encontro pyproject.toml
    echo         Ejecuta este script desde el directorio raiz del proyecto.
    goto :error
)
if not exist "requirements.txt" (
    echo [ERROR] No se encontro requirements.txt
    goto :error
)
echo [OK] Directorio del proyecto correcto

REM ============================================================================
REM 2. VERIFICAR PYTHON
REM ============================================================================
echo.
echo [PASO 2/8] Verificando Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor instala Python 3.9 o superior desde python.org
    echo y asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    echo Despues de instalar Python, vuelve a ejecutar este script.
    goto :error
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detectado

REM Verificar version minima
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)
if %PYTHON_MAJOR% LSS 3 goto :python_version_error
if %PYTHON_MAJOR%==3 if %PYTHON_MINOR% LSS 9 goto :python_version_error
echo [OK] Version de Python compatible
goto :continue_install

:python_version_error
echo [ERROR] Se requiere Python 3.9 o superior
echo         Version actual: %PYTHON_VERSION%
goto :error

:continue_install

REM ============================================================================
REM 3. VERIFICAR PIP
REM ============================================================================
echo.
echo [PASO 3/8] Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip no esta disponible
    goto :error
)
echo [OK] pip esta disponible

echo [*] Actualizando pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] No se pudo actualizar pip, continuando...
) else (
    echo [OK] pip actualizado
)

REM ============================================================================
REM 4. CREAR ENTORNO VIRTUAL
REM ============================================================================
echo.
echo [PASO 4/8] Configurando entorno virtual...

if exist "venv" (
    echo [*] Entorno virtual existente detectado
    set /p RECREATE="Deseas recrear el entorno virtual? (s/N): "
    if /i "!RECREATE!"=="s" (
        echo [*] Eliminando entorno virtual anterior...
        rmdir /s /q venv
        echo [*] Creando nuevo entorno virtual...
        python -m venv venv
        if errorlevel 1 goto :error
        echo [OK] Entorno virtual recreado
    ) else (
        echo [*] Usando entorno virtual existente
    )
) else (
    echo [*] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 goto :error
    echo [OK] Entorno virtual creado
)

echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 goto :error
echo [OK] Entorno virtual activado

REM ============================================================================
REM 5. INSTALAR DEPENDENCIAS
REM ============================================================================
echo.
echo [PASO 5/8] Instalando dependencias...
echo [*] Esto puede tomar varios minutos...

python -m pip install --upgrade pip setuptools wheel --quiet

echo [*] Instalando dependencias desde requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error
echo [OK] Dependencias principales instaladas

echo [*] Instalando paquete en modo desarrollo...
python -m pip install -e . 2>nul
if errorlevel 1 (
    python -m pip install -e .[dev] 2>nul
)
echo [OK] Instalacion de dependencias completada

REM ============================================================================
REM 6. CREAR ESTRUCTURA DE DIRECTORIOS
REM ============================================================================
echo.
echo [PASO 6/8] Creando estructura de directorios...

if not exist "data" mkdir data
if not exist "var\logs" mkdir var\logs
if not exist "var\config" mkdir var\config
if not exist "tmp\logs" mkdir tmp\logs

echo [OK] Estructura de directorios lista

REM ============================================================================
REM 7. CONFIGURACION INICIAL
REM ============================================================================
echo.
echo [PASO 7/8] Configurando proyecto...

if not exist ".env" (
    echo [*] Creando archivo .env...
    (
        echo # Configuracion de API Keys - Analizador Bursatil
        echo.
        echo # Tiingo API Key (opcional)
        echo #TIINGO_API_KEY=tu_api_key_aqui
        echo.
        echo LOG_LEVEL=INFO
        echo CACHE_ENABLED=true
        echo CACHE_TTL=300
    ) > .env
    echo [OK] Archivo .env creado
) else (
    echo [OK] Archivo .env ya existe
)

if not exist "var\config\portfolio.json" (
    echo [*] Creando configuracion de portfolio...
    echo {"symbols":["AAPL","MSFT","GOOGL","TSLA","AMZN"],"weights":[0.2,0.2,0.2,0.2,0.2],"initial_investment":10000} > var\config\portfolio.json
    echo [OK] Configuracion de portfolio creada
)

if not exist "ejemplos" mkdir ejemplos
if not exist "ejemplos\symbols.txt" (
    (
        echo AAPL
        echo MSFT
        echo GOOGL
        echo TSLA
        echo AMZN
    ) > ejemplos\symbols.txt
)

echo [OK] Configuracion inicial completada

REM ============================================================================
REM 8. VERIFICACION
REM ============================================================================
echo.
echo [PASO 8/8] Verificacion de instalacion...
echo.
set /p RUN_TESTS="Deseas ejecutar los tests? (s/N): "

if /i "!RUN_TESTS!"=="s" (
    echo.
    echo [*] Ejecutando tests...
    python -m pytest tests/ -v --tb=short
    if errorlevel 1 (
        echo [WARNING] Algunos tests fallaron
    ) else (
        echo [OK] Tests completados
    )
) else (
    echo [*] Tests omitidos
)

REM ============================================================================
REM INSTALACION COMPLETADA
REM ============================================================================
echo.
echo ========================================================================
echo     INSTALACION COMPLETADA EXITOSAMENTE
echo ========================================================================
echo.
echo Para ejecutar la aplicacion:
echo   1. Activar entorno virtual: venv\Scripts\activate
echo   2. Ejecutar: python run_app.py
echo   3. O usar: run_app.bat
echo.
echo La aplicacion se abrira en http://localhost:8501
echo.
echo ========================================================================
echo.
set /p RUN_NOW="Deseas ejecutar la aplicacion ahora? (s/N): "
if /i "!RUN_NOW!"=="s" (
    echo.
    echo [*] Iniciando aplicacion...
    python run_app.py
)

goto :end

REM ============================================================================
REM MANEJO DE ERRORES
REM ============================================================================
:error
echo.
echo ========================================================================
echo     ERROR EN LA INSTALACION
echo ========================================================================
echo.
echo La instalacion no se pudo completar.
echo.
echo Soluciones:
echo   1. Verifica que Python 3.9+ este instalado
echo   2. Ejecuta este script desde CMD de Windows (no Git Bash)
echo   3. Verifica tu conexion a Internet
echo   4. Consulta README.md para mas ayuda
echo.
echo ========================================================================
echo.
pause
exit /b 1

:end
echo.
pause
endlocal
