from __future__ import annotations
from typing import Tuple
import streamlit as st
from .types import ReporteParams


def sidebar_reporte() -> Tuple[bool, ReporteParams]:
    st.sidebar.header("📋 Parámetros del Reporte")
    
    with st.sidebar.form("form_reporte"):
        st.markdown("📄 **Configuración**")
        
        formato = st.selectbox(
            "Formato de exportación", 
            ["Markdown", "HTML", "PDF (WIP)"], 
            key="reporte_fmt",
            help="Markdown: texto plano fácil de copiar | HTML: para web"
        )
        
        incluir_riesgo = st.checkbox(
            "Incluir métricas de riesgo", 
            value=True, 
            key="reporte_risk",
            help="Agrega VaR, escenarios y advertencias al reporte"
        )
        
        submitted = st.form_submit_button(
            "📊 Generar Reporte Completo",
            width='stretch'
        )
    
    return submitted, ReporteParams(formato, incluir_riesgo)

