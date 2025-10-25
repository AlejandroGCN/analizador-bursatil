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
    st.info("Resultados y gráficos de simulación.")

    if submit and params is not None:
        # TODO: implementar simulación (trayectorias, histograma final, percentiles)
        st.success("✅ Simulación lanzada (pendiente de implementación).")


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
