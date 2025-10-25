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

### Paso 1: Descargar el Proyecto

#### Opción A: Descarga Directa (Más Fácil)
1. Ve a [GitHub del proyecto](https://github.com/AlejandroGCN/analizador-bursatil)
2. Haz clic en el botón verde **"Code"**
3. Selecciona **"Download ZIP"**
4. Extrae el archivo ZIP en tu escritorio

#### Opción B: Con Git (Si sabes usarlo)
```bash
git clone https://github.com/AlejandroGCN/analizador-bursatil.git
cd analizador-bursatil
```

### Paso 2: Instalación Automática

#### Windows
1. Abre la carpeta del proyecto
2. Haz **doble clic** en `install.bat`
3. Espera a que termine la instalación
4. Haz **doble clic** en `run_app.py`

#### Mac/Linux
1. Abre "Terminal" en la carpeta del proyecto
2. Escribe: `python install.py`
3. Espera a que termine la instalación
4. Escribe: `python run_app.py`

### Paso 3: ¡Usar la Aplicación!
1. Se abrirá automáticamente tu navegador
2. La aplicación estará en `http://localhost:8501`
3. ¡Empieza a analizar datos financieros!

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

## 🚀 Mejoras Recientes

### Diagramas de Arquitectura
- 📊 **Diagrama Mermaid detallado**: Visualización completa de la arquitectura del sistema
- 🔄 **Diagrama de secuencia**: Flujo de datos paso a paso
- 🏗️ **Patrones de diseño**: Documentación de los patrones utilizados

### Documentación API Mejorada
- 📝 **Docstrings detalladas**: Documentación completa con ejemplos
- 🔍 **Parámetros documentados**: Descripción detallada de todos los argumentos
- 💡 **Ejemplos de uso**: Casos de uso prácticos en la documentación
- ⚠️ **Manejo de errores**: Documentación de excepciones y casos límite

### Reportes y Visualizaciones
- 📋 **Reportes enriquecidos**: Análisis completo con métricas básicas
- 📊 **Gráficos mejorados**: Visualizaciones profesionales de carteras
- ⚠️ **Análisis de advertencias**: Detección automática de riesgos y problemas
- 🎨 **Interfaz mejorada**: Mejor organización visual de la información

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

## 🔧 Solución de Problemas

### ❌ "No se puede encontrar Python"
**Problema**: El sistema no encuentra Python
**Solución**: 
1. Ve a [python.org/downloads](https://www.python.org/downloads/)
2. Instala Python 3.12
3. **IMPORTANTE**: Marca "Add Python to PATH" durante la instalación
4. Reinicia tu computadora

### ❌ "No module named 'streamlit'"
**Problema**: Faltan componentes de la aplicación
**Solución**: 
1. Abre Terminal/CMD en la carpeta del proyecto
2. Escribe: `pip install -e .[dev]`
3. Espera a que termine

### ❌ "Symbol not found" (Símbolo no encontrado)
**Problema**: El símbolo que escribiste no existe
**Solución**: 
- **Yahoo Finance**: Usa `AAPL`, `MSFT`, `GOOGL`
- **Binance**: Usa `BTCUSDT`, `ETHUSDT`, `ADAUSDT`
- **Stooq**: Usa `AAPL.US`, `MSFT.US`

### ❌ La aplicación no se abre en el navegador
**Problema**: Puerto ocupado o problema de conexión
**Solución**: 
1. Cierra todas las ventanas del navegador
2. Abre Terminal/CMD en la carpeta del proyecto
3. Escribe: `python run_app.py`
4. Si no funciona, escribe: `streamlit run src/ui/dashboard.py --server.port 8502`

### ❌ "pandas_datareader no está disponible"
**Problema**: Incompatibilidad con Python 3.12+
**Solución**: 
- **No uses Stooq** si tienes Python 3.12+
- **Usa Yahoo Finance** para acciones
- **Usa Binance** para criptomonedas

### ❌ La aplicación va muy lenta
**Problema**: Demasiados datos o símbolos
**Solución**: 
- Reduce el rango de fechas (ej: últimos 6 meses)
- Usa menos símbolos (máximo 5)
- Cambia a intervalo diario (`1d`) en lugar de horario (`1h`)

## 📁 Archivos de Ayuda

### Documentación
- **[README.md](README.md)**: Esta guía completa
- **[QUICKSTART.md](QUICKSTART.md)**: Guía de inicio rápido (5 minutos)
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Documentación técnica detallada

### Instalación
- **[install.py](install.py)**: Script de instalación automática (Linux/Mac)
- **[install.bat](install.bat)**: Script de instalación automática (Windows)

### Ejemplos y Configuración
- **[ejemplos/symbols_example.txt](ejemplos/symbols_example.txt)**: Lista detallada de símbolos recomendados
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

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
