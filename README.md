# 📈 Analizador Bursátil

Aplicación **Streamlit** que descarga, normaliza y visualiza datos bursátiles históricos desde **Yahoo Finance**, **Binance** y **Stooq**, utilizando el motor modular del paquete `data_extractor`.

Permite seleccionar fuente, símbolos, rango temporal, tipo de dato (OHLCV, retornos o volatilidad), y visualizar los resultados en tablas y gráficos interactivos.

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

## 📁 Estructura del Proyecto

Para una documentación detallada de la arquitectura, consulta [ARCHITECTURE.md](ARCHITECTURE.md) que incluye:
- Diagramas Mermaid interactivos
- Flujo de datos detallado
- Patrones de diseño utilizados
- Tecnologías y dependencias
