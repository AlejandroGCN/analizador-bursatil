# Analizador Bursátil

Aplicación **Streamlit** para análisis financiero cuantitativo con descarga, normalización y visualización de datos bursátiles desde múltiples fuentes (Yahoo Finance, Binance, Tiingo).

**Características principales:**
- Extracción multi-fuente con arquitectura modular
- Simulación Monte Carlo para análisis de riesgo
- Sistema de logging profesional
- Gestión segura de API keys
- Visualizaciones interactivas

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

- **Python**: 3.10 o superior
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

### Instalación Rápida

**Windows:**
```bash
git clone https://github.com/AlejandroGCN/analizador-bursatil.git
cd analizador-bursatil
install.bat
```

**Linux/macOS:**
```bash
git clone https://github.com/AlejandroGCN/analizador-bursatil.git
cd analizador-bursatil
python install.py
```

### Instalación Manual

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python run_app.py
```

### Instalación con Docker

```bash
docker-compose up --build
```

La aplicación estará disponible en: `http://localhost:8501`

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

```bash
python run_app.py
```

La interfaz se abrirá automáticamente en el navegador.

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
