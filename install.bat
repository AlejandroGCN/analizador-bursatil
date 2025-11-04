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
REM 2. VERIFICAR PYTHON Y DETECTAR VERSIONES
REM ============================================================================
echo.
echo [PASO 2/8] Verificando Python...

REM Intentar detectar Python en el PATH
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo.
    echo SOLUCION: Instalar Python 3.12 automaticamente
    echo.
    set /p AUTO_INSTALL="Deseas instalar Python 3.12 ahora con winget? (s/N): "
    if /i "!AUTO_INSTALL!"=="s" (
        echo.
        echo [*] Instalando Python 3.12...
        winget install Python.Python.3.12 -e --silent --accept-package-agreements
        if errorlevel 1 (
            echo [ERROR] No se pudo instalar Python automaticamente
            echo         Instalalo manualmente desde: https://www.python.org/downloads/
            goto :error
        )
        echo [OK] Python 3.12 instalado
        echo [*] Reinicia este script para continuar
        pause
        exit /b 0
    ) else (
        echo.
        echo Por favor instala Python 3.12 manualmente:
        echo   winget install Python.Python.3.12
        echo O descarga desde: https://www.python.org/downloads/
        goto :error
    )
)

REM Detectar version de Python en uso
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detectado

REM Buscar versiones alternativas de Python en el sistema
echo [*] Buscando versiones de Python instaladas...
set PYTHON_CMD=python
set FOUND_312=0
set FOUND_311=0

REM Intentar encontrar python3.12
python3.12 --version >nul 2>&1
if not errorlevel 1 (
    echo [*] Python 3.12 encontrado ^(python3.12^)
    set FOUND_312=1
)

REM Intentar encontrar python3.11
python3.11 --version >nul 2>&1
if not errorlevel 1 (
    echo [*] Python 3.11 encontrado ^(python3.11^)
    set FOUND_311=1
)

REM Buscar en Program Files
if exist "C:\Program Files\Python312\python.exe" (
    echo [*] Python 3.12 encontrado en Program Files
    set FOUND_312=1
)

if exist "C:\Program Files\Python311\python.exe" (
    echo [*] Python 3.11 encontrado en Program Files
    set FOUND_311=1
)

REM Verificar version minima y maxima recomendada
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

REM Verificar version minima (3.9+)
if %PYTHON_MAJOR% LSS 3 goto :python_version_error
if %PYTHON_MAJOR%==3 if %PYTHON_MINOR% LSS 9 goto :python_version_error

REM Advertir sobre versiones muy nuevas (3.13+)
if %PYTHON_MAJOR%==3 if %PYTHON_MINOR% GEQ 13 (
    echo.
    echo [WARNING] Python %PYTHON_VERSION% detectado - VERSION MUY NUEVA
    echo.
    echo Algunas dependencias pueden fallar al instalarse porque:
    echo - pyarrow, numpy y otras librerias cientificas aun no tienen
    echo   versiones precompiladas para Python 3.13+
    echo.
    
    REM Ofrecer alternativas si se encontraron versiones compatibles
    if !FOUND_312!==1 (
        echo SOLUCION: Se encontro Python 3.12 en tu sistema
        echo.
        set /p USE_312="Deseas usar Python 3.12 en su lugar? (S/n): "
        if /i not "!USE_312!"=="n" (
            if exist "C:\Program Files\Python312\python.exe" (
                set PYTHON_CMD="C:\Program Files\Python312\python.exe"
            ) else (
                set PYTHON_CMD=python3.12
            )
            echo [OK] Usando Python 3.12
            goto :continue_install
        )
    ) else if !FOUND_311!==1 (
        echo SOLUCION: Se encontro Python 3.11 en tu sistema
        echo.
        set /p USE_311="Deseas usar Python 3.11 en su lugar? (S/n): "
        if /i not "!USE_311!"=="n" (
            if exist "C:\Program Files\Python311\python.exe" (
                set PYTHON_CMD="C:\Program Files\Python311\python.exe"
            ) else (
                set PYTHON_CMD=python3.11
            )
            echo [OK] Usando Python 3.11
            goto :continue_install
        )
    ) else (
        echo SOLUCION: Instalar Python 3.12 en paralelo
        echo.
        set /p INSTALL_312="Deseas instalar Python 3.12 ahora? (s/N): "
        if /i "!INSTALL_312!"=="s" (
            echo.
            echo [*] Instalando Python 3.12 con winget...
            winget install Python.Python.3.12 -e --silent --accept-package-agreements
            if errorlevel 1 (
                echo [ERROR] No se pudo instalar automaticamente
            ) else (
                echo [OK] Python 3.12 instalado
                echo [*] Reinicia este script para usarlo
                pause
                exit /b 0
            )
        )
    )
    
    echo.
    echo Opciones restantes:
    echo   1. Cancelar e instalar Python 3.12 manualmente
    echo   2. Continuar con Python %PYTHON_VERSION% ^(PUEDE FALLAR^)
    echo.
    set /p CONTINUE="Deseas continuar de todos modos? (s/N): "
    if /i not "!CONTINUE!"=="s" (
        echo.
        echo Instalacion cancelada.
        echo Instala Python 3.12: winget install Python.Python.3.12
        goto :error
    )
    echo.
    echo [*] Continuando con Python %PYTHON_VERSION% ^(puede haber errores^)...
)

echo [OK] Version de Python compatible
goto :continue_install

:python_version_error
echo [ERROR] Se requiere Python 3.9 o superior
echo         Version actual: %PYTHON_VERSION%
echo.
echo Instala Python 3.12 con: winget install Python.Python.3.12
goto :error

:continue_install

REM ============================================================================
REM 3. VERIFICAR PIP
REM ============================================================================
echo.
echo [PASO 3/8] Verificando pip...
%PYTHON_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip no esta disponible
    goto :error
)
echo [OK] pip esta disponible

echo [*] Actualizando pip...
%PYTHON_CMD% -m pip install --upgrade pip --quiet
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
        %PYTHON_CMD% -m venv venv
        if errorlevel 1 goto :error
        echo [OK] Entorno virtual recreado
    ) else (
        echo [*] Usando entorno virtual existente
    )
) else (
    echo [*] Creando entorno virtual...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 goto :error
    echo [OK] Entorno virtual creado
)

echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 goto :error
echo [OK] Entorno virtual activado

REM Una vez activado el venv, usar python del venv
set PYTHON_CMD=python

REM ============================================================================
REM 5. INSTALAR DEPENDENCIAS
REM ============================================================================
echo.
echo [PASO 5/8] Instalando dependencias...
echo [*] Esto puede tomar varios minutos...

%PYTHON_CMD% -m pip install --upgrade pip setuptools wheel --quiet

echo [*] Instalando dependencias desde requirements.txt...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 goto :error
echo [OK] Dependencias principales instaladas

echo [*] Instalando paquete en modo desarrollo...
%PYTHON_CMD% -m pip install -e . 2>nul
if errorlevel 1 (
    %PYTHON_CMD% -m pip install -e .[dev] 2>nul
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
    %PYTHON_CMD% -m pytest tests/ -v --tb=short
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
    %PYTHON_CMD% run_app.py
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
