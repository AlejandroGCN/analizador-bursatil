from __future__ import annotations
from typing import Tuple
import streamlit as st
from .types import ReporteParams


def sidebar_reporte() -> Tuple[bool, ReporteParams]:
    st.sidebar.header("📋 Parámetros del Reporte")
    
    st.sidebar.markdown("📄 **Configuración**")
    
    incluir_riesgo = st.sidebar.checkbox(
        "Incluir métricas de riesgo", 
        value=True, 
        key="reporte_risk",
        help="Agrega VaR, escenarios y advertencias al reporte"
    )
    
    submitted = st.sidebar.button(
        "📄 Generar reporte",
        key="btn_generar_reporte",
        use_container_width=True
    )
    
    # Formato fijo: solo Markdown
    formato = "Markdown"
    
    return submitted, ReporteParams(formato, incluir_riesgo)

