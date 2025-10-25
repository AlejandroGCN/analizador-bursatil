# 🚀 Guía de Inicio Rápido - Analizador Bursátil

Esta guía te ayudará a instalar y usar el Analizador Bursátil en menos de 5 minutos.

## ⚡ Instalación Ultra-Rápida

### Windows
```cmd
# Descargar y ejecutar
git clone https://github.com/AlejandroGCN/analizador-bursatil.git
cd analizador-bursatil
install.bat
python run_app.py
```

### Linux/Mac
```bash
# Descargar y ejecutar
git clone https://github.com/AlejandroGCN/analizador-bursatil.git
cd analizador-bursatil
python install.py
python run_app.py
```

## 🎯 Primer Uso (2 minutos)

1. **Abrir la app**: Se abrirá automáticamente en `http://localhost:8501`

2. **Configuración básica**:
   - **Fuente**: Yahoo Finance
   - **Símbolos**: `AAPL,MSFT,GOOGL`
   - **Fechas**: Últimos 2 años
   - **Intervalo**: 1d (diario)

3. **Hacer clic en "Analizar"**

4. **¡Listo!** Verás gráficos y métricas automáticamente

## 📊 Ejemplos Rápidos

### Análisis de Acciones Tech
```
Fuente: Yahoo Finance
Símbolos: AAPL,MSFT,GOOGL,TSLA
Período: 2023-01-01 a 2024-01-01
Intervalo: 1d
```

### Análisis de Criptomonedas
```
Fuente: Binance
Símbolos: BTCUSDT,ETHUSDT,ADAUSDT
Período: Últimos 6 meses
Intervalo: 1h
```

### Análisis de Índices
```
Fuente: Yahoo Finance
Símbolos: ^GSPC,^DJI,^IXIC
Período: Últimos 5 años
Intervalo: 1d
```

## 🔧 Solución Rápida de Problemas

### ❌ "No module named 'streamlit'"
```bash
pip install -e .[dev]
```

### ❌ "Symbol not found"
- Usa símbolos de la lista de ejemplos
- Verifica que la fuente sea correcta
- Yahoo: `AAPL`, Binance: `BTCUSDT`, Stooq: `AAPL.US`

### ❌ App no se abre
```bash
# Puerto alternativo
streamlit run src/ui/dashboard.py --server.port 8502
```

### ❌ Error de conexión
- Verifica tu conexión a Internet
- Algunas fuentes pueden estar temporalmente no disponibles

## 📈 Funciones Principales

### 1. Análisis de Precios
- Gráficos OHLCV interactivos
- Comparación entre símbolos
- Análisis de tendencias

### 2. Métricas de Riesgo
- Volatilidad anualizada
- Ratio de Sharpe
- Retornos esperados

### 3. Simulación Monte Carlo
- 1000 simulaciones por defecto
- Intervalos de confianza
- Análisis de escenarios

### 4. Reportes Automáticos
- Análisis en Markdown
- Gráficos profesionales
- Advertencias de riesgo

## 🎨 Personalización

### Cambiar Configuración
1. Copia `config_example.yaml` a `config.yaml`
2. Modifica los valores por defecto
3. Reinicia la aplicación

### Agregar Símbolos
1. Ve a `ejemplos/symbols_example.txt`
2. Agrega tus símbolos favoritos
3. Usa el formato: `SÍMBOLO,Descripción,Fuente`

## 📚 Recursos Adicionales

- **README.md**: Documentación completa
- **ARCHITECTURE.md**: Documentación técnica
- **ejemplos/**: Archivos de ejemplo
- **tests/**: Tests unitarios

## 🆘 Soporte

Si tienes problemas:
1. Revisa esta guía
2. Consulta el README.md
3. Abre un issue en GitHub
4. Verifica que Python 3.10+ esté instalado

## 🎉 ¡Disfruta Analizando!

El Analizador Bursátil está diseñado para ser simple pero potente. 
¡Experimenta con diferentes símbolos y configuraciones!
