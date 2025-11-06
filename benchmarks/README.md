# 🚀 Benchmarks de Rendimiento

Scripts para medir el rendimiento del sistema de análisis bursátil.

## 📊 Resultados de Referencia

Mediciones en hardware típico (Python 3.12, pandas 2.3.3, numpy 2.3.4):

| Operación | Tiempo | Detalles |
|-----------|--------|----------|
| **Extracción de datos** | ~0.9s | 3 símbolos, 1 año (Yahoo Finance) |
| **Procesamiento** | <1ms | Limpieza y validación de datos |
| **Creación de portfolio** | <1ms | 3-8 activos |
| **Monte Carlo (1K × 30 días)** | <0.01s | Simulación pequeña |
| **Monte Carlo (5K × 90 días)** | ~0.03s | Simulación mediana |
| **Monte Carlo (10K × 252 días)** | ~0.21s | Simulación grande (~48K sims/s) |

**Tiempo total típico**: 1-2 segundos para análisis completo

## 📁 Scripts Disponibles

### 1. `quick_benchmark.py` ⚡

**Benchmark rápido y directo** - Mide las operaciones clave del sistema.

```bash
python benchmarks/quick_benchmark.py
```

**Mide:**
- Extracción de datos (Yahoo Finance, 3 símbolos, 1 año)
- Procesamiento y limpieza de datos
- Creación y métricas de portfolio
- 3 simulaciones Monte Carlo de diferentes tamaños

**Salida:**
```
[1/4] Extracción de datos...
   -> Tiempo: 0.88s
   -> Símbolos extraídos: 3
   -> Filas por símbolo: 249

[2/4] Procesamiento de datos...
   -> Tiempo limpieza: 0.0005s

[3/4] Creación de portfolio...
   -> Activos: 3
   -> Retorno anual: 27.27%
   -> Volatilidad: 24.13%

[4/4] Simulación Monte Carlo...
   -> 1,000 sims x 30 días: 0.00s
   -> 5,000 sims x 90 días: 0.03s
   -> 10,000 sims x 252 días: 0.21s

TIEMPO TOTAL: 1.12s
```

### 2. `benchmark_performance.py` 🔬

**Benchmark completo y detallado** - Análisis exhaustivo con medición de memoria.

```bash
python benchmarks/benchmark_performance.py
```

**Características:**
- Mide tiempo **y** uso de memoria
- Múltiples escenarios de extracción de datos
- Benchmarks de procesamiento (limpieza, retornos, correlaciones)
- Operaciones de portfolio completas
- Suite completa de simulaciones Monte Carlo
- Resumen global por fases

**Ideal para:**
- Identificar cuellos de botella
- Optimizar uso de memoria
- Comparar rendimiento entre versiones
- Análisis de escalabilidad

## 🎯 Uso en Presentaciones

### Para la presentación oral:

> "El sistema es muy eficiente: extrae y procesa datos de 3 activos en menos de 1 segundo, 
> y ejecuta 10,000 simulaciones Monte Carlo completas (252 días) en solo 0.2 segundos, 
> lo que equivale a casi 50,000 simulaciones por segundo."

### Métricas destacables:

1. **Rapidez en extracción**: < 1s para obtener 1 año de datos históricos
2. **Procesamiento instantáneo**: < 1ms para limpiar y validar datos
3. **Monte Carlo ultrarrápido**: 48,000 simulaciones/segundo
4. **Escalabilidad**: El sistema paralelo permite procesar múltiples símbolos eficientemente

## 📈 Interpretación de Resultados

### Tiempos esperados según escenario:

| Escenario | Símbolos | Periodo | Simulaciones | Tiempo estimado |
|-----------|----------|---------|--------------|-----------------|
| Análisis rápido | 3-5 | 6 meses | 1,000 | ~0.5s |
| Análisis estándar | 5-8 | 1 año | 5,000 | ~1-2s |
| Análisis exhaustivo | 8-15 | 2 años | 10,000 | ~3-5s |
| Análisis institucional | 15-30 | 5 años | 20,000 | ~10-15s |

### Factores que afectan el rendimiento:

- **Red**: La extracción de datos depende de la velocidad de internet
- **API**: Yahoo Finance puede tener rate limits
- **Paralelización**: El sistema descarga múltiples símbolos en paralelo
- **Hardware**: CPU y RAM afectan las simulaciones Monte Carlo

## 🔧 Personalización

Puedes modificar los benchmarks para tus necesidades:

```python
# En quick_benchmark.py, línea ~40
symbols = ['AAPL', 'MSFT', 'GOOGL']  # Cambia los símbolos
start_date = end_date - timedelta(days=365)  # Cambia el periodo

# Línea ~90
n_simulations=10000  # Cambia número de simulaciones
time_horizon=252  # Cambia horizonte temporal
```

## 📝 Notas Técnicas

### Optimizaciones implementadas:

1. **DataFrame copies evitadas**: Solo se copian datos cuando es necesario
2. **Broadcasting de NumPy**: Operaciones vectorizadas para Monte Carlo
3. **ThreadPoolExecutor**: Descarga paralela de símbolos
4. **Lazy evaluation**: Cálculos solo cuando se solicitan

### Recomendaciones:

- Ejecutar benchmarks varias veces para obtener promedios estables
- Los primeros runs pueden ser más lentos (calentamiento de caché)
- Para mediciones precisas, cerrar otras aplicaciones pesadas
- En producción, considerar cachear datos para reducir llamadas a APIs

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

```bash
# Asegúrate de ejecutar desde el directorio raíz del proyecto
cd analizador-bursatil
python benchmarks/quick_benchmark.py
```

### Tiempos muy altos en extracción

- Verifica tu conexión a internet
- Yahoo Finance puede tener límites de tasa
- Considera usar un proxy o cambiar de fuente de datos

### Errores de memoria en simulaciones grandes

- Reduce `n_simulations` o `time_horizon`
- El sistema usa ~100MB para 10K simulaciones × 252 días
- Para portfolios grandes (>20 activos), considera ejecutar por lotes

---

**Última actualización**: Noviembre 2025  
**Versión del sistema**: 1.0.0  
**Python requerido**: 3.10+

