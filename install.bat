@echo off
REM Script de instalacion automatica para Windows
REM Instala todas las dependencias y configura el entorno de desarrollo

echo === Instalador del Analizador Bursatil ===
echo ================================================

REM Verificar que estamos en el directorio correcto
if not exist "pyproject.toml" (
    echo [ERROR] No se encontro pyproject.toml
    echo    Asegurate de ejecutar este script desde el directorio del proyecto
    pause
    exit /b 1
)

REM Verificar Python
echo [*] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo    Instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python esta disponible

REM Verificar pip
echo [*] Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip no esta disponible
    echo    Instala pip desde: https://pip.pypa.io/en/stable/installation/
    pause
    exit /b 1
)
echo [OK] pip esta disponible

REM Actualizar pip
echo [*] Actualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Error actualizando pip
    pause
    exit /b 1
)
echo [OK] pip actualizado

REM Instalar dependencias
echo [*] Instalando dependencias del proyecto...
python -m pip install -e .[dev]
if errorlevel 1 (
    echo [ERROR] Error instalando dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

REM Ejecutar tests
echo [*] Ejecutando tests...
python -m pytest tests/ -v
if errorlevel 1 (
    echo [WARNING] Algunos tests fallaron, pero la instalacion puede estar correcta
) else (
    echo [OK] Todos los tests pasaron
)

REM Crear archivo de configuracion de ejemplo
echo [*] Creando configuracion de ejemplo...
(
echo # Configuracion de ejemplo para el Analizador Bursatil
echo # Copia este archivo como 'config.yaml' y modifica segun tus necesidades
echo.
echo # Configuracion por defecto
echo default:
echo   source: "yahoo"  # yahoo, binance, tiingo
echo   interval: "1d"   # 1d, 1h, 1wk, 1mo
echo   start_date: "2023-01-01"
echo   end_date: "2024-01-01"
echo.
echo # Simbolos recomendados por fuente
echo symbols:
echo   yahoo:
echo     - "AAPL"
echo     - "MSFT" 
echo     - "GOOGL"
echo     - "TSLA"
echo     - "AMZN"
echo.
echo   binance:
echo     - "BTCUSDT"
echo     - "ETHUSDT"
echo     - "ADAUSDT"
echo     - "SOLUSDT"
echo     - "DOTUSDT"
echo.
echo   tiingo:
echo     - "AAPL"
echo     - "MSFT"
echo     - "GOOGL"
echo     - "BP"
echo     # Nota: Requiere API key gratuita de tiingo.com
echo     # Configura: set TIINGO_API_KEY=tu_key_aqui
echo.
echo # Configuracion de Monte Carlo
echo monte_carlo:
echo   simulations: 1000
echo   time_horizon: 252
echo   dynamic_volatility: false
) > config_example.yaml
echo [OK] Archivo config_example.yaml creado

echo.
echo [OK] Instalacion completada exitosamente!
echo.
echo Proximos pasos:
echo    1. Ejecutar la app: python run_app.py
echo    2. Abrir navegador: http://localhost:8501
echo    3. Configurar simbolos y fechas
echo    4. Empezar a analizar!
echo.
echo Documentacion:
echo    - README.md: Guia completa de uso
echo    - ARCHITECTURE.md: Documentacion tecnica
echo    - config_example.yaml: Configuracion de ejemplo
echo.
pause
