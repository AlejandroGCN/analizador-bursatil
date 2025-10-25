# src/ui/views.py
from __future__ import annotations

from typing import Any, Dict, Callable
import streamlit as st
import pandas as pd
from ui.app_config import TAB_LABELS

# Tipos de parámetros que devuelve cada sidebar (para type hints y claridad)
from ui.sidebars import (
    DatosParams,
    CarteraParams,
    MonteCarloParams,
    ReporteParams,
    ConfigParams,
)

# Backend: descarga y normalización cacheadas
from ui.services_backend import fetch_market_data
# Config centralizada: mapeos UI→backend y helper de construcción de cfg/kind
from ui.app_config import build_cfg_and_kind


# ───────────────────────────────────────────────────────────────
# Renderizadores de contenido por pestaña
# ───────────────────────────────────────────────────────────────

def tab_datos(submit: bool, params: DatosParams | None) -> None:
    """Contenido central de la pestaña 📊 Datos."""
    st.subheader("📊 Vista de datos")

    # Cuando el usuario envía el formulario del sidebar de Datos
    if submit and params is not None:
        try:
            # Traducir etiquetas de la UI a claves internas y construir cfg
            cfg_dict, kind = build_cfg_and_kind(
                params.fuente,
                params.tipo,
                params.intervalo,
            )

            with st.spinner("Cargando datos…"):
                # Convertir string de símbolos a lista
                symbols_list = [s.strip() for s in params.simbolos.split(",") if s.strip()]
                
                data_map = fetch_market_data(
                    cfg_dict=cfg_dict,
                    symbols=symbols_list,
                    start=params.fecha_ini,
                    end=params.fecha_fin,
                    interval=params.intervalo,
                    kind=kind,
                )

            if not data_map:
                st.warning("No se recibieron datos.")
                return

            # Limpiar cache anterior
            if "last_data_map" in st.session_state:
                del st.session_state["last_data_map"]
            
            # Persistir resultado
            st.session_state["last_data_map"] = data_map
            st.session_state["last_kind"] = kind

            _data_map(data_map, kind)

        except Exception as e:
            st.error(f"❌ Error obteniendo datos: {e}")

    # Si no hay submit, intenta mostrar el último resultado cacheado
    elif "last_data_map" in st.session_state:
        st.info("Mostrando últimos datos descargados (cache).")
        data_map = st.session_state["last_data_map"]
        kind = st.session_state.get("last_kind", "ohlcv")
        _data_map(data_map, kind)


def tab_cartera(submit: bool, params: CarteraParams | None) -> None:
    """Contenido central de la pestaña 💼 Cartera."""
    st.subheader("💼 Construcción de cartera")
    st.info("Selecciona activos y asigna pesos.")

    if submit and params is not None:
        # TODO: implementar validación de pesos (suma=1), cálculo retorno/vol/Sharpe, etc.
        st.success("✅ Pesos aplicados (pendiente de lógica de cartera).")


def tab_montecarlo(submit: bool, params: MonteCarloParams | None) -> None:
    """Contenido central de la pestaña 🎲 Monte Carlo."""
    st.subheader("🎲 Simulación Monte Carlo")
    
    # Verificar si hay datos disponibles
    if "last_data_map" not in st.session_state:
        st.warning("⚠️ Primero descarga datos en la pestaña '📊 Datos' para poder simular.")
        return
    
    if submit and params is not None:
        try:
            with st.spinner(f"Ejecutando {params.nsims} simulaciones..."):
                # Obtener datos históricos
                data_map = st.session_state["last_data_map"]
                
                # Crear cartera desde los datos
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
                from simulation import Portfolio
                
                # Extraer símbolos y crear DataFrame de precios
                prices_dict = {}
                for symbol, data_info in data_map.items():
                    if isinstance(data_info, dict) and "data" in data_info:
                        df = data_info["data"]
                    else:
                        df = getattr(data_info, "data", None)
                    
                    if df is not None:
                        # Extraer columna de cierre
                        close_col = next((c for c in df.columns if c.lower() == 'close'), None)
                        if close_col:
                            prices_dict[symbol] = df[close_col]
                
                if not prices_dict:
                    st.error("No se pudieron extraer precios de los datos.")
                    return
                
                # Crear DataFrame de precios
                prices_df = pd.DataFrame(prices_dict)
                
                # Usar cartera configurada si existe, sino pesos iguales
                if "portfolio_symbols" in st.session_state and "portfolio_weights" in st.session_state:
                    symbols = st.session_state["portfolio_symbols"]
                    weights = st.session_state["portfolio_weights"]
                    st.info(f"💼 Usando cartera configurada con {len(symbols)} activos")
                else:
                    symbols = list(prices_dict.keys())
                    n_assets = len(symbols)
                    weights = [1.0 / n_assets] * n_assets
                    st.info(f"📊 Usando pesos iguales (1/{n_assets} = {1.0/n_assets:.2%} cada uno)")
                
                portfolio = Portfolio(
                    name="Portfolio",
                    symbols=symbols,
                    weights=weights
                )
                portfolio.set_prices(prices_df)
                
                # Ejecutar simulación
                results = portfolio.monte_carlo_simulation(
                    n_simulations=params.nsims,
                    time_horizon=params.horizonte,
                    dynamic_volatility=params.vol_dinamica,
                    random_seed=42
                )
                
                # Guardar resultados en session state
                st.session_state["montecarlo_results"] = results
                st.session_state["montecarlo_portfolio"] = portfolio
                
                st.success(f"✅ Simulación completada exitosamente!")
            
            # Mostrar resultados
            _show_montecarlo_results(results, portfolio)
            
        except Exception as e:
            st.error(f"❌ Error en simulación: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # Mostrar últimos resultados si existen
    elif "montecarlo_results" in st.session_state:
        st.info("Mostrando último resultado de simulación.")
        _show_montecarlo_results(
            st.session_state["montecarlo_results"],
            st.session_state.get("montecarlo_portfolio")
        )


def tab_reporte(submit: bool, params: ReporteParams | None) -> None:
    """Contenido central de la pestaña 📋 Reporte."""
    st.subheader("📋 Reporte")
    st.info("Informe resumen del análisis.")

    if submit and params is not None:
        # TODO: generar Markdown/HTML/PDF y permitir descarga
        st.success("✅ Reporte generado (pendiente de render).")


def tab_config(submit: bool, params: ConfigParams | None) -> None:
    """Contenido central de la pestaña ⚙️ Configuración."""
    st.subheader("⚙️ Configuración avanzada")
    st.info("Ajusta parámetros globales y claves API.")

    if submit and params is not None:
        # TODO: guardar API keys de forma segura (st.secrets o almacén externo)
        st.success("✅ Configuración guardada.")


# ───────────────────────────────────────────────────────────────
# Despachador único de contenido por pestaña
# ───────────────────────────────────────────────────────────────

TAB_TO_VIEW: Dict[str, Callable[[bool, Any], None]] = {
    TAB_LABELS["datos"]: tab_datos,
    TAB_LABELS["cartera"]: tab_cartera,
    TAB_LABELS["montecarlo"]: tab_montecarlo,
    TAB_LABELS["reporte"]: tab_reporte,
    TAB_LABELS["config"]: tab_config,
}

def content_for(tab: str, submit: bool, params: Any) -> None:
    """
    Renderiza el contenido central para la pestaña indicada.
    Si no hay función asociada, no muestra nada.
    """
    fn = TAB_TO_VIEW.get(tab)
    if fn:
        fn(submit, params)


# ───────────────────────────────────────────────────────────────
# Helpers privados
# ───────────────────────────────────────────────────────────────

def _data_map(data_map: dict, kind: str) -> None:
    """
    Renderiza tablas y gráficos rápidos para el resultado normalizado.
    `data_map`: Dict[str, dict] con formato serializable del cache.
    Optimizado para reducir uso de memoria.
    """
    for sym, data_info in data_map.items():
        st.markdown(f"### {sym}")

        # Manejar el nuevo formato serializable
        if isinstance(data_info, dict) and "data" in data_info:
            df = data_info["data"]
            series_type = data_info.get("type", "Unknown")
        else:
            # Fallback para formato anterior
            df = getattr(data_info, "data", None)
            series_type = type(data_info).__name__

        if df is None:
            # Fallback: mostrar objeto tal cual si no tiene .data
            st.write(data_info)
            continue

        # Mostrar todos los datos del rango seleccionado con altura personalizada
        st.dataframe(df, height=400, use_container_width=True)
        
        # Mostrar información del rango de fechas
        if not df.empty:
            st.info(f"📅 **Rango de datos:** {df.index.min().strftime('%Y-%m-%d')} a {df.index.max().strftime('%Y-%m-%d')} ({len(df)} registros)")

        # Gráficos optimizados - mostrar todos los datos
        if kind == "ohlcv":
            # Busca columna de cierre con tolerancia a capitalización
            close_col = next((c for c in df.columns if c.lower() == "close"), None)
            if close_col:
                chart_data = df[close_col]
                st.line_chart(chart_data)
            elif "Close" in df.columns:
                chart_data = df["Close"]
                st.line_chart(chart_data)
        else:
            if isinstance(df, pd.Series):
                chart_data = df
                st.line_chart(chart_data)
            elif "value" in getattr(df, "columns", []):
                chart_data = df["value"]
                st.line_chart(chart_data)


def _show_montecarlo_results(results: pd.DataFrame, portfolio: Any) -> None:
    """Muestra los resultados de la simulación Monte Carlo."""
    
    # Estadísticas de la cartera
    if portfolio is not None:
        stats = portfolio.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Retorno esperado", f"{stats['return']:.4f}")
        with col2:
            st.metric("Volatilidad", f"{stats['volatility']:.4f}")
        with col3:
            st.metric("Sharpe Ratio", f"{stats['sharpe_ratio']:.4f}")
        with col4:
            st.metric("Activos", len(portfolio.symbols))
        
        st.divider()
    
    # Estadísticas del valor final
    final_values = results.iloc[:, -1]
    
    st.subheader("📊 Estadísticas del valor final")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Distribución del valor final:**")
        stats_dict = {
            "Media": f"${final_values.mean():,.2f}",
            "Mediana": f"${final_values.median():,.2f}",
            "Std Dev": f"${final_values.std():,.2f}",
            "Mínimo": f"${final_values.min():,.2f}",
            "Máximo": f"${final_values.max():,.2f}"
        }
        for key, value in stats_dict.items():
            st.write(f"- **{key}**: {value}")
    
    with col2:
        st.write("**Percentiles:**")
        percentiles_dict = {
            "5%": final_values.quantile(0.05),
            "25%": final_values.quantile(0.25),
            "50%": final_values.quantile(0.50),
            "75%": final_values.quantile(0.75),
            "95%": final_values.quantile(0.95)
        }
        for key, value in percentiles_dict.items():
            st.write(f"- **{key}**: ${value:,.2f}")
    
    st.divider()
    
    # Gráfico de trayectorias
    st.subheader("📈 Trayectorias de simulación")
    
    # Mostrar una muestra de trayectorias
    import numpy as np
    sample_size = min(100, len(results))
    sample_indices = np.random.choice(len(results), sample_size, replace=False)
    sample_results = results.iloc[sample_indices]
    
    st.line_chart(sample_results.T)
    
    st.divider()
    
    # Histograma del valor final
    st.subheader("📊 Distribución del valor final")
    
    import matplotlib.pyplot as plt
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histograma
    ax1.hist(final_values, bins=50, edgecolor='black', alpha=0.7)
    ax1.axvline(final_values.mean(), color='red', linestyle='--', label='Media')
    ax1.axvline(final_values.median(), color='green', linestyle='--', label='Mediana')
    ax1.set_xlabel('Valor final ($)')
    ax1.set_ylabel('Frecuencia')
    ax1.set_title('Distribución del valor final')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot
    ax2.boxplot([final_values], vert=True)
    ax2.set_ylabel('Valor final ($)')
    ax2.set_title('Box Plot del valor final')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.divider()
    
    # Tabla de resumen
    st.subheader("📋 Resumen de simulación")
    st.dataframe(results.describe())
