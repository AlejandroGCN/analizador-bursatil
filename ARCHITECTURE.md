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
