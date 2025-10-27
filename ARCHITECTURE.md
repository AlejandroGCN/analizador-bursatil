# 🏗️ Arquitectura del Analizador Bursátil

## Diagrama de Arquitectura General

```mermaid
graph TB
    subgraph "🎨 Capa de Presentación"
        UI[📱 Streamlit Dashboard]
        Views[📊 Views & Components]
        Sidebars[⚙️ Sidebars & Controls]
    end
    
    subgraph "🔧 Capa de Servicios"
        Backend[🔄 Services Backend]
        Config[⚙️ App Configuration]
    end
    
    subgraph "📦 Capa de Extracción"
        Extractor[📈 DataExtractor<br/>Fachada Principal]
        ConfigExt[⚙️ ExtractorConfig]
    end
    
    subgraph "🏭 Capa de Providers"
        Registry[📋 Provider Registry]
        YahooP[🌐 Yahoo Provider]
        BinanceP[💰 Binance Provider]
        StooqP[📊 Stooq Provider]
    end
    
    subgraph "🔌 Capa de Adaptadores"
        BaseAdapter[🔧 Base Adapter]
        YahooA[🌐 Yahoo Adapter]
        BinanceA[💰 Binance Adapter]
        StooqA[📊 Stooq Adapter]
    end
    
    subgraph "📊 Capa de Series de Datos"
        PriceSeries[💰 PriceSeries<br/>OHLCV Data]
        PerfSeries[📈 PerformanceSeries<br/>Returns Data]
        VolSeries[📊 VolatilitySeries<br/>Volatility Data]
        VolActSeries[📈 VolumeActivitySeries<br/>Volume Data]
    end
    
    subgraph "🎯 Capa de Simulación"
        Portfolio[💼 Portfolio<br/>Asset Management]
        MonteCarlo[🎲 MonteCarloSimulation<br/>Risk Analysis]
    end
    
    subgraph "🧹 Capa de Limpieza"
        Cleaner[🧽 DataCleaner<br/>Data Processing]
    end
    
    subgraph "📈 Fuentes Externas"
        YahooAPI[🌐 Yahoo Finance API]
        BinanceAPI[💰 Binance API]
        StooqAPI[📊 Stooq API]
    end
    
    %% Conexiones principales
    UI --> Views
    UI --> Sidebars
    Views --> Backend
    Sidebars --> Backend
    Backend --> Extractor
    Extractor --> ConfigExt
    Extractor --> Registry
    
    Registry --> YahooP
    Registry --> BinanceP
    Registry --> StooqP
    
    YahooP --> YahooA
    BinanceP --> BinanceA
    StooqP --> StooqA
    
    YahooA --> BaseAdapter
    BinanceA --> BaseAdapter
    StooqA --> BaseAdapter
    
    BaseAdapter --> YahooAPI
    BaseAdapter --> BinanceAPI
    BaseAdapter --> StooqAPI
    
    %% Flujo de datos
    Extractor --> PriceSeries
    Extractor --> PerfSeries
    Extractor --> VolSeries
    Extractor --> VolActSeries
    
    PriceSeries --> Portfolio
    PerfSeries --> Portfolio
    Portfolio --> MonteCarlo
    
    PriceSeries --> Cleaner
    PerfSeries --> Cleaner
    VolSeries --> Cleaner
    VolActSeries --> Cleaner
    
    %% Estilos
    classDef uiLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef serviceLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dataLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef providerLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef adapterLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef seriesLayer fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    classDef simulationLayer fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef cleaningLayer fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef externalLayer fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class UI,Views,Sidebars uiLayer
    class Backend,Config serviceLayer
    class Extractor,ConfigExt dataLayer
    class Registry,YahooP,BinanceP,StooqP providerLayer
    class BaseAdapter,YahooA,BinanceA,StooqA adapterLayer
    class PriceSeries,PerfSeries,VolSeries,VolActSeries seriesLayer
    class Portfolio,MonteCarlo simulationLayer
    class Cleaner cleaningLayer
    class YahooAPI,BinanceAPI,StooqAPI externalLayer
```

## Flujo de Datos Detallado

```mermaid
sequenceDiagram
    participant U as 👤 Usuario
    participant UI as 📱 Streamlit UI
    participant BE as 🔄 Backend Service
    participant EX as 📈 DataExtractor
    participant REG as 📋 Registry
    participant PR as 🏭 Provider
    participant AD as 🔌 Adapter
    participant API as 🌐 External API
    participant PS as 📊 PriceSeries
    participant PO as 💼 Portfolio
    participant MC as 🎲 MonteCarlo
    
    U->>UI: Selecciona símbolos y parámetros
    UI->>BE: Envía configuración
    BE->>EX: get_market_data(symbols, params)
    EX->>REG: Resuelve provider por fuente
    REG->>PR: Retorna provider específico
    EX->>PR: get_symbols(symbols, params)
    PR->>AD: fetch_data(symbols, params)
    AD->>API: HTTP Request
    API-->>AD: Raw Data Response
    AD-->>PR: Normalized Data
    PR-->>EX: Series Objects
    EX-->>BE: Dict[symbol -> Series]
    BE-->>UI: Datos para visualización
    
    Note over U,MC: Análisis de Cartera
    U->>UI: Crea cartera con pesos
    UI->>BE: Portfolio creation
    BE->>PO: new Portfolio(symbols, weights)
    PO->>PS: set_prices(price_data)
    PS-->>PO: Calcula retornos automáticamente
    
    Note over U,MC: Simulación Monte Carlo
    U->>UI: Ejecuta simulación
    UI->>BE: Monte Carlo request
    BE->>PO: monte_carlo_simulation(params)
    PO->>MC: simulate_portfolio(returns, volatility)
    MC-->>PO: Simulation results
    PO-->>BE: DataFrame con simulaciones
    BE-->>UI: Resultados para visualización
    UI-->>U: Gráficos y estadísticas
```

## Patrones de Diseño Utilizados

### 1. **Patrón Facade** 
- `DataExtractor` actúa como fachada unificada para todos los providers
- Simplifica la interfaz compleja del sistema de extracción

### 2. **Patrón Registry**
- `REGISTRY` mantiene un mapa de fuentes → providers
- Permite añadir nuevas fuentes dinámicamente

### 3. **Patrón Strategy**
- Cada `Provider` implementa una estrategia diferente de extracción
- `BaseProvider` define la interfaz común

### 4. **Patrón Adapter**
- `BaseAdapter` adapta diferentes APIs externas a una interfaz común
- Cada adapter maneja las peculiaridades de su API específica

### 5. **Patrón Template Method**
- `BaseSeries` define el template para todas las series de datos
- Cada serie implementa sus métodos específicos

## 🎨 Arquitectura de UI (Streamlit)

### Estructura de Archivos

```
src/ui/
├── dashboard.py                 # Punto de entrada principal
├── app_config.py               # Configuración de la app
├── services_backend.py         # Servicios backend
├── error_handler.py            # Manejo de errores
├── file_loader.py              # Carga de archivos
├── utils.py                    # Utilidades compartidas
│
├── views/                      # Vistas principales
│   ├── __init__.py
│   ├── datos_view.py           # Pestaña Datos
│   ├── cartera_view.py         # Pestaña Cartera
│   ├── montecarlo_view.py      # Pestaña Monte Carlo
│   └── reporte_view.py         # Pestaña Reporte
│
└── sidebars/                   # Controles laterales
    ├── __init__.py
    ├── types.py                # Dataclasses para parámetros
    ├── datos_sidebar.py        # Sidebar Datos
    ├── cartera_sidebar.py     # Sidebar Cartera
    ├── montecarlo_sidebar.py  # Sidebar Monte Carlo
    └── reporte_sidebar.py      # Sidebar Reporte
```

### Flujo de Session State

```mermaid
graph LR
    A[Usuario interactúa] --> B[Widget actualiza session_state]
    B --> C{Es un form?}
    C -->|Sí| D[Espera submit]
    C -->|No| E[Rerun inmediato]
    D --> F[Submit actualiza todos los valores]
    F --> G[Rerun]
    E --> G
    G --> H[Render nuevo con valores actualizados]
```

### Componentes Principales

1. **Sidebars** (`sidebars/`)
   - Cada pestaña tiene su propio sidebar
   - Contiene formularios y controles
   - Retorna parámetros validados

2. **Views** (`views/`)
   - Contenido principal de cada pestaña
   - Recibe parámetros del sidebar
   - Muestra visualizaciones y resultados

3. **Utils** (`utils.py`)
   - Funciones compartidas entre views/sidebars
   - Manejo de símbolos
   - Validaciones comunes

### 🔧 Características Actuales

#### Inputs de Símbolos
- ✅ **Panel central**: Inputs en el panel principal para mejor visibilidad
- ✅ **Persistencia**: Los símbolos se mantienen al cambiar de pestaña
- ✅ **Importación entre pestañas**: Fácil copiar símbolos entre Datos y Cartera
- ✅ **Carga de archivos**: Soporte para CSV, Excel, JSON, TXT

#### Sistema de Pesos de Cartera
- ✅ **Validación inteligente**: Tolerancia a redondeos (33%+33%+33%=99%)
- ✅ **Visualización monetaria**: Muestra valores absolutos en dólares
- ✅ **Error cuando excede 100%**: Prevención de pesos inválidos
- ✅ **Normalización automática**: Ajuste proporcional cuando suma < 100%

#### Validación de Datos
- ✅ **Error cuando faltan símbolos**: Prevención de ejecución vacía
- ✅ **Mensajes informativos**: Guía clara para el usuario
- ✅ **Validación de formato**: Verificación de símbolos parseados

#### UI/UX
- ✅ **CSS personalizado**: Sidebar con fondo azul para contraste
- ✅ **Botones mejorados**: Iconos y ancho completo
- ✅ **Monte Carlo integrado**: Valor inicial automático desde cartera

## Métricas y Análisis Disponibles

### 📊 **Métricas Básicas**
- Media y desviación estándar (automáticas)
- Retorno esperado y volatilidad
- Ratio de Sharpe

### 🎲 **Simulación Monte Carlo**
- Trayectorias de precios simuladas
- Intervalos de confianza
- Análisis de percentiles
- Visualización interactiva

## Tecnologías y Dependencias

### **Core**
- Python 3.10+
- Pandas 2.0+ (manipulación de datos)
- NumPy 1.24+ (cálculos numéricos)

### **APIs Externas**
- yfinance (Yahoo Finance)
- requests (Binance API)
- pandas_datareader (Stooq)

### **UI y Visualización**
- Streamlit (interfaz web)
- Matplotlib (gráficos)
- Seaborn (visualizaciones avanzadas)

### **Testing y Calidad**
- pytest (testing framework)
- pytest-cov (cobertura de código)
- black, flake8, mypy (calidad de código)
