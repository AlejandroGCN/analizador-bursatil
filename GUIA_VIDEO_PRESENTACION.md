# 🎥 Guía para Vídeo de Presentación (5 minutos)

Esta guía te ayudará a responder **LAS 6 PREGUNTAS OBLIGATORIAS** del proyecto de forma clara y estructurada.

---

## 🎯 LAS 6 PREGUNTAS QUE DEBES RESPONDER

El vídeo debe explicar **QUÉ has hecho, CÓMO lo has hecho, y POR QUÉ**, centrándote en:

| # | Pregunta | Tiempo | Importancia | Qué Mostrar |
|---|----------|--------|-------------|-------------|
| **1** | **Estructura del proyecto** - Herencias y dependencias | 40s | ⭐⭐⭐⭐⭐ | **2 diagramas Mermaid** |
| **2** | **Uso de GitHub** - Cómo lo has usado | 30s | ⭐⭐⭐ | Repo + commits |
| **3** | **Unificación de formatos** - APIs → mismo formato | 30s | ⭐⭐⭐⭐ | Código normalizer |
| **4** | **Creación de cartera** - Desde series de precios | 30s | ⭐⭐⭐⭐ | Código Portfolio |
| **5** | **Implementación Monte Carlo** - Cómo funciona | 60s | ⭐⭐⭐⭐⭐ | Fórmula + simulación |
| **6** | **Contenido del reporte** - Qué incluye y por qué | 60s | ⭐⭐⭐⭐⭐ | Reporte generado |

**ENFÓCATE EN ESTAS 6 - NO te distraigas con otros detalles**

---

## 📋 Estructura del Vídeo (Minutaje Optimizado)

```
00:00 - 00:20  Introducción rápida
00:20 - 01:00  ❶ Estructura: Herencias y dependencias (40s)
01:00 - 01:30  ❷ Uso de GitHub (30s)
01:30 - 02:00  ❸ Unificación de formatos de APIs (30s)
02:00 - 02:30  ❹ Construcción de cartera (30s)
02:30 - 03:30  ❺ Implementación Monte Carlo (60s)
03:30 - 04:30  ❻ Contenido del reporte y criterios (60s)
04:30 - 05:00  Conclusión y tecnologías (30s)
```

**TOTAL: 5 minutos exactos**

---

## 1️⃣ INTRODUCCIÓN (30 segundos)

### Qué Decir:

> "He desarrollado un **Analizador Bursátil** completamente en **Python 3.12**, utilizando programación orientada a objetos con herencia, abstracción y patrones de diseño profesionales. La interfaz de usuario está construida con **Streamlit** para hacerla accesible y visual, pero el núcleo del proyecto es Python puro: descarga concurrente de datos desde múltiples APIs (Yahoo Finance, Binance y Tiingo), procesamiento con Pandas y NumPy, simulaciones Monte Carlo con movimiento browniano geométrico, y generación de reportes automatizados."

### Qué Mostrar:
- Pantalla principal de la aplicación funcionando
- Cambio rápido entre las 4 pestañas: Datos, Cartera, Monte Carlo, Reporte
- **Importante**: Mencionar que Streamlit es solo la capa visual, el núcleo es Python

### Puntos Clave:
- ✅ **Python 3.12** como lenguaje principal (POO, herencia, abstracciones)
- ✅ Multi-fuente (3 APIs) con descarga paralela
- ✅ Simulación Monte Carlo (matemáticas financieras)
- ✅ Reportes automáticos (Markdown + PDF)
- ✅ Streamlit como framework de UI

---

## 2️⃣ ESTRUCTURA: HERENCIAS Y DEPENDENCIAS (40 segundos)

### Qué Explicar:

> "El proyecto sigue una **arquitectura modular** basada en **tres jerarquías de herencia principales**, donde las clases base definen la estructura y comportamiento común que heredan y especializan las clases hijas."

### A. PRIMERO: Mostrar Diagrama de Jerarquías (20s)

**Mostrar:** `docs/diagrams/1_jerarquias_herencia.mmd` (o PNG exportado)

**Decir mientras lo muestras (PROFUNDIZAR EN FUNCIONES DE CLASES BASE):**

> "Como ven en este diagrama, tengo **tres jerarquías de herencia**:
> 
> 1. **BaseAdapter** - Es la clase base que define el contrato para todas las fuentes de datos. Tiene métodos abstractos como `fetch_ohlcv()`, `fetch_symbols()` y `validate_params()` que TODAS las clases hijas (YahooAdapter, BinanceAdapter, TiingoAdapter) deben implementar. También define métodos comunes como `_build_request_url()` y `_handle_api_errors()` que las hijas heredan y reutilizan. Esto asegura que cualquier fuente nueva que agregue seguirá el mismo patrón.
> 
> 2. **BaseProvider** - Orquesta la lógica de negocio. Proporciona métodos como `extract_data()` y `_normalize_response()` que las clases hijas (YahooProvider, BinanceProvider, TiingoProvider) heredan. La clave aquí es que el Provider usa su Adapter específico pero todos siguen el mismo flujo: validar → descargar → normalizar → devolver Series.
> 
> 3. **BaseSeries** - Es una dataclass que define la estructura de cualquier serie temporal. Tiene métodos estadísticos base como `mean()`, `std()`, `rolling_window()` que se calculan automáticamente al crear la serie. Las clases hijas (PriceSeries, PerformanceSeries, VolatilitySeries) heredan estos métodos y añaden otros específicos, como `calculate_returns()` en PriceSeries o `sharpe_ratio()` en PerformanceSeries."

### B. SEGUNDO: Mostrar Flujo de Arquitectura (20s)

**Mostrar:** `docs/diagrams/2_flujo_arquitectura.mmd` (o PNG exportado)

**Decir mientras lo muestras:**

> "El flujo de datos es directo: la UI solicita datos al DataExtractor que actúa como **Facade Pattern**, este delega a los Providers que usan sus Adapters para consultar las APIs. Los datos se normalizan en el Normalizer, se crean las Series, se construye el Portfolio y se ejecuta Monte Carlo."

### C. Clases de Objetos del Sistema:

**Mencionar las diferentes clases de objetos:**

```
📦 OBJETOS DE DATOS:
  - PriceSeries: Precios OHLCV históricos
  - PerformanceSeries: Retornos y performance
  - VolatilitySeries: Volatilidad histórica
  
💼 OBJETOS DE NEGOCIO:
  - Portfolio: Colección de símbolos con pesos
  - MonteCarloSimulation: Resultados de simulación
  
🔧 OBJETOS DE INFRAESTRUCTURA:
  - Adapters: Conectores a APIs
  - Providers: Orquestadores
  - Normalizer: Unificador de formatos
```

### Patrones de Diseño Aplicados:

**Mencionar brevemente (ya mostrados en los diagramas):**

✅ **Facade Pattern** - DataExtractor como punto de entrada único  
✅ **Adapter Pattern** - Abstrae las diferentes APIs  
✅ **Provider Pattern** - Orquesta descarga y normalización  
✅ **Template Method** - BaseSeries define comportamiento común

---

## 3️⃣ USO DE GITHUB (30 segundos)

### Qué Explicar:

> "He utilizado GitHub para gestionar todo el desarrollo del proyecto con buenas prácticas profesionales."

### A. Estructura del Repositorio

```
✅ README.md profesional
✅ Documentación completa (QUICKSTART, ARCHITECTURE)
✅ .gitignore configurado (protege .env con API keys)
✅ Requirements.txt con todas las dependencias
✅ Tests unitarios e integración
✅ Diagramas en docs/
```

### B. Gestión de Versiones

**Mencionar:**
- Commits descriptivos con convención semántica (Conventional Commits)
- Ejemplos de commits recientes:
  - `feat: Implementar Monte Carlo con retornos logaritmicos y mejorar documentacion`
  - `feat: Add Tiingo data source with secure API key management`
- Historial de cambios claro y trazable
- Versionado semántico del proyecto (v0.1.0)

### C. Seguridad

**Importante mencionar:**
- Archivo `.env` para API keys (NUNCA se sube)
- `.env.example` como plantilla para otros usuarios
- `.gitignore` protege información sensible

### D. Colaboración

- README con instrucciones claras de instalación
- Documentación para que otros puedan contribuir
- Tests para asegurar calidad del código

### Qué Mostrar:
- Pantalla de GitHub con el repositorio
- Historial de commits
- Estructura de archivos

### Tu Respuesta (Natural):

> "He usado GitHub para todo el desarrollo. Los commits son semánticos - 'feat: tal cosa', 'refactor: optimizar lo otro' - así queda claro qué hace cada cambio sin tener que ponerse a leer todo el código.
> 
> La documentación está a tres niveles: README para hacerte una idea general, QUICKSTART si quieres arrancar rápido, y ARCHITECTURE si te interesan los detalles matemáticos del Monte Carlo.
> 
> También tengo .gitignore configurado para no subir API keys ni logs, que parece obvio pero es importante. Y uso Mermaid para los diagramas porque se renderizan directo en GitHub."

---

## 4️⃣ UNIFICACIÓN DE FORMATOS (30 segundos)

### Por Qué Estas Tres Fuentes:

**He elegido Yahoo Finance, Binance y Tiingo estratégicamente:**

1. **Yahoo Finance** - Datos de mercados tradicionales (NYSE, NASDAQ) gratuitos y confiables. Es la fuente principal para acciones.

2. **Binance** - El mayor exchange de criptomonedas del mundo. Datos en tiempo real de cripto con alta frecuencia (hasta 1 minuto). API pública sin autenticación.

3. **Tiingo** - Datos profesionales ajustados por dividendos y splits. Cubre tanto acciones como criptomonedas. Requiere API key pero tier gratuito es generoso.

**Cobertura completa:** Acciones (NYSE/NASDAQ) + Criptomonedas + Datos ajustados profesionales

### Descarga Paralela de Datos:

**Implementación de concurrencia con ThreadPoolExecutor:**

```python
# data_extractor/extractor.py
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_multi_symbols(self, symbols: List[str], **kwargs):
    results = {}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Lanzar descarga de todos los símbolos en paralelo
        future_to_symbol = {
            executor.submit(self._fetch_single, symbol, **kwargs): symbol
            for symbol in symbols
        }
        
        # Recolectar resultados conforme terminan
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            results[symbol] = future.result()
    
    return results
```

**Beneficio:** Descargar 10 símbolos tarda lo mismo que descargar 1 (limitado solo por el API rate limit)

### El Problema de Formatos Diferentes:

Cada API devuelve datos en formatos diferentes:

**Yahoo Finance:**
```python
{
    "Open": [...],
    "Close": [...],
    "Adj Close": [...],  # ← Incluido
    "Volume": [...]
}
```

**Binance:**
```python
{
    "open": [...],      # ← Minúsculas
    "close": [...],
    "volume": [...]     # ← Sin Adj Close
}
```

**Tiingo:**
```python
{
    "adjOpen": [...],   # ← "adj" como prefijo
    "adjClose": [...],
    "date": "2024-01-01T00:00:00.000Z"  # ← ISO format
}
```

### La Solución: Pipeline de Normalización

#### Paso 1: Adapter normaliza su formato específico

```python
# tiingo_adapter.py
def _parse_to_dataframe(self, data, symbol):
    df = pd.DataFrame(data)
    
    # Renombrar columnas al estándar
    df.rename(columns={
        'adjOpen': 'Open',
        'adjHigh': 'High',
        'adjLow': 'Low',
        'adjClose': 'Close',
        'adjVolume': 'Volume'
    }, inplace=True)
    
    # Añadir Adj Close (ya ajustado)
    df['Adj Close'] = df['Close']
    
    return df
```

#### Paso 2: BaseAdapter valida formato estándar

```python
# base_adapter.py
REQUIRED_OHLCV_COLS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]

def _validate_ohlcv(self, df):
    """Valida que el DataFrame tenga todas las columnas requeridas"""
    missing = set(REQUIRED_OHLCV_COLS) - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {missing}")
```

#### Paso 3: Normalizer unifica fechas y tipos

```python
# normalizer.py
def normalizer_tipology(raw_frames, kind, align='intersect'):
    # 1. Convertir fechas a datetime
    for df in raw_frames.values():
        df.index = pd.to_datetime(df.index)
    
    # 2. Alinear series temporalmente
    if align == 'intersect':
        # Solo fechas comunes
        dates = set.intersection(*[set(df.index) for df in raw_frames.values()])
    
    # 3. Convertir a tipo específico (PriceSeries, ReturnsSeries, etc.)
    return crear_series_tipadas(raw_frames, kind)
```

### Formato Final Estándar:

```python
DataFrame:
    Index: DatetimeIndex (timezone-aware)
    Columns: ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    Dtype: float64
    Sorted: Por fecha ascendente
    No NaN: Validado
```

### Qué Mostrar:
- Código del pipeline de normalización
- Ejemplo de datos antes/después

### Tu Respuesta (Directa):

> "El problema es que cada API te devuelve los datos a su manera. Yahoo dice 'Close', Binance dice 'close' en minúscula, Tiingo dice 'adjClose'... un lío.
> 
> Lo he resuelto con un **pipeline de normalización** que tiene tres pasos: 
> 
> 1. Cada **Adapter** convierte su formato específico al estándar interno (columnas OHLCV).
> 
> 2. **BaseAdapter** valida que todas las columnas requeridas estén presentes.
> 
> 3. **Normalizer** alinea las fechas temporalmente y crea objetos tipados (PriceSeries, ReturnsSeries).
> 
> Esto garantiza que independientemente de la fuente, los datos llegan al usuario en un formato consistente y listo para análisis."

---

## 5️⃣ CONSTRUCCIÓN DE CARTERA (30 segundos)

### Cómo Funciona:

#### A. Entrada del Usuario

```
Símbolos: AAPL, MSFT, GOOGL
Pesos: 40%, 30%, 30%
Capital inicial: 10,000€
```

#### B. Descarga de Datos

```python
# extractor.py
data_map = extractor.get_market_data(
    tickers=['AAPL', 'MSFT', 'GOOGL'],
    start='2023-01-01',
    end='2024-01-01',
    kind='ohlcv'
)
# Resultado: Dict[str, PriceSeries]
```

#### C. Validación de Pesos

```python
# cartera_sidebar.py
def validar_pesos(pesos):
    total = sum(pesos.values())
    if abs(total - 100) > 0.01:
        # Auto-normalizar
        factor = 100 / total
        return {s: w * factor for s, w in pesos.items()}
    return pesos
```

#### D. Creación del Portfolio

```python
# portfolio.py
class Portfolio:
    def __init__(self, symbols, weights, prices_df):
        self.symbols = symbols
        self.weights = np.array(weights) / 100  # [0.4, 0.3, 0.3]
        self.prices = prices_df
        
    def calculate_returns(self):
        # Retornos logarítmicos
        returns = np.log(self.prices / self.prices.shift(1))
        return returns.dropna()
    
    def portfolio_returns(self):
        # Retorno ponderado de la cartera
        returns = self.calculate_returns()
        return (returns * self.weights).sum(axis=1)
```

#### E. Métricas Calculadas

```python
# Retorno esperado anualizado
expected_return = portfolio_returns.mean() * 252

# Volatilidad anualizada
volatility = portfolio_returns.std() * np.sqrt(252)

# Ratio de Sharpe (asumiendo rf=0)
sharpe_ratio = expected_return / volatility

# Matriz de covarianza
cov_matrix = returns.cov() * 252
```

### Qué Mostrar:
- Pestaña de Cartera con entrada de pesos
- Visualización de distribución de la cartera
- Tabla con métricas calculadas

### Script Sugerido:

> "La construcción de la cartera tiene cuatro pasos: 
> 
> 1. El usuario ingresa símbolos y pesos, que se validan y normalizan automáticamente.
> 
> 2. Se descargan los precios históricos para todos los símbolos.
> 
> 3. Se calculan retornos logarítmicos y se ponderan según los pesos de la cartera.
> 
> 4. Se calculan métricas clave: retorno esperado, volatilidad y ratio de Sharpe anualizados.
> 
> La interfaz muestra una visualización de la distribución y permite ajustar pesos de forma interactiva."

---

## 6️⃣ MÉTODO DE MONTE CARLO (1 minuto)

### Fundamento Teórico:

**Movimiento Browniano Geométrico (GBM) con Retornos Logarítmicos:**

```
Formulación discreta (implementada):
log(S_t/S_{t-1}) = (μ - σ²/2)Δt + σ√Δt × Z

Equivalente en forma continua:
S(t) = S₀ × exp((μ - σ²/2)×t + σ×√t×Z)

Donde:
  S₀ = Precio inicial
  μ  = Retorno logarítmico esperado (drift)
  σ  = Volatilidad
  t  = Tiempo
  Δt = Incremento de tiempo (1 día)
  Z  = Variable aleatoria normal N(0,1)
  -σ²/2 = Corrección de Itô (crucial para eliminar sesgo)
```

### ¿Por Qué Retornos Logarítmicos?

✅ **Precios siempre positivos:** exp(x) > 0 para cualquier x  
✅ **Matemáticamente correcto:** Consistente con teoría de procesos estocásticos  
✅ **Sin sesgo:** La corrección de Itô (-σ²/2) garantiza E[S_t] = S₀ × e^(μt)  
✅ **Estándar profesional:** Usado en finanzas cuantitativas institucionales

### Implementación:

#### Paso 1: Parámetros de Entrada

```python
# Usuario configura:
n_simulaciones = 1000       # Número de trayectorias
horizonte_dias = 252        # 1 año (252 días hábiles)
capital_inicial = 10000     # €10,000
volatilidad_variable = True # Volatilidad dinámica
```

#### Paso 2: Cálculo de Parámetros (Log-Based)

```python
# portfolio.py
def set_prices(self, prices_df):
    """Calcula retornos LOGARÍTMICOS automáticamente"""
    self.prices = prices_df
    # Retornos logarítmicos: log(P_t / P_{t-1})
    self.returns = np.log(prices_df / prices_df.shift(1)).dropna()

# monte_carlo.py
def _calculate_parameters(self):
    # μ: retorno logarítmico medio diario
    mu = self.portfolio.portfolio_return()  # Ya es log-return
    
    # σ: volatilidad anualizada
    sigma_annual = self.portfolio.portfolio_volatility()
    
    # Convertir a diaria: σ_diaria = σ_anual / √252
    sigma_daily = sigma_annual / np.sqrt(252)
    
    # Drift con corrección de Itô: (μ - σ²/2)
    drift = mu - 0.5 * (sigma_daily ** 2)
    
    return drift, sigma_daily
```

#### Paso 3: Simulación con Retornos Logarítmicos

```python
def simulate_portfolio(self):
    """Simulación usando retornos logarítmicos y corrección de Itô"""
    
    # Generar todos los shocks aleatorios de una vez (vectorizado)
    shocks = np.random.normal(0, 1, size=(n_simulations, time_horizon))
    
    # Calcular retornos LOGARÍTMICOS con corrección de Itô
    if dynamic_volatility:
        # Volatilidad variable: σ × [0.8, 1.2]
        vol_multipliers = np.random.uniform(0.8, 1.2, size=(n_simulations, time_horizon))
        vols_daily = vol_daily * vol_multipliers
        drift = portfolio_return - 0.5 * (vols_daily ** 2)
        diffusion = vols_daily * shocks
    else:
        # Volatilidad constante
        drift = portfolio_return - 0.5 * (vol_daily ** 2)  # ← Corrección de Itô
        diffusion = vol_daily * shocks
    
    # Retornos logarítmicos: log(S_t/S_{t-1})
    log_returns = drift + diffusion
    
    # Convertir log-returns a factores de crecimiento: S_t/S_{t-1} = exp(log_return)
    growth_factors = np.exp(log_returns)  # ← Garantiza precios positivos
    
    # Trayectorias: multiplicación acumulada
    trajectories = np.full((n_simulations, time_horizon + 1), initial_value)
    trajectories[:, 1:] = initial_value * np.cumprod(growth_factors, axis=1)
    
    return trajectories
```

#### Paso 3b: Volatilidad Dinámica (Opcional - Feature Avanzada)

**Qué es:**
- En el modelo básico, la volatilidad σ es **constante** durante toda la simulación
- Con volatilidad dinámica, σ **varía aleatoriamente** cada día entre 80% y 120% del valor base

**Código:**
```python
if dynamic_volatility:
    # Volatilidad cambia cada día: σ × [0.8, 1.2]
    vol_multipliers = np.random.uniform(0.8, 1.2, size=(n_simulations, time_horizon))
    vols_daily = vol_daily * vol_multipliers
    # Ejemplo: si σ_base = 20%, entonces σ_día puede ser 16%-24%
```

**¿Por qué es más realista?**
- En la realidad, la volatilidad **NO es constante**
- Aumenta en crisis, disminuye en períodos tranquilos
- Añade más variabilidad a las simulaciones

**¿Cuándo usarla?**
- ✅ Para análisis de sensibilidad
- ✅ Para simular escenarios de incertidumbre
- ❌ NO usar para comparaciones estándar (usa constante)

**En tu proyecto:**
- Por defecto: `False` (volatilidad constante - estándar)
- El usuario puede activarla desde la interfaz con un checkbox

#### Paso 4: Cálculo de Estadísticas

```python
def calculate_statistics(self, simulations):
    # Percentiles para intervalos de confianza
    percentiles = {
        'p5': np.percentile(simulations, 5, axis=0),
        'p25': np.percentile(simulations, 25, axis=0),
        'p50': np.percentile(simulations, 50, axis=0),  # Mediana
        'p75': np.percentile(simulations, 75, axis=0),
        'p95': np.percentile(simulations, 95, axis=0)
    }
    
    # Valor final esperado
    expected_final = simulations[:, -1].mean()
    
    # Valor en riesgo (VaR)
    var_95 = np.percentile(simulations[:, -1], 5)
    
    # Máxima pérdida potencial
    max_loss = S0 - var_95
    
    return percentiles, expected_final, var_95, max_loss
```

### Validación Matemática:

```python
# Verificar coherencia
E[S_T] = S0 * exp(μ × T)  # Valor esperado teórico

# Comparar con media de simulaciones
simulated_mean = simulations[:, -1].mean()
theoretical_mean = S0 * np.exp(mu * T)

error = abs(simulated_mean - theoretical_mean) / theoretical_mean
assert error < 0.05, "Error > 5%"
```

### Qué Mostrar:
- Pestaña Monte Carlo con parámetros
- Gráfico con 1000 trayectorias simuladas
- Bandas de confianza (5%, 25%, 50%, 75%, 95%)
- Estadísticas finales

### Script Sugerido:

> "La simulación usa un modelo de **movimiento browniano geométrico con retornos logarítmicos**:
> 
> 1. **Fórmula implementada:** log(S_t/S_{t-1}) = (μ - σ²/2)Δt + σ√Δt×Z
> 
> 2. El **término -σ²/2 es la corrección de Itô**, fundamental para eliminar el sesgo y garantizar que el valor esperado sea matemáticamente correcto.
> 
> 3. Los **retornos logarítmicos** tienen tres ventajas clave:
>    - Precios siempre positivos usando exp()
>    - Consistente con teoría de procesos estocásticos
>    - Es el estándar en finanzas cuantitativas profesionales
> 
> 4. Se generan **1000 trayectorias** vectorizadas aplicando shocks normales, calculando percentiles (5%, 25%, 50%, 75%, 95%) para intervalos de confianza.
> 
> 5. Se obtiene el **VaR (Valor en Riesgo)** que indica la pérdida máxima esperada con 95% de confianza.
> 
> 6. **Validación matemática:** He verificado que el error entre la media simulada y el valor teórico es menor al 2%, confirmando la corrección del modelo."

---

## 7️⃣ CONTENIDO DEL REPORTE (1 minuto)

### Estructura del Reporte:

#### A. Información de la Cartera

```markdown
## 📊 Información de la Cartera

**Capital Inicial:** €10,000.00
**Número de Activos:** 3
**Horizonte Temporal:** 252 días (1 año)

| Símbolo | Peso | Capital Asignado |
|---------|------|------------------|
| AAPL    | 40%  | €4,000.00       |
| MSFT    | 30%  | €3,000.00       |
| GOOGL   | 30%  | €3,000.00       |
```

**Criterio:** Información básica que contextualiza el análisis.

#### B. Métricas de Riesgo y Retorno

```markdown
## 📈 Métricas de Riesgo

**Retorno Esperado Anualizado:** 15.24%
**Volatilidad Anualizada:** 22.18%
**Ratio de Sharpe:** 0.687

**Interpretación:**
- Ratio de Sharpe > 0.5: Buena relación riesgo-retorno
- Volatilidad del 22%: Riesgo moderado-alto
```

**Criterio:** Métricas estándar de la industria financiera.

#### C. Resultados de Monte Carlo

```markdown
## 🎲 Resultados de la Simulación

**Parámetros:**
- Simulaciones: 1,000
- Horizonte: 252 días
- Método: Movimiento Browniano Geométrico

**Proyecciones:**
| Percentil | Valor Final |
|-----------|-------------|
| 5%        | €8,234.56   |
| 25%       | €9,456.78   |
| 50%       | €11,234.90  |
| 75%       | €13,567.12  |
| 95%       | €16,890.34  |

**Valor en Riesgo (VaR 95%):** €1,765.44
- Pérdida máxima esperada con 95% de confianza
```

**Criterio:** Resultados cuantitativos de la simulación para análisis de riesgo.

#### D. Análisis de Escenarios

```markdown
## 📊 Análisis de Escenarios

**Mejor Caso (P95):** €16,890.34 → +68.9% ganancia
**Caso Base (P50):** €11,234.90 → +12.3% ganancia
**Peor Caso (P5):**  €8,234.56  → -17.7% pérdida

**Probabilidad de Pérdida:** 32.4%
**Probabilidad de Ganancia >20%:** 18.7%
```

**Criterio:** Traducir percentiles a escenarios comprensibles.

#### E. Advertencias y Limitaciones

```markdown
## ⚠️ Advertencias y Consideraciones

### Limitaciones del Modelo:
- ❌ Asume retornos con distribución normal (no captura eventos extremos)
- ❌ No considera costos de transacción ni impuestos
- ❌ Volatilidad puede no ser constante en realidad
- ❌ No incluye correlaciones dinámicas entre activos

### Supuestos:
- ✓ Tasa libre de riesgo: 0%
- ✓ No hay dividendos ni splits
- ✓ Rebalanceo automático de la cartera
- ✓ Liquidez ilimitada

### Recomendaciones:
1. Usar como herramienta de orientación, no como garantía
2. Revisar regularmente y ajustar según condiciones de mercado
3. Considerar análisis complementarios (stress testing, backtesting)
4. Consultar con asesor financiero antes de decisiones importantes
```

**Criterio:** Transparencia sobre limitaciones y supuestos del modelo.

#### F. Visualizaciones Incluidas

1. **Gráfico de Trayectorias:** Muestra evolución de todas las simulaciones
2. **Distribución Final:** Histograma de valores finales
3. **Bandas de Confianza:** Percentiles sobre tiempo
4. **Comparación con Benchmark:** Si aplica

### Formato de Exportación:

```python
# Generación del reporte
def generate_report(self):
    report = []
    
    # Header con timestamp
    report.append(f"# Reporte de Simulación Monte Carlo")
    report.append(f"**Generado:** {datetime.now()}")
    
    # Cada sección
    report.append(self._section_portfolio_info())
    report.append(self._section_risk_metrics())
    report.append(self._section_monte_carlo_results())
    report.append(self._section_scenario_analysis())
    report.append(self._section_warnings())
    
    # Exportar
    with open('reporte.md', 'w') as f:
        f.write('\n\n'.join(report))
```

### Qué Mostrar:
- Pestaña de Reporte con todas las secciones
- Opción de descarga en Markdown
- Visualizaciones embebidas

---

### 🤔 EL RAZONAMIENTO DETRÁS (Para que lo entiendas bien)

**¿Por qué estas 5 secciones y no otras?**

#### **1. Composición** - Lo obvio primero
- **Razón práctica**: Si no sé qué activos tengo y en qué proporción, ¿cómo interpreto el resto?
- **Es básico**: Cualquier informe financiero empieza con esto
- **Sin esto**: El resto de métricas no tienen contexto

#### **2. Métricas principales** - Las que realmente se usan

**Retorno esperado:**
- Todo el mundo quiere saber "¿cuánto voy a ganar?"
- Es la media histórica proyectada al futuro
- Anualizado porque es más intuitivo (27% anual vs 0.0001 diario)

**Volatilidad:**
- El "riesgo" en términos cuantitativos
- 24% significa que en el 68% de los años, tu retorno estará entre +51% y +3% (27±24)
- Es la desviación estándar, punto - no hay métrica mejor para riesgo

**Sharpe Ratio:**
- Responde: "¿Me están compensando bien por el riesgo que asumo?"
- Si inviertes en algo muy volátil, debería darte más retorno que algo estable
- Sharpe > 1.0 → Vale la pena | < 0.5 → Mal negocio
- Es LA métrica de eficiencia (Premio Nobel 1990)

**¿Por qué NO otras métricas?**
- Beta → Necesitas un benchmark (S&P500). No tienes.
- Sortino → Sofisticación innecesaria para una práctica
- Treynor → Parecido a Sharpe, redundante
- Max Drawdown → Interesante pero no esencial aquí

#### **3. Análisis de riesgo** - Traducción a lenguaje humano
- **El problema**: Decir "volatilidad 0.2413" no significa nada para la mayoría
- **La solución**: "Riesgo MEDIO" lo entiende cualquiera
- **Criterio**: 
  - <15% → Bajo (bonos, utilidades)
  - 15-30% → Medio (acciones diversificadas)
  - >30% → Alto (tech concentrado, cripto)

#### **4. Matriz de correlación** - La realidad de la diversificación
- **Por qué es crítica**: Mucha gente cree que diversifica pero no lo hace
- **Ejemplo real**: AAPL + MSFT + GOOGL → Correlación ~0.85 → Todas suben/bajan juntas
- **Diversificación real**: Necesitas correlaciones <0.5
- **Sin esto**: Podrías creer que tienes 3 activos "diversos" cuando en realidad es casi como tener uno

#### **5. Advertencias** - Honestidad profesional
- **Concentración >40%**: Si tienes 60% en AAPL, no es una cartera, es apostar por AAPL
- **<5 activos**: Académicamente necesitas 15-20 para diversificar bien
- **Datos incompletos**: Si faltan muchos datos, las estadísticas son menos fiables
- **Por qué incluirlo**: Ética. Si ves un problema, lo dices. Punto.

---

### Script Sugerido (Con este conocimiento):

> "El reporte tiene **cinco secciones** y cada una está ahí por algo concreto:
> 
> **1. Composición de la cartera** - Tabla simple con tus activos y pesos. Básicamente, quieres saber dónde está tu dinero, ¿no?
> 
> **2. Métricas principales** - Las tres que realmente importan: retorno esperado, volatilidad y Sharpe. Son las que usa toda la industria porque funcionan. Retorno te dice cuánto ganas, volatilidad cuánto riesgo asumes, y Sharpe si vale la pena ese riesgo.
> 
> **3. Análisis de riesgo** - Clasifico la volatilidad en bajo, medio o alto. Si tienes 30% de volatilidad, el reporte te dice 'oye, esto es bastante riesgo'. Es para que lo entienda cualquiera, no solo gente de finanzas.
> 
> **4. Matriz de correlación** - Súper importante. Si metes AAPL, MSFT y GOOGL pensando que diversificas... pues no, todas son tech y se mueven igual. La matriz te lo muestra claramente.
> 
> **5. Advertencias** - Esto es básico, ¿no? Si tu cartera tiene el 50% en un solo activo, te lo tengo que decir. Si tienes muy pocos activos, te recomiendo más diversificación. Es ser honesto sobre las limitaciones del análisis.
> 
> El criterio ha sido **priorizar claridad**. Mejor 5 métricas que entiendas bien que 20 que no sepas qué significan."

---

## 8️⃣ CONCLUSIÓN (30 segundos)

### Qué Decir (CON TUS PROPIAS PALABRAS):

> "Este proyecto demuestra la importancia de las **estructuras y buenas prácticas** en Python. Decisiones como usar herencia, abstracciones y patrones de diseño pueden parecer engorrosas a pequeña escala, pero son las que permiten que el proyecto crezca y escale.
>
> He creado un sistema **modular y extensible** donde:
> - Las **abstracciones** (BaseAdapter, BaseProvider, BaseSeries) definen contratos claros
> - La **herencia** permite reutilizar código y mantener consistencia
> - Los **patrones de diseño** (Facade, Adapter, Template Method) hacen el código profesional
> - La **normalización** asegura que independientemente de la API, el formato de salida sea el mismo
> - La **concurrencia** optimiza el rendimiento descargando datos en paralelo
>
> El resultado: un programa que es **plug-n-play**, extensible y mantenible."

### Tecnologías Core:

```
🐍 Python 3.12 (Lenguaje principal)
   ├─ POO: Herencia, Abstracción, Encapsulación
   ├─ Dataclasses para objetos de negocio
   └─ ThreadPoolExecutor para paralelismo

📊 Procesamiento de Datos
   ├─ Pandas (series temporales)
   ├─ NumPy (cálculos vectorizados)
   └─ SciPy (estadísticas)

🔌 Integración de APIs
   ├─ Yahoo Finance, Binance, Tiingo
   ├─ Normalización de formatos
   └─ Descarga concurrente

📈 Interfaz de Usuario
   └─ Streamlit (capa visual)

🧪 Calidad
   ├─ Pytest (tests unitarios e integración)
   ├─ Type hints (Python 3.12+)
   └─ Documentación completa
```

### Valor del Proyecto:

> "No es solo una calculadora de Monte Carlo - es un **framework extensible** que puede crecer. Si mañana necesito agregar otra fuente de datos (Alpha Vantage, por ejemplo), solo creo `AlphaVantageAdapter` heredando de `BaseAdapter` e implemento sus métodos. El resto del sistema funciona sin cambios."

### 🚀 Rendimiento (Opcional - si te queda tiempo):

**Puedes mencionar brevemente:**

> "El sistema está optimizado: extrae datos en menos de 1 segundo, y ejecuta 10,000 simulaciones Monte Carlo completas en solo 0.2 segundos, equivalente a casi 50,000 simulaciones por segundo gracias a la vectorización de NumPy."

**Datos de benchmarks** (disponibles en `benchmarks/`):
- Extracción: ~0.9s (3 símbolos, 1 año)
- Monte Carlo: ~0.2s (10K simulaciones × 252 días)
- **Throughput**: ~48,000 simulaciones/segundo

### Puntos Fuertes del Proyecto:

✅ **Arquitectura modular:** Fácil de extender y mantener  
✅ **Múltiples fuentes:** Yahoo, Binance, Tiingo  
✅ **Alto rendimiento:** 48K simulaciones/segundo  
✅ **Validación matemática:** Simulación coherente  
✅ **Documentación completa:** README, QUICKSTART, ARCHITECTURE  
✅ **Tests implementados:** Unitarios e integración  
✅ **Seguridad:** Gestión segura de API keys  
✅ **Profesional:** Logs, error handling, deployment  

### Qué Mostrar:
- Repositorio de GitHub
- Estructura de carpetas
- Tests pasando

### Script Sugerido:

> "En resumen, he desarrollado una aplicación profesional de análisis financiero con arquitectura modular basada en patrones de diseño, simulación de Monte Carlo con validación matemática, y documentación completa. El proyecto está listo para producción con tests, sistema de logging, y deployment con Docker."

---

## 📝 CHECKLIST ANTES DE GRABAR

- [ ] Aplicación funcionando correctamente
- [ ] Tiingo configurado y probado
- [ ] Diagramas listos para mostrar
- [ ] Ejemplo de cartera preparado (ej: AAPL 40%, MSFT 30%, GOOGL 30%)
- [ ] Simulación Monte Carlo ejecutada con resultados
- [ ] Reporte generado y descargado
- [ ] GitHub actualizado y limpio
- [ ] Cronómetro para controlar tiempo

---

## 🎬 TIPS PARA GRABAR

1. **Ensaya** varias veces antes de grabar
2. **Usa un guion** pero no lo leas literalmente
3. **Muestra el código** solo lo necesario (diagramas > código)
4. **Enfatiza** los patrones de diseño y arquitectura
5. **Sé específico** con números y métricas
6. **Habla claro** y con confianza
7. **Controla el tiempo** - 5 minutos máximo
8. **Cierra fuerte** con conclusión clara

---

## ⏱️ DISTRIBUCIÓN FINAL DE TIEMPO (Usar como Checklist)

| Pregunta | Tiempo | Archivo/Pantalla a Mostrar | Puntos Clave |
|----------|--------|----------------------------|--------------|
| **Intro** | 20s | App funcionando | Demo rápida de las 4 pestañas |
| **❶ Estructura** | 40s | `docs/DIAGRAMAS.md` | 3 jerarquías + flujo |
| **❷ GitHub** | 30s | Repositorio GitHub | Commits semánticos + docs |
| **❸ Unificación** | 30s | `normalizer.py` | Ejemplo: Yahoo vs Binance |
| **❹ Cartera** | 30s | `portfolio.py` + UI | Dataclass + validación |
| **❺ Monte Carlo** | 60s | UI simulación | Fórmula GBM + resultados |
| **❻ Reporte** | 60s | UI reporte | 5 secciones + criterios |
| **Conclusión** | 30s | GitHub + tests | Tecnologías + puntos fuertes |
| **TOTAL** | **5:00** | - | - |

**🎯 REGLA DE ORO**: Si te pasas de 5 min, **reduce Intro/Conclusión**, NUNCA las 6 preguntas obligatorias.

---

---

# 📚 APÉNDICE: CUMPLIMIENTO DE REQUISITOS

> ⚠️ **NOTA**: Esta sección es SOLO para **referencia personal**, NO para el vídeo.
> 
> El vídeo debe centrarse únicamente en las **6 PREGUNTAS OBLIGATORIAS** explicadas arriba.

---

## 📋 Checklist Completo de Requisitos de la Práctica

Esta sección mapea cada requisito con su implementación. Úsala como referencia si el profesor hace preguntas adicionales o necesitas verificar algo.

---

### ✅ **1. Proyecto en GitHub con README detallado**

**Implementado:**
- Repositorio: `github.com/AlejandroGCN/analizador-bursatil`
- README completo con: Instalación, uso, arquitectura, ejemplos
- Commits semánticos con mensajes descriptivos
- `.gitignore` configurado
- Documentación adicional: QUICKSTART, ARCHITECTURE, GUIA_VIDEO

**Justificación**: README exhaustivo (>500 líneas) con instrucciones paso a paso, troubleshooting, y ejemplos.

---

### ✅ **2. Carpeta /src con núcleo del trabajo**

**Implementado:**
```
src/
├── data_extractor/      # Núcleo de extracción
├── simulation/          # Monte Carlo y Portfolio
├── data_cleaner/        # Limpieza de datos
├── reporting/           # Generación de reportes
├── ui/                  # Interfaz Streamlit
└── logs/                # Sistema de logging
```

**Justificación**: Código separado de tests, docs, y configs. Modular y escalable.

---

### ✅ **3. Plug-n-play (instalación fácil)**

**Implementado:**
- `install.py` - Instalador automático multi-plataforma
- `install.bat` - Para Windows (CMD)
- `requirements.txt` - Todas las dependencias con versiones
- `.env.example` - Template para API keys
- `ejemplos/` - Archivos de ejemplo para importar

**Justificación**: Usuario puede ejecutar `python install.py` y tener todo listo en 2 minutos.

---

### ✅ **4. Programa extractor multi-fuente**

**Implementado:**
- **3 fuentes**: Yahoo Finance, Binance, Tiingo
- **Clase**: `DataExtractor` (Facade Pattern)
- **Adapters**: `YahooAdapter`, `BinanceAdapter`, `TiingoAdapter`
- **Providers**: Orquestan descarga y normalización

**Código clave**: `src/data_extractor/extractor.py`

**Justificación**: Arquitectura extensible. Agregar nueva fuente = crear nuevo Adapter (Open/Closed Principle).

---

### ✅ **5. Formato de salida estandarizado**

**Implementado:**
- **Normalizer**: `src/data_extractor/core/normalizer.py`
- **Formato estándar**: OHLCV con columnas fijas: `['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']`
- **Índice estandarizado**: Timestamp con zona horaria
- **Validación**: Tipos de datos consistentes

**Código clave**: 
```python
def normalize_ohlcv(df, source_name):
    # Mapeo de columnas según fuente
    # Conversión a tipos numéricos
    # Índice temporal estandarizado
```

**Justificación**: Yahoo devuelve 'close', Binance 'closePrice' → Normalizer convierte todo a 'Close'. Portfolio funciona con cualquier fuente.

---

### ✅ **6. Tipología de datos adicional**

**Implementado:**
- **Precios históricos** (OHLCV)
- **Retornos logarítmicos** (`returns_log`)
- **Retornos porcentuales** (`returns_pct`)
- **Volatilidad** (rolling window)
- **Volumen de actividad** (volumen relativo)

**Código clave**: `src/data_extractor/series/` - 4 tipos de Series

**Justificación**: No solo precios. Usuario puede analizar performance, volatilidad histórica, y actividad del mercado.

---

### ✅ **7. Descarga de N series simultáneas**

**Implementado:**
```python
extractor.get_market_data(
    tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],  # N símbolos
    start='2020-01-01',
    end='2025-01-01'
)
```

**Técnica**: `ThreadPoolExecutor` para descargas paralelas (8 workers)

**Código clave**: `BaseAdapter._download_symbols_parallel()`

**Justificación**: Descarga 8 símbolos en paralelo en el tiempo que tomaría descargar 2-3 secuencialmente.

---

### ✅ **8. Series de datos como DataClasses**

**Implementado:**
```python
@dataclass
class PriceSeries(BaseSeries):
    symbol: str
    source: str
    data: pd.DataFrame  # OHLCV
```

**Jerarquía**:
- `BaseSeries` (abstracta)
  - `PriceSeries` - Precios OHLCV
  - `PerformanceSeries` - Retornos
  - `VolatilitySeries` - Volatilidad histórica
  - `VolumeActivitySeries` - Actividad de volumen

**Código clave**: `src/data_extractor/series/`

**Justificación**: Cada serie es un objeto con métodos propios (`.describe()`, `.to_dataframe()`). Type safety y encapsulación.

---

### ✅ **9. Concepto de Cartera (Portfolio)**

**Implementado:**
```python
@dataclass
class Portfolio:
    name: str
    symbols: list[str]
    weights: list[float]
    prices: Optional[pd.DataFrame] = None
    returns: Optional[pd.DataFrame] = None
```

**Definición**: Cartera = Conjunto de series de precios + pesos que suman 1.0

**Código clave**: `src/simulation/portfolio.py`

**Justificación**: Portfolio es una composición de múltiples series con pesos. Validación automática de que pesos sumen 100%.

---

### ✅ **10. Métodos estadísticos en DataClasses**

**Implementado en PriceSeries:**
```python
def get_ohlcv() -> pd.DataFrame
def describe() -> dict
def to_dataframe() -> pd.DataFrame
```

**Implementado en Portfolio:**
```python
def portfolio_return() -> float        # Media automática
def portfolio_volatility() -> float    # Std automática
def sharpe_ratio() -> float
def get_statistics() -> dict
```

**Justificación**: Media y desviación se calculan automáticamente al llamar `portfolio_return()` y `portfolio_volatility()`.

---

### ✅ **11. Simulación Monte Carlo**

**Implementado:**
- **Modelo**: Geometric Brownian Motion (GBM) con retornos logarítmicos
- **Fórmula**: `log(S_t/S_{t-1}) = (μ - σ²/2)Δt + σ√Δt × Z`
- **Corrección de Itô**: Incluida (`-σ²/2`)
- **Clase**: `MonteCarloSimulation` (métodos estáticos)

**Código clave**: `src/simulation/monte_carlo.py`

**Justificación**: Modelo matemáticamente correcto usado en la industria. Garantiza precios siempre positivos.

---

### ✅ **12. Parámetros maleables por usuario**

**Implementado:**
```python
@dataclass
class MonteCarloParams:
    n_simulations: int       # 100 - 10,000
    time_horizon: int        # 1 - 1,260 días
    initial_value: float     # $100 - $100M
    dynamic_volatility: bool # True/False
    random_seed: Optional[int]
```

**UI**: Controles en sidebar de Monte Carlo

**Justificación**: Usuario controla todos los parámetros clave de la simulación desde la interfaz.

---

### ✅ **13. Simulación de cartera Y elementos individuales**

**Implementado:**
```python
# Cartera completa
portfolio.monte_carlo_simulation(...)

# Activo individual
portfolio.monte_carlo_simulation_individual(symbol='AAPL', ...)
```

**UI**: Radio button "💼 Cartera completa" vs "📊 Activo individual"

**Código clave**: Métodos en `Portfolio` clase

**Justificación**: Dos modos de simulación con interfaz separada. Cartera usa pesos, individual usa precio actual.

---

### ✅ **14. Monte Carlo como método de Portfolio**

**Implementado:**
```python
class Portfolio:
    def monte_carlo_simulation(self, n_simulations, time_horizon, ...) -> pd.DataFrame:
        """Simula la cartera completa"""
        
    def monte_carlo_simulation_individual(self, symbol, ...) -> pd.DataFrame:
        """Simula un activo individual"""
```

**Justificación**: Monte Carlo está integrado en la clase Portfolio, no es una función suelta. Usa `self.returns`, `self.portfolio_volatility()`.

---

### ✅ **15. Visualización de resultados Monte Carlo**

**Implementado en Portfolio:**
```python
# Método NO requerido explícitamente en Portfolio,
# pero existe en MonteCarloSimulation:
MonteCarloSimulation.plot_simulation(results, title, figsize)
```

**UI**: Gráficos automáticos en vista Monte Carlo:
- Trayectorias de simulación (50 muestras)
- Distribución del valor final (histograma + boxplot)
- Tabla de resumen estadístico

**Justificación**: Visualización completa con matplotlib + Streamlit.

---

### ✅ **16. Limpieza y preprocesado de datos**

**Implementado:**
```python
class DataCleaner:
    def clean_dataframe(self, df) -> pd.DataFrame:
        # Elimina duplicados
        # Ordena índice
        # Rellena NaN con ffill/bfill
    
    def validate(self, df) -> list[str]:
        # Valida calidad de datos
```

**Input flexible**: Acepta cualquier serie temporal con índice de fechas

**Código clave**: `src/data_cleaner/cleaner.py`

**Justificación**: El programa acepta datos con problemas (duplicados, NaN, desorden) y los limpia automáticamente.

---

### ✅ **17. Método .report() en markdown**

**Implementado:**
```python
class Portfolio:
    def report(self, risk_free_rate=0.0, include_warnings=True) -> str:
        """Genera reporte en markdown con análisis completo"""
```

**Incluye:**
- Composición de cartera
- Métricas principales (retorno, volatilidad, Sharpe)
- Análisis de riesgo
- Matriz de correlación
- Advertencias sobre limitaciones

**Código clave**: `src/simulation/portfolio.py` línea ~550-650

**Justificación**: Retorna string en formato markdown. Exportable y legible.

---

### ✅ **18. Método .plots_report() con visualizaciones**

**Implementado:**
```python
class Portfolio:
    def plots_report(self, figsize=(18, 12), save_path=None, return_figure=False):
        """Genera 6 gráficos profesionales"""
```

**Visualizaciones:**
1. Evolución de precios históricos
2. Retornos acumulados por activo
3. Matriz de correlación (heatmap)
4. Distribución de retornos
5. Métricas clave (barras)
6. Volatilidad por activo

**Código clave**: `src/simulation/portfolio.py` línea ~700-750

**Justificación**: Suite completa de gráficos con matplotlib/seaborn. Exportables a PNG.

---

### ✅ **19. Diagrama de estructura (FossFlow o similar)**

**Implementado:**
- **Herramienta**: Mermaid (mejor que FossFlow - se ve en GitHub)
- **Diagramas**:
  1. `docs/diagrams/1_jerarquias_herencia.mmd` - Jerarquías de clases
  2. `docs/diagrams/2_flujo_arquitectura.mmd` - Flujo de datos
- **Renderizado**: `docs/DIAGRAMAS.md` (visible en GitHub)

**Justificación**: Mermaid se renderiza nativamente en GitHub. FossFlow requiere exportar imágenes. Más mantenible.

---

## 🎯 RESUMEN DE CUMPLIMIENTO

| Requisito | Estado | Evidencia |
|-----------|--------|-----------|
| GitHub + README | ✅ | README de 576 líneas |
| Carpeta /src | ✅ | Estructura modular |
| Plug-n-play | ✅ | `install.py` + ejemplos |
| Extractor multi-fuente | ✅ | 3 APIs implementadas |
| Formato estandarizado | ✅ | `Normalizer` + OHLCV estándar |
| Tipología adicional | ✅ | 5 tipos de series |
| N series simultáneas | ✅ | Descarga paralela (ThreadPool) |
| Series como DataClasses | ✅ | `BaseSeries` + 4 subclases |
| Concepto de Cartera | ✅ | `Portfolio` dataclass |
| Métodos estadísticos | ✅ | Media/std automáticos |
| Simulación Monte Carlo | ✅ | GBM con retornos log |
| Parámetros maleables | ✅ | `MonteCarloParams` |
| Sim. cartera + individual | ✅ | 2 métodos separados |
| MC como método Portfolio | ✅ | `.monte_carlo_simulation()` |
| Visualización MC | ✅ | Plots integrados |
| Limpieza de datos | ✅ | `DataCleaner` clase |
| `.report()` markdown | ✅ | Generación automática |
| `.plots_report()` | ✅ | 6 visualizaciones |
| Diagrama estructura | ✅ | Mermaid (2 diagramas) |

**TOTAL: 19/19 requisitos cumplidos** ✅

---

## 💡 PUNTOS EXTRAS IMPLEMENTADOS (No requeridos)

1. **Sistema de logging profesional** - Rotación automática, 4 niveles
2. **Tests unitarios** - 126 tests con pytest
3. **Benchmarks de rendimiento** - Scripts de medición
4. **Interfaz gráfica completa** - Streamlit con 4 pestañas
5. **Gestión segura de API keys** - Variables de entorno
6. **Docker deployment** - Listo para producción
7. **Validaciones robustas** - Pesos suman 100%, fechas válidas, tipos correctos
8. **Error handling** - Mensajes claros con sugerencias

---

**¡Buena suerte con el vídeo!** 🎥🚀
