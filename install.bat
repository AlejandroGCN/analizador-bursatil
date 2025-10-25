@echo off
REM Script de instalación automática para Windows
REM Instala todas las dependencias y configura el entorno de desarrollo

echo 🚀 Instalador del Analizador Bursátil
echo ================================================

REM Verificar que estamos en el directorio correcto
if not exist "pyproject.toml" (
    echo ❌ No se encontró pyproject.toml
    echo    Asegúrate de ejecutar este script desde el directorio del proyecto
    pause
    exit /b 1
)

REM Verificar Python
echo 🐍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    echo    Instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python está disponible

REM Verificar pip
echo 📦 Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no está disponible
    echo    Instala pip desde: https://pip.pypa.io/en/stable/installation/
    pause
    exit /b 1
)
echo ✅ pip está disponible

REM Actualizar pip
echo 🔄 Actualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Error actualizando pip
    pause
    exit /b 1
)
echo ✅ pip actualizado

REM Instalar dependencias
echo 📦 Instalando dependencias del proyecto...
python -m pip install -e .[dev]
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

REM Ejecutar tests
echo 🧪 Ejecutando tests...
python -m pytest tests/ -v
if errorlevel 1 (
    echo ⚠️  Algunos tests fallaron, pero la instalación puede estar correcta
) else (
    echo ✅ Todos los tests pasaron
)

REM Crear archivo de configuración de ejemplo
echo 📝 Creando configuración de ejemplo...
(
echo # Configuración de ejemplo para el Analizador Bursátil
echo # Copia este archivo como 'config.yaml' y modifica según tus necesidades
echo.
echo # Configuración por defecto
echo default:
echo   source: "yahoo"  # yahoo, binance, stooq
echo   interval: "1d"   # 1d, 1h, 1wk, 1mo
echo   start_date: "2023-01-01"
echo   end_date: "2024-01-01"
echo.
echo # Símbolos recomendados por fuente
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
echo   stooq:
echo     - "AAPL.US"
echo     - "MSFT.US"
echo     - "GOOGL.US"
echo.
echo # Configuración de Monte Carlo
echo monte_carlo:
echo   simulations: 1000
echo   time_horizon: 252
echo   dynamic_volatility: false
) > config_example.yaml
echo ✅ Archivo config_example.yaml creado

echo.
echo 🎉 ¡Instalación completada exitosamente!
echo.
echo 📋 Próximos pasos:
echo    1. Ejecutar la app: python run_app.py
echo    2. Abrir navegador: http://localhost:8501
echo    3. Configurar símbolos y fechas
echo    4. ¡Empezar a analizar!
echo.
echo 📚 Documentación:
echo    - README.md: Guía completa de uso
echo    - ARCHITECTURE.md: Documentación técnica
echo    - config_example.yaml: Configuración de ejemplo
echo.
pause
