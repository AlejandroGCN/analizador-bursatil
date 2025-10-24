#!/usr/bin/env python3
"""
Script de inicio para la aplicación Streamlit del Analizador Bursátil
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    """Ejecuta la aplicación Streamlit."""
    # Obtener el directorio del script (directorio raíz del proyecto)
    script_dir = Path(__file__).parent
    src_dir = script_dir / "src"
    
    # Ruta al dashboard
    dashboard_path = src_dir / "ui" / "dashboard.py"
    
    if not dashboard_path.exists():
        print("Error: No se encontro dashboard.py")
        print(f"   Buscando en: {dashboard_path}")
        sys.exit(1)
    
    # Configurar PYTHONPATH para que los imports funcionen
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    if str(src_dir) not in current_pythonpath.split(os.pathsep):
        os.environ["PYTHONPATH"] = f"{str(src_dir)}{os.pathsep}{current_pythonpath}"
    
    # Comando para ejecutar Streamlit usando py
    cmd = [
        "py", "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ]
    
    print("Iniciando Analizador Bursatil...")
    print(f"Dashboard: {dashboard_path}")
    print(f"Directorio de trabajo: {script_dir}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'No configurado')}")
    print("URL: http://localhost:8501")
    print("-" * 50)
    
    try:
        # Ejecutar desde el directorio raíz del proyecto
        subprocess.run(cmd, cwd=str(script_dir))
    except KeyboardInterrupt:
        print("\nAplicacion cerrada por el usuario")
    except FileNotFoundError:
        print("Error: Streamlit no esta instalado")
        print("   Instala con: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()