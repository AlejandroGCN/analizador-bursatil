# 🎥 Guía para Vídeo de Presentación (5 minutos)

Esta guía te ayudará a responder todas las preguntas del proyecto de forma clara y estructurada.

---

## 📋 Estructura del Vídeo (Minutaje Optimizado)

### Distribución por Preguntas Requeridas:

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

### Prioridades:

| Pregunta | Tiempo | Importancia | Diagramas a Mostrar |
|----------|--------|-------------|---------------------|
| ❶ Herencias y dependencias | 40s | ⭐⭐⭐⭐⭐ | Diagrama 1 + Diagrama 2 |
| ❺ Monte Carlo | 60s | ⭐⭐⭐⭐⭐ | Pantalla de simulación |
| ❻ Reporte | 60s | ⭐⭐⭐⭐⭐ | Pantalla de reporte |
| ❸ Unificación APIs | 30s | ⭐⭐⭐⭐ | Código normalizer |
| ❹ Construcción cartera | 30s | ⭐⭐⭐⭐ | Pantalla cartera |
| ❷ GitHub | 30s | ⭐⭐⭐ | Repositorio GitHub |

---

## 1️⃣ INTRODUCCIÓN (30 segundos)

### Qué Decir:

> "He desarrollado un **Analizador Bursátil** con **Streamlit** que permite realizar simulaciones de Monte Carlo para análisis de riesgo financiero. La aplicación descarga datos de múltiples fuentes (Yahoo Finance, Binance y Tiingo), construye carteras personalizadas y genera reportes completos con proyecciones de riesgo."

### Qué Mostrar:
- Pantalla principal de la aplicación funcionando
- Cambio rápido entre las 4 pestañas: Datos, Cartera, Monte Carlo, Reporte

### Puntos Clave:
- ✅ Multi-fuente (3 APIs)
- ✅ Simulación Monte Carlo
- ✅ Reportes automáticos
- ✅ Interfaz intuitiva

---

## 2️⃣ ESTRUCTURA: HERENCIAS Y DEPENDENCIAS (40 segundos)

### Qué Explicar:

> "El proyecto sigue una **arquitectura modular** con **tres jerarquías de herencia principales** y un flujo de datos claro."

### A. PRIMERO: Mostrar Diagrama de Jerarquías (20s)

**Mostrar:** `docs/diagrams/1_jerarquias_herencia.mmd` (o PNG exportado)

**Decir mientras lo muestras:**

> "Como ven en este diagrama, tengo **tres jerarquías de herencia**:
> 
> 1. **BaseAdapter** del que heredan YahooAdapter, BinanceAdapter y TiingoAdapter - son las clases que se conectan directamente a cada API.
> 
> 2. **BaseProvider** del que heredan los tres providers - orquestan la descarga y normalización.
> 
> 3. **BaseSeries** del que heredan PriceSeries, PerformanceSeries y VolatilitySeries - representan diferentes tipos de datos financieros."

### B. SEGUNDO: Mostrar Flujo de Arquitectura (20s)

**Mostrar:** `docs/diagrams/2_flujo_arquitectura.mmd` (o PNG exportado)

**Decir mientras lo muestras:**

> "El flujo de datos es directo: la UI solicita datos al DataExtractor que actúa como **Facade Pattern**, este delega a los Providers que usan sus Adapters para consultar las APIs. Los datos se normalizan en el Normalizer, se crean las Series, se construye el Portfolio y se ejecuta Monte Carlo."

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

### Script Sugerido:

> "He usado GitHub siguiendo best practices: commits semánticos descriptivos usando Conventional Commits, documentación completa, y seguridad mediante .gitignore para proteger las API keys. 
> 
> Por ejemplo, mi último commit fue 'feat: Implementar Monte Carlo con retornos logarítmicos' que documenta claramente la funcionalidad añadida.
> 
> El repositorio incluye tests, diagramas Mermaid, y tres niveles de documentación: README para overview, QUICKSTART para inicio rápido, y ARCHITECTURE para detalles técnicos del modelo matemático."

---

## 4️⃣ UNIFICACIÓN DE FORMATOS (30 segundos)

### El Problema:

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

### Script Sugerido:

> "Cada API devuelve datos en formatos diferentes. He resuelto esto con un **pipeline de normalización en tres capas**: 
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

### Script Sugerido:

> "El reporte incluye **cinco secciones** con criterios específicos:
> 
> 1. **Información de Cartera:** Composición y capital asignado - criterio de contexto.
> 
> 2. **Métricas de Riesgo:** Retorno esperado, volatilidad y Sharpe - criterio: métricas estándar de la industria.
> 
> 3. **Resultados Monte Carlo:** Percentiles y VaR - criterio: análisis cuantitativo de riesgo.
> 
> 4. **Análisis de Escenarios:** Mejor caso, base y peor caso con probabilidades - criterio: interpretación práctica.
> 
> 5. **Advertencias:** Limitaciones del modelo y recomendaciones - criterio: transparencia y ética profesional.
> 
> El reporte es exportable en Markdown y incluye todas las visualizaciones. He priorizado claridad y honestidad sobre las limitaciones del modelo."

---

## 8️⃣ CONCLUSIÓN (30 segundos)

### Tecnologías y Herramientas:

```
🐍 Python 3.12
📊 Pandas, NumPy, SciPy
📈 Streamlit (UI)
🔌 yfinance, pandas_datareader (APIs)
🧪 Pytest (Testing)
🐳 Docker (Deployment)
📝 Markdown (Reportes)
🔐 python-dotenv (Seguridad)
```

### Puntos Fuertes del Proyecto:

✅ **Arquitectura modular:** Fácil de extender y mantener  
✅ **Múltiples fuentes:** Yahoo, Binance, Tiingo  
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

## ⏱️ DISTRIBUCIÓN FINAL DE TIEMPO

| Pregunta Requerida | Tiempo | Prioridad | Qué Mostrar |
|-------------------|--------|-----------|-------------|
| ❶ Herencias y dependencias | 40s | ⭐⭐⭐⭐⭐ | 2 diagramas en docs/DIAGRAMAS.md |
| ❷ Uso de GitHub | 30s | ⭐⭐⭐ | Repo + commits + docs |
| ❸ Unificación APIs | 30s | ⭐⭐⭐⭐ | Código normalizer.py |
| ❹ Construcción cartera | 30s | ⭐⭐⭐⭐ | Pantalla Cartera |
| ❺ Monte Carlo | 60s | ⭐⭐⭐⭐⭐ | Pantalla simulación + fórmula |
| ❻ Reporte y criterios | 60s | ⭐⭐⭐⭐⭐ | Pantalla reporte + secciones |
| **Intro + Conclusión** | 50s | - | Demo rápida + cierre |
| **Total** | **5:00** | - | - |

---

**¡Buena suerte con el vídeo!** 🎥🚀
