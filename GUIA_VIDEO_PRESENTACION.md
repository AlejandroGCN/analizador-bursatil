# 🎥 Guía para Vídeo de Presentación (5 minutos)

Esta guía te ayudará a responder todas las preguntas del proyecto de forma clara y estructurada.

---

## 📋 Estructura del Vídeo (Minutaje)

```
00:00 - 00:30  Introducción y demostración rápida
00:30 - 01:30  Estructura del proyecto y arquitectura
01:30 - 02:00  Uso de GitHub
02:00 - 02:30  Unificación de datos de APIs
02:30 - 03:30  Construcción de cartera y Monte Carlo
03:30 - 04:30  Sistema de reportes
04:30 - 05:00  Conclusión y tecnologías
```

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

## 2️⃣ ESTRUCTURA DEL PROYECTO (1 minuto)

### Qué Explicar:

> "El proyecto sigue una **arquitectura modular** basada en **patrones de diseño** que garantizan escalabilidad y mantenibilidad."

### A. Diagrama de Arquitectura

**Mostrar:** `docs/diagrams/1_arquitectura_completa.mmd` o captura del diagrama

```
UI (Streamlit)
    ↓
DataExtractor (Facade)
    ↓
Provider (Orquestación)
    ↓
Adapter (Cliente API)
    ↓
API Externa
```

### B. Herencias y Dependencias

**Explicar con el diagrama de clases:**

#### 1. **Patrón Adapter** (Abstracción de APIs)

```python
BaseAdapter (Clase abstracta)
    ↓
├── YahooAdapter
├── BinanceAdapter
└── TiingoAdapter
```

**Por qué:** Cada fuente tiene su propia API y formato. El patrón Adapter permite:
- Interfaz unificada
- Fácil extensión (añadir nuevas fuentes)
- Cada adapter conoce los detalles de su API

#### 2. **Patrón Provider** (Orquestación)

```python
BaseProvider (Clase base)
    ↓
├── YahooProvider
├── BinanceProvider
└── TiingoProvider
```

**Por qué:** Encapsula lógica común:
- Descarga paralela de múltiples símbolos
- Manejo de errores
- Normalización de datos

#### 3. **Patrón Facade** (Punto de entrada único)

```python
DataExtractor
    ↓
Usa Provider
    ↓
Usa Adapter
```

**Por qué:** Simplifica la interfaz para el usuario:
- Un solo punto de entrada
- Oculta complejidad interna
- Fácil de usar desde la UI

#### 4. **Jerarquía de Series**

```python
BaseSeries (Clase base)
    ↓
├── PriceSeries (Precios OHLCV)
├── ReturnsSeries (Retornos)
├── VolatilitySeries (Volatilidad)
└── PerformanceSeries (Rendimiento)
```

**Por qué:** Diferentes tipos de datos financieros con comportamientos específicos.

### C. Dependencias Principales

```
UI Layer
  ↓ depende de
Backend Services
  ↓ depende de
DataExtractor
  ↓ depende de
Providers
  ↓ depende de
Adapters
```

**Bajo acoplamiento:** Cada capa solo conoce la capa inmediatamente inferior.

### Qué Mostrar:
- Diagrama de arquitectura completa
- Diagrama de jerarquía de clases
- Árbol de directorios del proyecto

### Script Sugerido:

> "La estructura se basa en tres patrones clave:
> 
> 1. **Adapter Pattern** para abstraer las diferentes APIs. Cada fuente (Yahoo, Binance, Tiingo) tiene su propio adapter que implementa una interfaz común.
> 
> 2. **Provider Pattern** que orquesta los adapters y añade funcionalidad común como descarga paralela y normalización.
> 
> 3. **Facade Pattern** en DataExtractor que ofrece una interfaz simple para la UI.
> 
> Esta arquitectura permite añadir nuevas fuentes de datos simplemente creando un nuevo adapter, sin modificar el código existente."

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
- Commits descriptivos con convención semántica
- Ejemplo: `feat: Add Tiingo data source with secure API key management`
- Historial de cambios claro

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

> "He usado GitHub siguiendo best practices: commits semánticos descriptivos, documentación completa, y seguridad mediante .gitignore para proteger las API keys. El repositorio incluye tests, diagramas y tres niveles de documentación: README para overview, QUICKSTART para inicio rápido, y ARCHITECTURE para detalles técnicos."

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

**Movimiento Browniano Geométrico (GBM):**

```
S(t) = S₀ × exp((μ - σ²/2)×t + σ×√t×Z)

Donde:
  S₀ = Precio inicial
  μ  = Retorno esperado (drift)
  σ  = Volatilidad
  t  = Tiempo
  Z  = Variable aleatoria normal (0,1)
```

### Implementación:

#### Paso 1: Parámetros de Entrada

```python
# Usuario configura:
n_simulaciones = 1000       # Número de trayectorias
horizonte_dias = 252        # 1 año (252 días hábiles)
capital_inicial = 10000     # €10,000
volatilidad_variable = True # Volatilidad dinámica
```

#### Paso 2: Cálculo de Parámetros

```python
# monte_carlo.py
def _calculate_parameters(self):
    # Retornos de la cartera
    returns = self.portfolio.portfolio_returns()
    
    # Drift (μ - σ²/2)
    mu = returns.mean()
    sigma = returns.std()
    drift = mu - 0.5 * sigma**2
    
    # Para volatilidaddinámica
    if self.variable_volatility:
        sigma_history = returns.rolling(window=30).std()
    
    return drift, sigma
```

#### Paso 3: Simulación

```python
def simulate(self):
    S0 = self.initial_capital
    results = np.zeros((self.n_simulations, self.time_horizon))
    
    for i in range(self.n_simulaciones):
        # Trayectoria individual
        path = [S0]
        
        for t in range(1, self.time_horizon):
            # Shock aleatorio
            Z = np.random.normal(0, 1)
            
            # Volatilidad (fija o variable)
            if self.variable_volatility:
                sigma_t = self._get_dynamic_volatility(t)
            else:
                sigma_t = self.sigma
            
            # Siguiente valor
            S_t = path[-1] * np.exp(
                self.drift + sigma_t * Z
            )
            path.append(S_t)
        
        results[i, :] = path
    
    return results
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

> "La simulación de Monte Carlo usa **movimiento browniano geométrico** para modelar la evolución de la cartera:
> 
> 1. Se calculan parámetros: **drift** (retorno esperado menos corrección de volatilidad) y **volatilidad**.
> 
> 2. Se generan **1000 trayectorias** aleatorias aplicando shocks normales.
> 
> 3. Para cada paso de tiempo, el nuevo valor se calcula como: S(t+1) = S(t) × exp(drift + volatilidad × shock).
> 
> 4. Se calculan **percentiles** (5%, 25%, 50%, 75%, 95%) para intervalos de confianza.
> 
> 5. Se obtiene el **Valor en Riesgo (VaR)** que indica la pérdida máxima esperada con 95% de confianza.
> 
> He implementado validación matemática para verificar que la media de las simulaciones coincide con el valor esperado teórico."

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

## ⏱️ DISTRIBUCIÓN DE TIEMPO SUGERIDA

| Tema | Tiempo | Importancia |
|------|--------|-------------|
| Estructura y patrones | 1:30 | ⭐⭐⭐⭐⭐ |
| Monte Carlo | 1:00 | ⭐⭐⭐⭐⭐ |
| Unificación datos | 0:30 | ⭐⭐⭐⭐ |
| Reporte | 1:00 | ⭐⭐⭐⭐ |
| GitHub | 0:30 | ⭐⭐⭐ |
| Cartera | 0:30 | ⭐⭐⭐ |

---

**¡Buena suerte con el vídeo!** 🎥🚀
