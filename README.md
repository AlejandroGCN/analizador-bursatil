# 📈 Analizador Bursátil

Aplicación **Streamlit** que descarga, normaliza y visualiza datos bursátiles históricos desde **Yahoo Finance**, **Binance** y **Stooq**, utilizando el motor modular del paquete `data_extractor`.

Permite seleccionar fuente, símbolos, rango temporal, tipo de dato (OHLCV, retornos o volatilidad), y visualizar los resultados en tablas y gráficos interactivos.

## 📋 Requisitos del Sistema

### Para Usuarios Sin Conocimientos Técnicos
**Lo que necesitas:**
- ✅ **Computadora con Windows, Mac o Linux**
- ✅ **Conexión a Internet**
- ✅ **Navegador web** (Chrome, Firefox, Safari, Edge)

**¿No tienes Python instalado?** No te preocupes, te guiamos paso a paso:

### Instalación de Python (Si no lo tienes)

#### Windows
1. Ve a [python.org/downloads](https://www.python.org/downloads/)
2. Descarga "Python 3.12" (botón amarillo grande)
3. **IMPORTANTE**: Al instalar, marca ✅ "Add Python to PATH"
4. Sigue las instrucciones de instalación
5. Reinicia tu computadora

#### Mac
1. Ve a [python.org/downloads](https://www.python.org/downloads/)
2. Descarga "Python 3.12" para Mac
3. Abre el archivo descargado y sigue las instrucciones
4. Abre "Terminal" (búsquelo en Spotlight)

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

### Verificar que Python está instalado
Abre una ventana de comandos y escribe:
```bash
python --version
```
Deberías ver algo como: `Python 3.12.x`

## 🚀 Instalación Paso a Paso

### Opción 1: Instalación Simple (Recomendado) ✅

**Solo necesitas hacer doble clic en un archivo**

#### Paso 1: Descargar el Proyecto

##### Opción A: Descarga Directa (Más Fácil) 📥
1. Ve a [GitHub del proyecto](https://github.com/AlejandroGCN/analizador-bursatil)
2. Haz clic en el botón verde **"Code"**
3. Selecciona **"Download ZIP"**
4. Extrae el archivo ZIP en tu escritorio
5. Navega a la carpeta extraída

##### Opción B: Con Git (Recomendado para actualizaciones) 🔧
**Primero instala Git si no lo tienes:**

**Windows:**
1. Ve a [git-scm.com/downloads](https://git-scm.com/downloads)
2. Descarga Git para Windows
3. Instala con la configuración predeterminada
4. Reabre tu terminal/PowerShell

**Mac:**
```bash
# Git viene preinstalado. Si no lo tienes:
brew install git
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install git

# CentOS/RHEL
sudo yum install git
```

**Clonar el proyecto:**
```bash
git clone https://github.com/AlejandroGCN/analizador-bursatil.git
cd analizador-bursatil
```

#### Paso 2: Instalar y Ejecutar

#### Para Windows:
1. Haz **doble clic** en `install.bat`
2. Espera a que termine (puede tardar unos minutos)
3. Haz **doble clic** en `run_app.bat` (o `run_app.py`)
4. ¡Listo! Se abrirá tu navegador automáticamente

#### Para Mac/Linux:
1. Abre "Terminal" en la carpeta del proyecto
2. Escribe: `python install.py` y presiona Enter
3. Espera a que termine
4. Escribe: `python run_app.py` y presiona Enter
5. ¡Listo! Se abrirá tu navegador automáticamente



## 🐳 Instalación con Docker (Para usuarios avanzados)

Si prefieres usar Docker para tener todo aislado en un contenedor, sigue estas instrucciones:

### Requisitos previos
- Tener Docker Desktop instalado: https://www.docker.com/products/docker-desktop/
- Tener el proyecto descargado localmente

### Pasos para ejecutar

1. **Inicia Docker Desktop** (debe estar corriendo)

2. **Abre una terminal en la carpeta del proyecto**

3. **Construye e inicia el contenedor:**
   ```bash
   docker-compose up --build
   ```
   
   ⏱️ **Nota:** La primera vez puede tardar 5-10 minutos (descarga dependencias)

4. **Espera** hasta ver el mensaje:
   ```
   You can now view your Streamlit app in your browser.
   URL: http://0.0.0.0:8501
   ```

5. **Abre tu navegador** en: http://localhost:8501

### Comandos útiles

```bash
# Iniciar la aplicación
docker-compose up

# Iniciar en segundo plano (detached)
docker-compose up -d

# Detener la aplicación
docker-compose down

# Ver logs
docker-compose logs -f

# Reconstruir desde cero
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Solución de problemas

- **Error "Docker no está corriendo"**: Inicia Docker Desktop
- **Puerto 8501 ocupado**: Cambia el puerto en `docker-compose.yml` (ej: `8502:8501`)
- **Error al construir**: Asegúrate de estar en la carpeta del proyecto

---

## 🎯 Instalación Avanzada (Para Desarrolladores)

### Instalación Manual Completa
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -e .[dev]

# Ejecutar
python run_app.py
```

### Instalación Global
```bash
pip install -e .[dev]
analizador-bursatil  # Comando global
```

## 🎯 Uso Rápido

1. **Ejecutar la app**: `python run_app.py`
2. **Abrir navegador**: Se abrirá automáticamente en `http://localhost:8501`
3. **Seleccionar fuente**: Yahoo Finance, Binance o Stooq
4. **Elegir símbolos**: Ej: `AAPL`, `MSFT`, `BTCUSDT`
5. **Configurar fechas**: Rango temporal deseado
6. **¡Analizar!**: Ver gráficos y métricas automáticamente

## ✨ Características Principales

- 🔄 **Múltiples fuentes de datos**: Yahoo Finance, Binance, Stooq
- 🎲 **Simulación Monte Carlo**: Análisis de riesgo con parámetros configurables
- 📈 **Visualizaciones interactivas**: Gráficos profesionales con Streamlit
- 🧹 **Limpieza automática de datos**: Preprocesado y validación
- 📋 **Reportes en Markdown**: Análisis completo con advertencias
- 🏗️ **Arquitectura modular**: Fácil extensión y mantenimiento

## 📊 Métricas Financieras Disponibles

### Métricas Básicas
- **Retorno esperado**: Media de retornos anualizada
- **Volatilidad**: Desviación estándar de retornos anualizada  
- **Ratio de Sharpe**: Retorno ajustado por riesgo
- **Estadísticas descriptivas**: Media, desviación estándar automáticas

### Simulación Monte Carlo
- **Trayectorias simuladas**: Múltiples escenarios de evolución
- **Intervalos de confianza**: Percentiles 5%, 25%, 50%, 75%, 95%
- **Parámetros configurables**: Número de simulaciones, horizonte temporal
- **Volatilidad dinámica**: Opción de volatilidad variable en el tiempo
- **Validación matemática**: Cálculos verificados usando movimiento browniano geométrico correcto
- **Precisión en retornos**: Fórmula validada que garantiza coherencia entre retorno esperado y simulado

### Validación Dinámica de Intervalos

La interfaz valida automáticamente los intervalos disponibles según la fuente seleccionada:

- **Yahoo Finance**: Soporta intervalos diarios (1d, 1wk, 1mo), horarios (1h) e intradía (1m, 5m, 15m, 30m, 60m, 90m)
- **Binance**: Soporta intervalos desde 1 minuto hasta mensuales (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
- **Stooq**: Soporta solo datos diarios (1d, 1wk, 1mo)
- **Validación automática**: Si cambias de fuente, el intervalo se ajusta automáticamente si no está disponible
- **Consulta dinámica**: Los intervalos se obtienen directamente de los adaptadores para garantizar exactitud

---

## 🧠 Arquitectura General

               ┌─────────────────────┐
               │   UI (Streamlit)    │
               │  dashboard / views  │
               └────────┬────────────┘
                        │
               ┌────────▼────────────┐
               │  services_backend   │  ◄── Orquesta UI → extractor
               └────────┬────────────┘
                        │
               ┌────────▼────────────┐
               │   DataExtractor     │  ◄── Fachada unificada
               └────────┬────────────┘
                        │
               ┌────────▼────────────┐
               │      Provider       │  ◄── Lógica común (adapter + normalizer)
               └────────┬────────────┘
                        │
               ┌────────▼────────────┐
               │      Adapter        │  ◄── Cliente HTTP (Yahoo, Binance, Stooq)
               └─────────────────────┘

## 🌟 Características Principales

### ✨ Funcionalidades Implementadas
- 🎨 **Interfaz Streamlit**: Panel central para inputs de símbolos con mejor visibilidad
- 💼 **Análisis de cartera**: Sistema de pesos con validación inteligente, normalización automática y sincronización
- 🔄 **Persistencia de datos**: Los símbolos se mantienen al cambiar de pestaña
- 📦 **Importación flexible**: Importar símbolos entre pestañas (Datos ↔ Cartera)
- 🎯 **Validación robusta**: Mensajes de error claros cuando faltan símbolos
- 📊 **Visualización enriquecida**: Distribución de cartera con valores monetarios
- 🎲 **Simulación Monte Carlo**: Integrada con parámetros configurables
- 📈 **Múltiples fuentes**: Yahoo Finance, Binance y Stooq

### 🏗️ Arquitectura Técnica
- 🏗️ **Estructura modular**: Separación clara entre views, sidebars y utilities
- 🔧 **Código limpio**: Funciones pequeñas con responsabilidades únicas (principio SRP)
- 📝 **Sin duplicación**: Funciones reutilizables centralizadas en utils.py
- ⚡ **Baja complejidad**: Funciones principales < 80 líneas, auxiliares < 50 líneas
- 🎯 **Nomenclatura clara**: Archivos con sufijos `_view.py` y `_sidebar.py`
- ✨ **Optimizado**: CSS unificado, validaciones simplificadas, normalización eficiente
- 🎨 **Tema personalizado**: Sidebar con fondo azul para mejor contraste
- 🔍 **Sistema de logging**: Debug logging integrado para validación de cálculos y depuración
- ✅ **Validación de datos**: Verificación automática de normalización, coherencia y calidad de datos

### 📊 Documentación Completa
- 📊 **Diagramas Mermaid**: Visualización completa de la arquitectura
- 🔄 **Diagramas de secuencia**: Flujo de datos paso a paso
- 🏗️ **Patrones de diseño**: Documentación de patrones utilizados
- 📝 **API documentada**: Docstrings completos con ejemplos

---

## 📋 Ejemplos de Uso

### Símbolos Recomendados por Fuente

**Yahoo Finance (Acciones):**
- `AAPL` - Apple Inc.
- `MSFT` - Microsoft Corporation
- `GOOGL` - Alphabet Inc.
- `TSLA` - Tesla Inc.
- `AMZN` - Amazon.com Inc.

**Binance (Criptomonedas):**
- `BTCUSDT` - Bitcoin/USDT
- `ETHUSDT` - Ethereum/USDT
- `ADAUSDT` - Cardano/USDT
- `SOLUSDT` - Solana/USDT
- `DOTUSDT` - Polkadot/USDT

**Stooq (Acciones Europeas):**
- `AAPL.US` - Apple (US)
- `MSFT.US` - Microsoft (US)
- `GOOGL.US` - Google (US)

### Configuraciones Recomendadas

**Para Análisis Diario:**
- Intervalo: `1d`
- Rango: Últimos 2 años
- Fuente: Yahoo Finance

**Para Análisis Intradía:**
- Intervalo: `1h`
- Rango: Últimos 30 días
- Fuente: Binance (criptomonedas)

### Formatos de Archivos de Símbolos

El proyecto incluye diferentes formatos de ejemplo para que puedas elegir el que más te convenga:

**📄 symbols.txt** - Formato más simple
```
AAPL
MSFT
GOOGL
```
*Usa este formato si solo necesitas una lista simple de símbolos*

**📊 symbols.csv** - Formato con información adicional
```csv
symbol,company,price
AAPL,Apple Inc.,150.00
MSFT,Microsoft Corporation,300.00
```
*Usa este formato si quieres incluir información adicional como empresa y precio*

**📋 symbols.json** - Formato estructurado
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "description": "Lista de símbolos tecnológicos",
  "last_updated": "2025-10-24"
}
```
*Usa este formato si necesitas metadatos y estructura compleja*

**📝 symbols_example.txt** - Formato detallado con fuentes
```
AAPL,Apple Inc.,yahoo
BTCUSDT,Bitcoin/USDT,binance
```
*Usa este formato si necesitas especificar la fuente de datos para cada símbolo*

## 📁 Archivos de Ayuda

### Documentación
- **[README.md](README.md)**: Esta guía completa
- **[QUICKSTART.md](QUICKSTART.md)**: Guía de inicio rápido (5 minutos)
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Documentación técnica detallada

### Instalación
- **[install.py](install.py)**: Script de instalación automática (Linux/Mac)
- **[install.bat](install.bat)**: Script de instalación automática (Windows)

### Ejemplos y Configuración
- **[ejemplos/symbols.csv](ejemplos/symbols.csv)**: Formato CSV con símbolos, empresas y precios
- **[ejemplos/symbols.json](ejemplos/symbols.json)**: Formato JSON estructurado con metadatos
- **[ejemplos/symbols.txt](ejemplos/symbols.txt)**: Formato simple, solo símbolos uno por línea
- **[config_example.yaml](config_example.yaml)**: Configuración de ejemplo (se crea automáticamente)

### Ejecución
- **[run_app.py](run_app.py)**: Punto de entrada principal
- **Comandos globales**: `analizador-bursatil` o `bursatil` (después de instalar)

## 📁 Estructura del Proyecto

Para una documentación detallada de la arquitectura, consulta [ARCHITECTURE.md](ARCHITECTURE.md) que incluye:
- Diagramas Mermaid interactivos
- Flujo de datos detallado
- Patrones de diseño utilizados
- Tecnologías y dependencias

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
