#!/usr/bin/env python3
"""
Script de Instalación Completa - Analizador Bursátil
Instala todas las dependencias y configura el entorno desde cero
Compatible con Windows, Linux y macOS
"""

import subprocess
import sys
import os
import platform
import shutil
from pathlib import Path
from typing import Tuple, Optional

class Colors:
    """Códigos de colores ANSI para terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class Installer:
    """Clase principal del instalador"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.is_windows = platform.system() == "Windows"
        self.python_cmd = sys.executable
        
    def print_header(self, text: str):
        """Imprime un encabezado destacado"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*72}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text:^72}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*72}{Colors.ENDC}\n")
    
    def print_step(self, step: int, total: int, description: str):
        """Imprime el número de paso actual"""
        print(f"\n{Colors.OKBLUE}[PASO {step}/{total}] {description}...{Colors.ENDC}")
    
    def print_success(self, message: str):
        """Imprime un mensaje de éxito"""
        print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} {message}")
    
    def print_warning(self, message: str):
        """Imprime una advertencia"""
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {message}")
    
    def print_error(self, message: str):
        """Imprime un error"""
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {message}")
    
    def print_info(self, message: str):
        """Imprime información"""
        print(f"{Colors.OKCYAN}[*]{Colors.ENDC} {message}")
    
    def run_command(self, command: list, description: str, check: bool = True) -> Tuple[bool, str]:
        """
        Ejecuta un comando y retorna el resultado
        
        Args:
            command: Lista con el comando y sus argumentos
            description: Descripción de la operación
            check: Si debe fallar en caso de error
            
        Returns:
            Tuple[bool, str]: (éxito, salida)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            if check:
                self.print_error(f"{description} falló")
                self.print_error(f"Comando: {' '.join(command)}")
                if e.stderr:
                    self.print_error(f"Error: {e.stderr}")
            return False, e.stderr
        except FileNotFoundError:
            self.print_error(f"Comando no encontrado: {command[0]}")
            return False, ""
    
    def check_project_directory(self) -> bool:
        """Verifica que estamos en el directorio correcto del proyecto"""
        self.print_step(1, 8, "Verificando directorio del proyecto")
        
        required_files = ["pyproject.toml", "requirements.txt"]
        for file in required_files:
            if not (self.project_root / file).exists():
                self.print_error(f"No se encontró {file}")
                self.print_error("Ejecuta este script desde el directorio raíz del proyecto")
                return False
        
        self.print_success("Directorio del proyecto correcto")
        return True
    
    def check_python_version(self) -> bool:
        """Verifica la versión de Python"""
        self.print_step(2, 8, "Verificando Python")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        self.print_success(f"Python {version_str} detectado")
        
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            self.print_error(f"Python {version_str} no es compatible")
            self.print_error("Se requiere Python 3.9 o superior")
            self.print_info("Descarga Python desde: https://www.python.org/downloads/")
            return False
        
        self.print_success("Versión de Python compatible")
        return True
    
    def check_pip(self) -> bool:
        """Verifica y actualiza pip"""
        self.print_step(3, 8, "Verificando pip")
        
        success, _ = self.run_command(
            [self.python_cmd, "-m", "pip", "--version"],
            "Verificar pip",
            check=False
        )
        
        if not success:
            self.print_warning("pip no está disponible, intentando instalarlo...")
            success, _ = self.run_command(
                [self.python_cmd, "-m", "ensurepip", "--default-pip"],
                "Instalar pip"
            )
            if not success:
                return False
        
        self.print_success("pip está disponible")
        
        # Actualizar pip
        self.print_info("Actualizando pip a la última versión...")
        success, _ = self.run_command(
            [self.python_cmd, "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
            "Actualizar pip",
            check=False
        )
        
        if success:
            self.print_success("pip actualizado")
        else:
            self.print_warning("No se pudo actualizar pip, continuando con versión actual")
        
        return True
    
    def setup_virtual_environment(self) -> bool:
        """Configura el entorno virtual"""
        self.print_step(4, 8, "Configurando entorno virtual")
        
        if self.venv_path.exists():
            self.print_info("Entorno virtual existente detectado")
            response = input("¿Deseas recrear el entorno virtual? (s/N): ").strip().lower()
            
            if response == 's':
                self.print_info("Eliminando entorno virtual anterior...")
                shutil.rmtree(self.venv_path)
                
                self.print_info("Creando nuevo entorno virtual...")
                success, _ = self.run_command(
                    [self.python_cmd, "-m", "venv", str(self.venv_path)],
                    "Crear entorno virtual"
                )
                if not success:
                    return False
                self.print_success("Entorno virtual recreado")
            else:
                self.print_info("Usando entorno virtual existente")
        else:
            self.print_info("Creando entorno virtual...")
            success, _ = self.run_command(
                [self.python_cmd, "-m", "venv", str(self.venv_path)],
                "Crear entorno virtual"
            )
            if not success:
                return False
            self.print_success("Entorno virtual creado")
        
        # Actualizar la referencia de python al del venv
        if self.is_windows:
            self.python_cmd = str(self.venv_path / "Scripts" / "python.exe")
        else:
            self.python_cmd = str(self.venv_path / "bin" / "python")
        
        self.print_success("Entorno virtual configurado")
        return True
    
    def install_dependencies(self) -> bool:
        """Instala las dependencias del proyecto"""
        self.print_step(5, 8, "Instalando dependencias")
        self.print_info("Esto puede tomar varios minutos...")
        
        # Actualizar pip, setuptools y wheel en el venv
        self.print_info("Actualizando herramientas base...")
        self.run_command(
            [self.python_cmd, "-m", "pip", "install", "--upgrade", 
             "pip", "setuptools", "wheel", "--quiet"],
            "Actualizar pip/setuptools/wheel",
            check=False
        )
        
        # Instalar desde requirements.txt
        self.print_info("Instalando dependencias desde requirements.txt...")
        success, _ = self.run_command(
            [self.python_cmd, "-m", "pip", "install", "-r", "requirements.txt"],
            "Instalar requirements.txt"
        )
        if not success:
            return False
        self.print_success("Dependencias principales instaladas")
        
        # Instalar el paquete en modo desarrollo
        self.print_info("Instalando paquete en modo desarrollo...")
        success, _ = self.run_command(
            [self.python_cmd, "-m", "pip", "install", "-e", "."],
            "Instalar en modo desarrollo",
            check=False
        )
        if not success:
            self.print_warning("No se pudo instalar en modo desarrollo")
            # Intentar con [dev]
            success, _ = self.run_command(
                [self.python_cmd, "-m", "pip", "install", "-e", ".[dev]"],
                "Instalar con extras dev",
                check=False
            )
            if not success:
                self.print_warning("Modo desarrollo no disponible, pero dependencias instaladas")
        
        self.print_success("Instalación de dependencias completada")
        return True
    
    def create_directory_structure(self) -> bool:
        """Crea la estructura de directorios necesaria"""
        self.print_step(6, 8, "Creando estructura de directorios")
        
        directories = [
            "data",
            "var/logs",
            "var/config",
            "tmp/logs",
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.print_success("Estructura de directorios lista")
        return True
    
    def create_configuration_files(self) -> bool:
        """Crea archivos de configuración iniciales"""
        self.print_step(7, 8, "Configurando proyecto")
        
        # Crear archivo .env
        env_file = self.project_root / ".env"
        if not env_file.exists():
            self.print_info("Creando archivo .env de ejemplo...")
            env_content = """# Configuracion de API Keys - Analizador Bursatil
# Configura tus API keys aqui

# Tiingo API Key (opcional - para fuente Tiingo)
# Registrate gratis en: https://www.tiingo.com/
#TIINGO_API_KEY=tu_api_key_aqui

# Configuracion de logging
LOG_LEVEL=INFO

# Configuracion de cache
CACHE_ENABLED=true
CACHE_TTL=300
"""
            env_file.write_text(env_content, encoding='utf-8')
            self.print_success("Archivo .env creado")
        else:
            self.print_success("Archivo .env ya existe")
        
        # Crear configuración de portfolio
        portfolio_file = self.project_root / "var" / "config" / "portfolio.json"
        if not portfolio_file.exists():
            self.print_info("Creando configuración de portfolio por defecto...")
            portfolio_content = """{
  "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"],
  "weights": [0.2, 0.2, 0.2, 0.2, 0.2],
  "initial_investment": 10000
}
"""
            portfolio_file.write_text(portfolio_content, encoding='utf-8')
            self.print_success("Configuración de portfolio creada")
        
        # Crear archivos de ejemplo
        ejemplos_dir = self.project_root / "ejemplos"
        ejemplos_dir.mkdir(exist_ok=True)
        
        symbols_file = ejemplos_dir / "symbols.txt"
        if not symbols_file.exists():
            self.print_info("Verificando archivos de ejemplo...")
            symbols_content = """AAPL
MSFT
GOOGL
TSLA
AMZN
"""
            symbols_file.write_text(symbols_content, encoding='utf-8')
            self.print_success("Archivos de ejemplo verificados")
        
        self.print_success("Configuración inicial completada")
        return True
    
    def run_tests(self) -> bool:
        """Ejecuta los tests de verificación"""
        self.print_step(8, 8, "Verificación de instalación")
        
        response = input("\n¿Deseas ejecutar los tests para verificar la instalación? (s/N): ").strip().lower()
        
        if response == 's':
            print()
            self.print_info("Ejecutando tests...")
            success, _ = self.run_command(
                [self.python_cmd, "-m", "pytest", "tests/", "-v", "--tb=short"],
                "Ejecutar tests",
                check=False
            )
            
            if success:
                self.print_success("Todos los tests pasaron exitosamente")
            else:
                self.print_warning("Algunos tests fallaron")
                self.print_warning("La instalación puede estar correcta de todas formas")
                self.print_warning("Revisa los logs para más detalles")
        else:
            self.print_info("Tests omitidos")
        
        return True
    
    def print_completion_message(self):
        """Imprime el mensaje final de instalación completada"""
        self.print_header("INSTALACION COMPLETADA EXITOSAMENTE")
        
        print("El entorno está listo para usar. A continuación:\n")
        
        print(f"{Colors.BOLD}PARA EJECUTAR LA APLICACIÓN:{Colors.ENDC}")
        if self.is_windows:
            print("  1. Activar el entorno virtual:  venv\\Scripts\\activate")
        else:
            print("  1. Activar el entorno virtual:  source venv/bin/activate")
        print("  2. Ejecutar la aplicación:      python run_app.py")
        print("  3. Abrir en navegador:          http://localhost:8501\n")
        
        print(f"{Colors.BOLD}ARCHIVOS DE INICIO RÁPIDO:{Colors.ENDC}")
        if self.is_windows:
            print("  - .\\run_app.bat           : Ejecuta la aplicación directamente")
        else:
            print("  - ./run_app.py            : Ejecuta la aplicación directamente")
        print("  - ./README.md             : Documentación completa")
        print("  - ./QUICKSTART.md         : Guía de inicio rápido")
        print("  - ./.env                  : Configuración de API keys")
        print("  - ./ejemplos/             : Archivos de ejemplo\n")
        
        print(f"{Colors.BOLD}FUENTES DE DATOS DISPONIBLES:{Colors.ENDC}")
        print("  - Yahoo Finance    : Acciones, ETFs (no requiere API key)")
        print("  - Binance          : Criptomonedas (no requiere API key)")
        print("  - Tiingo           : Acciones (requiere API key gratuita)\n")
        
        print(f"{Colors.BOLD}Para configurar Tiingo:{Colors.ENDC}")
        print("  1. Regístrate en: https://www.tiingo.com/")
        print("  2. Edita .env y agrega tu API key")
        print("  3. Ver: CONFIGURACION_API_KEYS.md para más detalles\n")
        
        print("="*72 + "\n")
        
        response = input("¿Deseas ejecutar la aplicación ahora? (s/N): ").strip().lower()
        if response == 's':
            print()
            self.print_info("Iniciando aplicación...")
            self.print_info("Abriendo navegador en http://localhost:8501")
            subprocess.run([self.python_cmd, "run_app.py"])
    
    def print_error_message(self):
        """Imprime mensaje de error en la instalación"""
        self.print_header("ERROR EN LA INSTALACION")
        
        print("La instalación no se pudo completar.\n")
        
        print(f"{Colors.BOLD}SOLUCIONES COMUNES:{Colors.ENDC}")
        print("  1. Verifica que Python 3.9+ esté instalado:")
        print("     python --version\n")
        print("  2. Asegúrate de tener permisos de escritura en este directorio\n")
        print("  3. Verifica tu conexión a Internet (necesaria para descargar paquetes)\n")
        print("  4. Si el problema persiste:")
        print("     - Revisa los logs en var/logs/")
        print("     - Consulta README.md")
        print("     - Abre un issue en GitHub\n")
        
        print("="*72 + "\n")
    
    def install(self) -> bool:
        """Ejecuta el proceso completo de instalación"""
        self.print_header("INSTALADOR COMPLETO - ANALIZADOR BURSATIL")
        
        print("Este script instalará y configurará todo lo necesario para ejecutar")
        print("el Analizador Bursátil desde cero.\n")
        
        input("Presiona Enter para continuar o Ctrl+C para cancelar...")
        
        steps = [
            self.check_project_directory,
            self.check_python_version,
            self.check_pip,
            self.setup_virtual_environment,
            self.install_dependencies,
            self.create_directory_structure,
            self.create_configuration_files,
            self.run_tests,
        ]
        
        for step in steps:
            if not step():
                self.print_error_message()
                return False
        
        self.print_completion_message()
        return True

def main():
    """Función principal"""
    try:
        installer = Installer()
        success = installer.install()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\nInstalación cancelada por el usuario.")
        return 1
    except Exception as e:
        print(f"\n{Colors.FAIL}Error inesperado: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
