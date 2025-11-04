@echo off
REM ============================================================================
REM Script de Instalacion Completa - Analizador Bursatil
REM Instala Python, entorno virtual, dependencias y configura todo desde cero
REM ============================================================================

setlocal EnableDelayedExpansion

echo.
echo ========================================================================
echo     INSTALADOR COMPLETO - ANALIZADOR BURSATIL
echo ========================================================================
echo.
echo Este script instalara y configurara todo lo necesario para ejecutar
echo el Analizador Bursatil desde cero.
echo.
echo Presiona cualquier tecla para continuar o Ctrl+C para cancelar...
pause >nul

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
REM 2. VERIFICAR/INSTALAR PYTHON
REM ============================================================================
echo.
echo [PASO 2/8] Verificando Python...

REM Intentar detectar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python no esta instalado o no esta en el PATH
    echo.
    echo OPCIONES DE INSTALACION DE PYTHON:
    echo.
    echo 1. Descargar Python manualmente:
    echo    - Ve a: https://www.python.org/downloads/
    echo    - Descarga Python 3.10 o superior
    echo    - IMPORTANTE: Marca "Add Python to PATH" durante la instalacion
    echo.
    echo 2. Instalar con winget (Windows 11):
    echo    - Abre otra terminal como Administrador
    echo    - Ejecuta: winget install Python.Python.3.12
    echo.
    echo 3. Instalar con Chocolatey:
    echo    - Si tienes Chocolatey: choco install python
    echo.
    echo.
    echo Despues de instalar Python, vuelve a ejecutar este script.
    goto :error
)

REM Obtener version de Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detectado

REM Verificar version minima de Python (3.9+)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)
if %PYTHON_MAJOR% LSS 3 (
    echo [ERROR] Se requiere Python 3.9 o superior. Version actual: %PYTHON_VERSION%
    goto :error
)
if %PYTHON_MAJOR%==3 if %PYTHON_MINOR% LSS 9 (
    echo [ERROR] Se requiere Python 3.9 o superior. Version actual: %PYTHON_VERSION%
    goto :error
)
echo [OK] Version de Python compatible

REM ============================================================================
REM 3. VERIFICAR/ACTUALIZAR PIP
REM ============================================================================
echo.
echo [PASO 3/8] Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] pip no esta disponible, intentando instalarlo...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo [ERROR] No se pudo instalar pip
        goto :error
    )
)
echo [OK] pip esta disponible

echo [*] Actualizando pip a la ultima version...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] No se pudo actualizar pip, continuando con la version actual...
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
    set /p RECREATE="¿Deseas recrear el entorno virtual? (s/N): "
    if /i "!RECREATE!"=="s" (
        echo [*] Eliminando entorno virtual anterior...
        rmdir /s /q venv
        echo [*] Creando nuevo entorno virtual...
        python -m venv venv
        if errorlevel 1 (
            echo [ERROR] No se pudo crear el entorno virtual
            goto :error
        )
        echo [OK] Entorno virtual recreado
    ) else (
        echo [*] Usando entorno virtual existente
    )
) else (
    echo [*] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        goto :error
    )
    echo [OK] Entorno virtual creado
)

REM Activar entorno virtual
echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    goto :error
)
echo [OK] Entorno virtual activado

REM ============================================================================
REM 5. INSTALAR DEPENDENCIAS
REM ============================================================================
echo.
echo [PASO 5/8] Instalando dependencias...
echo [*] Esto puede tomar varios minutos...

REM Actualizar pip en el entorno virtual
python -m pip install --upgrade pip setuptools wheel --quiet

REM Instalar dependencias principales desde requirements.txt
echo [*] Instalando dependencias desde requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Error instalando dependencias desde requirements.txt
    goto :error
)
echo [OK] Dependencias principales instaladas

REM Instalar el paquete en modo desarrollo
echo [*] Instalando paquete en modo desarrollo...
python -m pip install -e .
if errorlevel 1 (
    echo [WARNING] Error instalando en modo desarrollo, intentando metodo alternativo...
    python -m pip install -e .[dev] 2>nul
    if errorlevel 1 (
        echo [WARNING] No se pudo instalar en modo desarrollo, pero las dependencias estan instaladas
    )
)
echo [OK] Instalacion de dependencias completada

REM ============================================================================
REM 6. CREAR ESTRUCTURA DE DIRECTORIOS
REM ============================================================================
echo.
echo [PASO 6/8] Creando estructura de directorios...

REM Crear directorios necesarios si no existen
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

REM Crear archivo .env de ejemplo si no existe
if not exist ".env" (
    echo [*] Creando archivo .env de ejemplo...
    (
        echo # Configuracion de API Keys - Analizador Bursatil
        echo # Renombra este archivo a .env y configura tus API keys
        echo.
        echo # Tiingo API Key ^(opcional - para fuente Tiingo^)
        echo # Registrate gratis en: https://www.tiingo.com/
        echo #TIINGO_API_KEY=tu_api_key_aqui
        echo.
        echo # Configuracion de logging
        echo LOG_LEVEL=INFO
        echo.
        echo # Configuracion de cache
        echo CACHE_ENABLED=true
        echo CACHE_TTL=300
    ) > .env.example
    copy .env.example .env >nul 2>&1
    echo [OK] Archivo .env creado
) else (
    echo [OK] Archivo .env ya existe
)

REM Crear configuracion de portfolio por defecto si no existe
if not exist "var\config\portfolio.json" (
    echo [*] Creando configuracion de portfolio por defecto...
    (
        echo {
        echo   "symbols"^: ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"],
        echo   "weights"^: [0.2, 0.2, 0.2, 0.2, 0.2],
        echo   "initial_investment"^: 10000
        echo }
    ) > var\config\portfolio.json
    echo [OK] Configuracion de portfolio creada
)

REM Crear archivo de simbolos de ejemplo
if not exist "ejemplos\symbols.txt" (
    echo [*] Verificando archivos de ejemplo...
    if not exist "ejemplos" mkdir ejemplos
    (
        echo AAPL
        echo MSFT
        echo GOOGL
        echo TSLA
        echo AMZN
    ) > ejemplos\symbols.txt
    echo [OK] Archivos de ejemplo verificados
)

echo [OK] Configuracion inicial completada

REM ============================================================================
REM 8. VERIFICAR INSTALACION (TESTS OPCIONALES)
REM ============================================================================
echo.
echo [PASO 8/8] Verificacion de instalacion...
echo.
set /p RUN_TESTS="¿Deseas ejecutar los tests para verificar la instalacion? (s/N): "

if /i "!RUN_TESTS!"=="s" (
    echo.
    echo [*] Ejecutando tests...
    python -m pytest tests/ -v --tb=short
    if errorlevel 1 (
        echo [WARNING] Algunos tests fallaron
        echo           La instalacion puede estar correcta de todas formas
        echo           Revisa los logs para mas detalles
    ) else (
        echo [OK] Todos los tests pasaron exitosamente
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
echo El entorno esta listo para usar. A continuacion:
echo.
echo PARA EJECUTAR LA APLICACION:
echo   1. Activar el entorno virtual:  venv\Scripts\activate
echo   2. Ejecutar la aplicacion:      python run_app.py
echo   3. Abrir en navegador:          http://localhost:8501
echo.
echo ARCHIVOS DE INICIO RAPIDO:
echo   - .\run_app.bat           : Ejecuta la aplicacion directamente
echo   - .\README.md             : Documentacion completa
echo   - .\QUICKSTART.md         : Guia de inicio rapido
echo   - .\.env                  : Configuracion de API keys
echo   - .\ejemplos\             : Archivos de ejemplo
echo.
echo FUENTES DE DATOS DISPONIBLES:
echo   - Yahoo Finance    : Acciones, ETFs (no requiere API key)
echo   - Binance          : Criptomonedas (no requiere API key)
echo   - Tiingo           : Acciones (requiere API key gratuita)
echo.
echo Para configurar Tiingo:
echo   1. Registrate en: https://www.tiingo.com/
echo   2. Edita .env y agrega tu API key
echo   3. Ver: CONFIGURACION_API_KEYS.md para mas detalles
echo.
echo ========================================================================
echo.
echo ¿Deseas ejecutar la aplicacion ahora? (s/N):
set /p RUN_NOW=
if /i "!RUN_NOW!"=="s" (
    echo.
    echo [*] Iniciando aplicacion...
    echo [*] Abriendo navegador en http://localhost:8501
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
echo SOLUCIONES COMUNES:
echo   1. Verifica que Python 3.9+ este instalado:
echo      python --version
echo.
echo   2. Asegurate de tener permisos de escritura en este directorio
echo.
echo   3. Verifica tu conexion a Internet (necesaria para descargar paquetes)
echo.
echo   4. Si el problema persiste:
echo      - Revisa los logs en var\logs\
echo      - Consulta README.md
echo      - Abre un issue en GitHub
echo.
echo ========================================================================
echo.
pause
exit /b 1

:end
echo.
pause
endlocal
