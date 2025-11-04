# Analizador Bursátil

Aplicación **Streamlit** para análisis financiero cuantitativo con descarga, normalización y visualización de datos bursátiles desde múltiples fuentes (Yahoo Finance, Binance, Tiingo).

**Características principales:**
- Extracción multi-fuente con arquitectura modular
- Simulación Monte Carlo para análisis de riesgo
- Sistema de logging profesional
- Gestión segura de API keys
- Visualizaciones interactivas

> 🚨 **IMPORTANTE - INSTALACIÓN EN WINDOWS**: 
> - Si usas `install.bat`: **Ejecútalo SOLO desde CMD de Windows** (no Git Bash)
> - Si tienes Python instalado: Usa `python install.py` que funciona en cualquier terminal
> - [Ver instrucciones detalladas de instalación](#-instalación-automática-completa-recomendado)

---

## Tabla de Contenidos

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Arquitectura](#arquitectura)
- [Sistema de Logging](#sistema-de-logging)
- [Documentación](#documentación)

---

## Requisitos

### 🐍 Versiones de Python Soportadas

| Versión Python | Estado | Recomendación |
|----------------|--------|---------------|
| **3.11** | ✅ Recomendado | Mejor compatibilidad y estabilidad |
| **3.12** | ✅ Recomendado | Versión actual estable |
| **3.10** | ✅ Soportado | Mínimo requerido |
| **3.9** | ⚠️ Compatible | Algunas librerías pueden ser antiguas |
| **3.13+** | ❌ No recomendado | Librerías pueden no estar actualizadas |

> ⚠️ **IMPORTANTE**: Si tienes Python 3.13 o superior, algunas dependencias (como `pyarrow`) pueden fallar al instalarse. Usa Python **3.11 o 3.12** para mejor experiencia.

- **Sistema operativo**: Windows, macOS, Linux
- **Dependencias**: Ver `requirements.txt`

### Dependencias principales

```
pandas>=2.0
numpy>=1.24
streamlit>=1.28
yfinance>=0.2
python-dotenv>=1.0.0
```

---

## Instalación

### 🚀 Instalación Automática Completa (Recomendado)

El instalador automático configura **todo lo necesario desde cero**, incluyendo:
- ✅ Verificación de Python 3.9+
- ✅ Creación de entorno virtual
- ✅ Instalación de todas las dependencias
- ✅ Configuración de estructura de directorios
- ✅ Archivos de configuración y ejemplos
- ✅ Tests de verificación (opcional)

---

#### 🪟 Opción A: Windows con `install.bat` (Plug & Play - Totalmente Automático)

```bash
# 1. Clonar el repositorio
git clone https://github.com/AlejandroGCN/analizador-bursatil.git
cd analizador-bursatil

# 2. Abrir CMD de Windows (NO Git Bash)
# Busca "cmd" en el menú de Windows o presiona Win+R y escribe "cmd"

# 3. Ejecutar el instalador
install.bat
```

**🎯 El instalador hace TODO automáticamente:**
- ✅ Detecta si Python está instalado (o ofrece instalarlo automáticamente con winget)
- ✅ Detecta la versión de Python y advierte si es incompatible (3.13+)
- ✅ Busca versiones compatibles de Python en tu sistema (3.10, 3.11, 3.12)
- ✅ Te permite elegir qué versión de Python usar si tienes varias instaladas
- ✅ Crea un entorno virtual automáticamente para aislar dependencias
- ✅ Instala todas las dependencias necesarias
- ✅ Configura archivos de configuración
- ✅ Opcionalmente ejecuta tests de verificación

**Escenarios comunes:**

| Situación | Qué hace el instalador |
|-----------|----------------------|
| No tienes Python | Te pregunta si quiere instalarlo automáticamente con `winget` |
| Tienes Python 3.14 | Busca Python 3.12/3.11 en tu sistema y te ofrece usarlo |
| Tienes Python 3.12 | ✅ Instala todo sin preguntas |
| Tienes múltiples versiones | Te permite elegir cuál usar |

> ⚠️ **MUY IMPORTANTE para Windows**: 
> - Ejecuta `install.bat` **SOLO desde CMD de Windows nativo**
> - **NO funciona** en Git Bash (MINGW), PowerShell ISE, o WSL
> - Si estás en Git Bash, escribe: `cmd.exe` para abrir CMD, luego ejecuta `install.bat`
> - Si tienes Python instalado, puedes usar `install.py` que funciona en cualquier terminal

---

#### 🐍 Opción B: Multiplataforma con `install.py` (Requiere Python instalado)

Esta opción funciona en **cualquier terminal** (Git Bash, PowerShell, CMD, Linux, macOS):

```bash
# 1. Clonar el repositorio
git clone https://github.com/AlejandroGCN/analizador-bursatil.git
cd analizador-bursatil

# 2. Ejecutar instalador Python (funciona en TODAS las terminales)
python install.py

# En Linux/macOS, dale permisos si es necesario:
chmod +x install.py
python3 install.py
```

> ✅ **Ventajas de install.py**:
> - Funciona en Git Bash, PowerShell, CMD, Terminal Linux/macOS
> - Interfaz con colores y mejor experiencia de usuario
> - Manejo de errores más robusto
> - **Requiere Python 3.9+ ya instalado**

---

#### 📊 Comparación de Instaladores

| Característica | `install.bat` | `install.py` |
|----------------|---------------|--------------|
| **Requiere Python previo** | ❌ NO | ✅ SÍ (Python 3.9+) |
| **Funciona en Git Bash** | ❌ NO | ✅ SÍ |
| **Funciona en CMD Windows** | ✅ SÍ | ✅ SÍ |
| **Funciona en PowerShell** | ⚠️ Limitado | ✅ SÍ |
| **Funciona en Linux/macOS** | ❌ NO | ✅ SÍ |
| **Colores en terminal** | ❌ NO | ✅ SÍ |
| **Mejor experiencia** | Básica | Avanzada |

**¿Cuál usar?**
- **Si NO tienes Python instalado en Windows** → Usa `install.bat` desde CMD
- **Si ya tienes Python** → Usa `install.py` (funciona en cualquier terminal)
- **Si estás en Linux/macOS** → Usa `install.py`
- **Si estás en Git Bash en Windows** → Usa `install.py` o abre CMD para usar `install.bat`

> **💡 Nota**: Ambos instaladores son completamente interactivos y te guían en cada paso.

### 🎯 Inicio Rápido (Post-Instalación)

Una vez instalado, ejecuta la aplicación con:

**Windows:**
```bash
run_app.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
python run_app.py
```

La aplicación se abrirá automáticamente en: **http://localhost:8501**

---

### 🚀 Scripts de Ejecución

#### `run_app.bat` (Windows)

Script automatizado para ejecutar la aplicación en Windows con todas las verificaciones necesarias.

**Qué hace automáticamente:**
- ✅ Verifica que estás en el directorio correcto
- ✅ Activa el entorno virtual si existe (`venv`)
- ✅ Verifica que Python esté instalado
- ✅ Muestra la versión de Python en uso
- ✅ Verifica que las dependencias estén instaladas (comprueba `streamlit`)
- ✅ Ejecuta la aplicación
- ✅ Maneja errores y muestra mensajes claros

**Uso:**
```bash
# Simplemente ejecuta desde CMD
run_app.bat
```

**Ventajas:**
- No necesitas activar manualmente el entorno virtual
- Detecta problemas antes de ejecutar la app
- Si falla, te indica qué hacer

#### `run_app.py` (Multiplataforma)

Script Python para ejecutar la aplicación en cualquier sistema operativo.

**Qué hace:**
- Inicia el servidor Streamlit
- Configura el puerto (8501 por defecto)
- Abre automáticamente el navegador

**Uso:**
```bash
# Asegúrate de activar el entorno virtual primero
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Luego ejecuta:
python run_app.py
```

**Cuándo usar cada uno:**

| Situación | Script Recomendado |
|-----------|-------------------|
| Windows con venv creado | `run_app.bat` (más fácil) |
| Windows sin venv | `python run_app.py` |
| Linux/macOS | `python run_app.py` |
| Desarrollo/debug | `python run_app.py` (más control) |
| Usuario final Windows | `run_app.bat` (más simple) |

### 📋 Requisitos Previos

#### Si usas `install.bat` (Windows):
- ✅ Windows 7 o superior
- ✅ Acceso a Internet
- ✅ CMD de Windows (viene con Windows)
- ❌ **NO requiere Python instalado** (el script te dirá cómo instalarlo)

#### Si usas `install.py` (Cualquier sistema):
- ✅ **Python 3.10, 3.11 o 3.12 YA INSTALADO** (recomendado 3.11 o 3.12)
   ```bash
   python --version  # Debe mostrar 3.10.x, 3.11.x o 3.12.x
   ```
- ✅ Acceso a Internet
- ✅ Permisos de escritura en el directorio

**¿Cómo instalar Python si no lo tienes?**

**Windows (Opción Recomendada - Python 3.12):**
```powershell
# Opción 1: Con winget (recomendado)
winget install Python.Python.3.12

# Opción 2: Descarga manual
# 1. Ve a: https://www.python.org/downloads/
# 2. Descarga Python 3.12.x
# 3. IMPORTANTE: Marca "Add Python to PATH" durante instalación
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-pip python3.12-venv
# o para Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv
```

**macOS:**
```bash
brew install python@3.12
```

> ⚠️ **EVITA Python 3.13 o superior**: Muchas librerías científicas (pyarrow, numpy) aún no tienen versiones precompiladas para Python 3.13+, lo que causará errores de instalación.

> 💡 **Recomendación**: Instala Python 3.11 o 3.12 y usa `install.py` que es más robusto y funciona en cualquier terminal.

### ⚙️ Instalación Manual (Avanzado)

Si prefieres instalar manualmente o necesitas mayor control:

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Actualizar pip
python -m pip install --upgrade pip

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Instalar en modo desarrollo (opcional)
pip install -e .

# 6. Crear directorios necesarios
mkdir -p data var/logs var/config tmp/logs

# 7. Copiar archivo de configuración
cp .env.example .env  # Editar con tus API keys si es necesario

# 8. Ejecutar aplicación
python run_app.py
```

### 🐳 Instalación con Docker

Para un entorno completamente aislado:

```bash
# Construir y ejecutar con Docker Compose
docker-compose up --build

# La aplicación estará en: http://localhost:8501
```

### 🔧 Solución de Problemas Comunes

**Error: "Python no encontrado"**
- Verifica que Python esté instalado: `python --version`
- En Windows, asegúrate de que Python esté en el PATH

**Error: "pip no disponible"**
- Ejecuta: `python -m ensurepip --default-pip`

**Error: "Permisos denegados"**
- Linux/macOS: No uses `sudo` para instalar en el venv
- Windows: Ejecuta la terminal como Administrador

**Error en instalación de dependencias**
- Verifica tu conexión a Internet
- Intenta actualizar pip: `python -m pip install --upgrade pip`
- Instala las dependencias una por una desde `requirements.txt`

**La aplicación no se abre en el navegador**
- Abre manualmente: http://localhost:8501
- Verifica que el puerto 8501 no esté en uso

---

## Configuración

### API Keys (Opcional)

Para utilizar **Tiingo** (datos de calidad institucional), configure su API key:

1. **Obtener API key**: Registrarse en [tiingo.com](https://www.tiingo.com) y obtener token en `/account/api/token`

2. **Configurar localmente**:
```bash
# Copiar plantilla
cp .env.example .env

# Editar .env con su API key
TIINGO_API_KEY=your_api_key_here
```

3. **Verificar**: La aplicación cargará automáticamente la configuración

**Nota:** Yahoo Finance y Binance no requieren API key.

**Documentación completa**: [CONFIGURACION_API_KEYS.md](CONFIGURACION_API_KEYS.md)

---

## Uso

### Ejecución

**Windows:**
```bash
run_app.bat
```

**Linux/macOS:**
```bash
python run_app.py
```

La interfaz se abrirá automáticamente en el navegador en **http://localhost:8501**

### 📊 Visualizaciones Mejoradas

La aplicación incluye visualizaciones profesionales con:

- **Gráficos de línea optimizados** con matplotlib
- **Distribución equilibrada** de datos en toda el área de visualización
- **Líneas de referencia** para retornos (línea en 0)
- **Cuadrícula y etiquetas** para mejor legibilidad
- **Formato responsive** que se ajusta al ancho del contenedor
- **Títulos contextuales** según el tipo de datos mostrados

**Tipos de visualización:**
- 📈 **OHLCV**: Evolución de precios de cierre
- 📊 **Retornos**: Gráfico de retornos diarios con línea de referencia en 0
- 📉 **Volatilidad**: Evolución de la volatilidad en el tiempo
- 📊 **Volumen**: Actividad de trading

### Fuentes de Datos

| Fuente | Tipo | API Key | Intervalos |
|--------|------|---------|-----------|
| **Yahoo Finance** | Acciones, índices | No | 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo |
| **Binance** | Criptomonedas | No | 1m-1M (completo) |
| **Tiingo** | Acciones globales | Sí (gratuita) | 1d (plan gratuito) |

**Limitaciones importantes:**
- Yahoo Finance: Intervalos intraday limitados a ~7 días de historia
- Tiingo plan gratuito: Solo datos EOD (end-of-day)

### Ejemplos de Símbolos

**Yahoo Finance:**
```
AAPL, MSFT, GOOGL, TSLA, AMZN
```

**Binance:**
```
BTCUSDT, ETHUSDT, ADAUSDT, SOLUSDT
```

**Tiingo:**
```
AAPL, MSFT, BP, GOOGL
```

### Formatos de Entrada

Soporta múltiples formatos para importar símbolos:

- **TXT**: Un símbolo por línea
- **CSV**: Columnas con metadata adicional
- **JSON**: Estructura con símbolos y metadatos

Ver ejemplos en: `ejemplos/`

---

## Arquitectura

### Estructura del Proyecto

```
analizador-bursatil/
├── src/
│   ├── data_extractor/       # Motor de extracción
│   │   ├── adapters/          # Yahoo, Binance, Tiingo
│   │   ├── providers/         # Orquestación
│   │   ├── core/              # Base y normalización
│   │   └── series/            # Tipos de series
│   ├── ui/                    # Interfaz Streamlit
│   │   ├── views/             # Vistas por pestaña
│   │   ├── sidebars/          # Controles
│   │   └── services_backend.py # Backend
│   ├── simulation/            # Monte Carlo
│   ├── reporting/             # Generación de reportes
│   └── logs/                  # Configuración de logging
├── var/
│   ├── logs/                  # Logs de aplicación
│   └── config/                # Configuraciones
├── tests/                     # Tests unitarios e integración
├── docs/                      # Diagramas
└── ejemplos/                  # Archivos de ejemplo
```

### Patrones de Diseño

- **Adapter Pattern**: Abstracción de fuentes de datos
- **Provider Pattern**: Lógica común de descarga
- **Facade Pattern**: DataExtractor como punto de entrada único
- **Factory Pattern**: Registro dinámico de adaptadores

### Diagrama de Componentes

```
┌─────────────────┐
│ UI (Streamlit)  │
└────────┬────────┘
         │
┌────────▼────────┐
│ DataExtractor   │ ◄── Facade
└────────┬────────┘
         │
┌────────▼────────┐
│   Provider      │ ◄── Lógica común
└────────┬────────┘
         │
┌────────▼────────┐
│    Adapter      │ ◄── Cliente HTTP
└─────────────────┘
```

**Documentación detallada**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Sistema de Logging

### Archivos de Log

Ubicación: `var/logs/`

| Archivo | Propósito | Nivel |
|---------|-----------|-------|
| `app.log` | Registro general | INFO+ |
| `errors.log` | Errores y excepciones | ERROR |
| `debug.log` | Depuración detallada | DEBUG |
| `performance.log` | Métricas de rendimiento | INFO |

### Configuración

- **Formato**: `Timestamp | Nivel | Módulo | Mensaje`
- **Rotación**: Automática al alcanzar 10MB
- **Historial**: 5 respaldos por archivo
- **Configuración**: `src/logs/logging.yaml`

### Comandos Útiles

```bash
# Ver logs en tiempo real
tail -f var/logs/app.log

# Filtrar errores
grep "ERROR" var/logs/app.log

# Ver solo módulo específico
grep "tiingo" var/logs/app.log
```

### Activar Debug Mode

Editar `src/ui/app_config.py`:
```python
DEBUG_LOGGING_ENABLED = True
```

---

## Características Técnicas

### Métricas Financieras

- **Retorno esperado**: Media anualizada
- **Volatilidad**: Desviación estándar anualizada
- **Ratio de Sharpe**: Retorno ajustado por riesgo
- **Estadísticas descriptivas**: Automáticas

### Simulación Monte Carlo

- Trayectorias múltiples con movimiento browniano geométrico
- Intervalos de confianza (5%, 25%, 50%, 75%, 95%)
- Volatilidad dinámica configurable
- Validación matemática de coherencia

### Validación de Datos

- Intervalos validados dinámicamente por fuente
- Normalización automática de series
- Detección de datos faltantes
- Alineación temporal configurable

---

## Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=src

# Solo tests unitarios
pytest tests/units/

# Solo tests de integración
pytest tests/integration/
```

---

## Documentación

### Archivos Principales

| Documento | Descripción |
|-----------|-------------|
| [README.md](README.md) | Esta documentación |
| [QUICKSTART.md](QUICKSTART.md) | Guía de inicio rápido |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detalles técnicos y diagramas |
| [CONFIGURACION_API_KEYS.md](CONFIGURACION_API_KEYS.md) | Setup de API keys |

### Diagramas

Los diagramas Mermaid están disponibles en: `docs/diagrams/`

- Arquitectura completa
- Patrones de diseño
- Flujo de secuencia
- Jerarquía de clases
- Stack tecnológico

---

## Licencia

MIT License - Ver archivo `LICENSE` para detalles.

---

## Contacto

Para consultas técnicas o colaboraciones, ver información en el perfil de GitHub.
