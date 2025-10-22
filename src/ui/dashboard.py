# src/ui/dashboard.py
import os
import sys
import pandas as pd
import streamlit as st

THIS_DIR = os.path.dirname(__file__)
SRC_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))  # -> carpeta 'src'
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

from ui.input_normalizer import UiInputNormalizer, UiQuery
from typing import Dict, Union, cast# noqa: E402
from data_extractor import (  # noqa: E402
    DataExtractor,
    ExtractorConfig,
    PriceSeries,
    PerformanceSeries,
    VolatilitySeries,
    VolumeActivitySeries,
)


SeriesType = Union[PriceSeries, PerformanceSeries, VolatilitySeries, VolumeActivitySeries]

# ============================================================================
#  Analizador Bursátil — UI Streamlit
# ============================================================================
st.set_page_config(page_title="Analizador Bursátil", layout="wide")
st.title("📈 Analizador Bursátil")

# ── Helpers ───────────────────────────────────────────────────────────────────
def _source_key(ui_label: str) -> str:
    """Mapea etiqueta UI a clave del REGISTRY."""
    mapping = {
        "Yahoo Finance (sin API key)": "yahoo",
        "Alpha Vantage (requiere API key)": "alpha_vantage",
        "Binance (cripto)": "binance",
        "FRED (macro / tipos / índices)": "fred",
    }
    return mapping.get(ui_label, "yahoo")


def _kind_label_to_str(label: str) -> str:
    """Convierte la etiqueta legible a la cadena esperada por el extractor."""
    mapping = {
        "OHLCV (precios)": "ohlcv",
        "Rendimientos %": "returns_pct",
        "Rendimientos log": "returns_log",
        "Volatilidad (σ anualizada)": "volatility",
        "Actividad de volumen (z-score)": "volume_activity",
    }
    return mapping[label]


@st.cache_data(show_spinner=False)
def _fetch_data_cached(
        source_key: str,
        tickers_list,
        start_dt,             # fecha inicio
        end_dt,               # fecha fin
        interval_name: str,   # intervalo (1d, 1h, 1wk, 1mo)
        kind_name: str,       # tipología como string
) -> Dict[str, SeriesType]:
    cfg = ExtractorConfig(source=source_key, interval=interval_name)
    ex = DataExtractor(cfg=cfg)
    data = ex.get_market_data(
        tickers_list, start=start_dt, end=end_dt, kind=kind_name
    )
    # streamlit no infiere tipos; explicitamos para el IDE
    return cast(Dict[str, SeriesType], data)


def _series_to_csv(series_any: SeriesType) -> str:
    """Convierte un objeto de serie (PriceSeries / PerformanceSeries / etc.) a CSV."""
    if isinstance(series_any, PriceSeries):
        df = series_any.data.copy()
        df.insert(0, "symbol", series_any.symbol)
        return df.to_csv(index=True)

    # Series 1D (returns, volatility, volume z-score)
    if hasattr(series_any, "data") and isinstance(series_any.data, pd.Series):
        df = series_any.data.to_frame(name="value")
        df.insert(0, "symbol", series_any.symbol)
        return df.to_csv(index=True)

    # Fallback vacío
    return pd.DataFrame().to_csv(index=False)


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("Configuración")

source_label = st.sidebar.selectbox(
    "Fuente de datos:",
    [
        "Yahoo Finance (sin API key)",
        "Alpha Vantage (requiere API key)",
        "Binance (cripto)",
        "FRED (macro / tipos / índices)",
    ],
    index=0,
)

tickers_text = st.sidebar.text_input(
    "Tickers (separados por comas):",
    value="AAPL,MSFT,GSPC",  # ^GSPC en Yahoo para S&P 500
)

st.sidebar.markdown("#### 📂 O cargar una cartera desde archivo")
cartera_file = st.sidebar.file_uploader("Archivo de cartera (.csv o .txt)", type=["csv", "txt"])

tickers_text_manual = st.sidebar.text_input(
    "⬇️ O introduce tickers manualmente (separados por coma, espacio o salto de línea):",
    value=""
)

def parse_symbols_from_file(file) -> list[str]:
    content = file.read().decode("utf-8")
    raw = content.replace("\n", " ").replace(",", " ").split()
    return list(set(s.strip().upper() for s in raw if s.strip()))

def get_tickers_input() -> list[str]:
    if cartera_file:
        return parse_symbols_from_file(cartera_file)
    elif tickers_text_manual:
        return [t.strip().upper() for t in tickers_text_manual.replace("\n", ",").replace(" ", ",").split(",") if t.strip()]
    else:
        return []

col_l, col_r = st.sidebar.columns(2)
start_date_sel = col_l.date_input("Inicio", pd.to_datetime("2020-01-01"))
end_date_sel = col_r.date_input("Fin", pd.to_datetime("2025-01-01"))

interval_sel = st.sidebar.selectbox("Intervalo", ["1d", "1h", "1wk", "1mo"], index=0)

kind_label = st.sidebar.selectbox(
    "Tipología de datos",
    [
        "OHLCV (precios)",
        "Rendimientos %",
        "Rendimientos log",
        "Volatilidad (σ anualizada)",
        "Actividad de volumen (z-score)",
    ],
    index=0,
)

st.sidebar.markdown("---")

if st.sidebar.button("✅ Obtener datos"):
    try:
        # ⬇️ Normalización y validación centralizada
        q: UiQuery = UiInputNormalizer.normalize(
            tickers_text=tickers_text,
            start_date_sel=start_date_sel,
            end_date_sel=end_date_sel,
            interval_sel=interval_sel,
            kind_label=kind_label,
            kind_label_to_str=_kind_label_to_str,
        )

        if not q.symbols:
            st.sidebar.error("Introduce al menos un ticker.")
        else:
            with st.spinner("Descargando datos..."):
                data_map = _fetch_data_cached(
                    source_key=_source_key(source_label),
                    tickers_list=q.symbols,
                    start_dt=q.start_ts,
                    end_dt=q.end_ts,
                    interval_name=q.interval_name,
                    kind_name=q.kind_str,  # ← string estable
                )
                # Tipamos para el IDE (Streamlit guarda Any)
                st.session_state["series_map"] = cast(Dict[str, SeriesType], data_map)
                st.session_state["cfg_view"] = {
                    "source_label": source_label,
                    "symbols": q.symbols,
                    "start": q.start_ts,
                    "end": q.end_ts,
                    "interval": q.interval_name,
                    "kind_label": kind_label,
                    "kind_str": q.kind_str,
                }
                st.success("Datos descargados correctamente.")
                st.balloons()
    except Exception as e:
        st.sidebar.error(f"Error obteniendo datos: {e}")

# ── Main ──────────────────────────────────────────────────────────────────────
st.subheader("🧭 Selección actual")
if "cfg_view" in st.session_state:
    cfg_view = st.session_state["cfg_view"]
    st.markdown(
        f"**Fuente:** {cfg_view['source_label']}  \n"
        f"**Tickers:** {', '.join(cfg_view['symbols'])}  \n"
        f"**Rango:** {cfg_view['start']} → {cfg_view['end']}  \n"
        f"**Intervalo:** {cfg_view['interval']}  \n"
        f"**Tipología:** {cfg_view['kind_label']}"
    )
else:
    st.info("Configura la fuente y los tickers en la barra lateral y pulsa **Obtener datos**.")

tab_datos, tab_port, tab_sim, tab_report, tab_config = st.tabs(
    ["📊 Datos", "💼 Cartera", "🎲 Simulación", "🧾 Reporte", "⚙️ Configuración avanzada"]
)

with tab_datos:
    st.subheader("📊 Datos descargados")
    if "series_map" not in st.session_state:
        st.info("Aún no hay datos. Usa el botón **Obtener datos**.")
    else:
        series_map = cast(Dict[str, SeriesType], st.session_state["series_map"])
        cfg_view = st.session_state.get("cfg_view", {})
        kstr = cast(str, cfg_view.get("kind_str", "ohlcv"))

        if not series_map:
            st.warning("No se obtuvieron datos para los tickers seleccionados.")
        else:
            for sym, series_obj in series_map.items():
                with st.expander(f"🔹 {sym}", expanded=False):
                    if isinstance(series_obj, PriceSeries):
                        st.caption("OHLCV (últimas 10 filas)")
                        st.dataframe(series_obj.data.tail(10))
                        st.metric("Media (close)", f"{series_obj.mean():.4f}")
                        st.metric("Desv. típica (close)", f"{series_obj.std():.4f}")
                    elif isinstance(series_obj, PerformanceSeries):
                        st.caption("Rendimientos (últimas 10 filas)")
                        st.dataframe(series_obj.data.tail(10))
                        st.metric("Media (ret)", f"{series_obj.mean():.6f}")
                        st.metric("Desv. típica (ret)", f"{series_obj.std():.6f}")
                    elif isinstance(series_obj, VolatilitySeries):
                        st.caption("Volatilidad anualizada (últimas 10 filas)")
                        st.dataframe(series_obj.data.tail(10))
                        st.metric("Volatilidad media", f"{series_obj.mean_vol:.4f}")
                    elif isinstance(series_obj, VolumeActivitySeries):
                        st.caption("Z-score volumen (últimas 10 filas)")
                        st.dataframe(series_obj.data.tail(10))
                        st.metric("Media (z)", f"{series_obj.mean():.4f}")
                        st.metric("Desv. típica (z)", f"{series_obj.std():.4f}")
                    else:
                        st.warning("Formato no reconocido.")

                    st.download_button(
                        label="💾 Descargar CSV",
                        data=_series_to_csv(series_obj),
                        file_name=f"{sym}_{kstr}.csv",
                        mime="text/csv",
                    )

with tab_port:
    st.subheader("💼 Cartera (en desarrollo)")
    st.info("Aquí podrás construir una cartera a partir de las series descargadas.")

with tab_sim:
    st.subheader("🎲 Simulación Monte Carlo (en desarrollo)")
    st.info("Se configurará el horizonte, nº simulaciones, volatilidad dinámica, etc.")

with tab_report:
    st.subheader("🧾 Reporte (en desarrollo)")
    st.info("Se mostrará el .report() en Markdown y las visualizaciones de .plots_report().")

with tab_config:
    st.subheader("⚙️ Configuración avanzada")
    st.info("Aquí se gestionarán API keys y opciones de normalización.")
