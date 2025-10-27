from __future__ import annotations
from typing import Tuple
import streamlit as st
from .types import ReporteParams


def sidebar_reporte() -> Tuple[bool, ReporteParams]:
    with st.sidebar.form("form_reporte"):
        st.header("📋 Opciones de reporte")
        formato = st.selectbox("Formato", ["Markdown", "HTML", "PDF (WIP)"], key="reporte_fmt")
        incluir_riesgo = st.checkbox("Incluir métricas de riesgo", value=True, key="reporte_risk")
        submitted = st.form_submit_button("Generar reporte")
    return submitted, ReporteParams(formato, incluir_riesgo)

