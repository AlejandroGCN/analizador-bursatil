# 📈 Analizador Bursátil

Aplicación **Streamlit** que descarga, normaliza y visualiza datos bursátiles históricos desde **Yahoo Finance**, **Binance** y **Stooq**, utilizando el motor modular del paquete `data_extractor`.

Permite seleccionar fuente, símbolos, rango temporal, tipo de dato (OHLCV, retornos o volatilidad), y visualizar los resultados en tablas y gráficos interactivos.

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
