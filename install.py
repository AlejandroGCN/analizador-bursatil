#!/usr/bin/env python3
"""
Script de instalación automática para el Analizador Bursátil
Instala todas las dependencias y configura el entorno de desarrollo
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        print(f"   Comando: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python {version.major}.{version.minor} no es compatible")
        print("   Se requiere Python 3.10 o superior")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} es compatible")
    return True

def check_pip():
    """Verifica que pip esté disponible"""
    print("📦 Verificando pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        print("✅ pip está disponible")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip no está disponible")
        print("   Instala pip desde: https://pip.pypa.io/en/stable/installation/")
        return False

def install_dependencies():
    """Instala las dependencias del proyecto"""
    print("📦 Instalando dependencias...")
    
    # Actualizar pip primero
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Actualizando pip"):
        return False
    
    # Instalar el proyecto en modo desarrollo
    if not run_command(f"{sys.executable} -m pip install -e .[dev]", "Instalando dependencias del proyecto"):
        return False
    
    return True

def run_tests():
    """Ejecuta los tests para verificar la instalación"""
    print("🧪 Ejecutando tests...")
    if run_command(f"{sys.executable} -m pytest tests/ -v", "Ejecutando tests"):
        print("✅ Todos los tests pasaron")
        return True
    else:
        print("⚠️  Algunos tests fallaron, pero la instalación puede estar correcta")
        return True  # No fallar la instalación por tests

def create_sample_config():
    """Crea un archivo de configuración de ejemplo"""
    print("📝 Creando configuración de ejemplo...")
    
    sample_config = """# Configuración de ejemplo para el Analizador Bursátil
# Copia este archivo como 'config.yaml' y modifica según tus necesidades

# Configuración por defecto
default:
  source: "yahoo"  # yahoo, binance, stooq
  interval: "1d"   # 1d, 1h, 1wk, 1mo
  start_date: "2023-01-01"
  end_date: "2024-01-01"
  
# Símbolos recomendados por fuente
symbols:
  yahoo:
    - "AAPL"
    - "MSFT" 
    - "GOOGL"
    - "TSLA"
    - "AMZN"
  
  binance:
    - "BTCUSDT"
    - "ETHUSDT"
    - "ADAUSDT"
    - "SOLUSDT"
    - "DOTUSDT"
  
  stooq:
    - "AAPL.US"
    - "MSFT.US"
    - "GOOGL.US"

# Configuración de Monte Carlo
monte_carlo:
  simulations: 1000
  time_horizon: 252
  dynamic_volatility: false
"""
    
    try:
        with open("config_example.yaml", "w", encoding="utf-8") as f:
            f.write(sample_config)
        print("✅ Archivo config_example.yaml creado")
        return True
    except Exception as e:
        print(f"⚠️  No se pudo crear config_example.yaml: {e}")
        return True  # No fallar por esto

def main():
    """Función principal de instalación"""
    print("🚀 Instalador del Analizador Bursátil")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not Path("pyproject.toml").exists():
        print("❌ No se encontró pyproject.toml")
        print("   Asegúrate de ejecutar este script desde el directorio del proyecto")
        return False
    
    # Verificaciones previas
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Instalación
    if not install_dependencies():
        return False
    
    # Verificaciones post-instalación
    run_tests()
    create_sample_config()
    
    print("\n🎉 ¡Instalación completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("   1. Ejecutar la app: python run_app.py")
    print("   2. Abrir navegador: http://localhost:8501")
    print("   3. Configurar símbolos y fechas")
    print("   4. ¡Empezar a analizar!")
    
    print("\n📚 Documentación:")
    print("   - README.md: Guía completa de uso")
    print("   - ARCHITECTURE.md: Documentación técnica")
    print("   - config_example.yaml: Configuración de ejemplo")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
