"""
Monte Carlo Report Generator for portfolio analysis.
"""
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from typing import Any
import traceback
import pandas as pd


class MonteCarloReporter:
    """Generador de reportes con análisis Monte Carlo."""
    
    @staticmethod
    def show_montecarlo_summary() -> None:
        """
        Muestra un resumen del análisis Monte Carlo si está disponible.
        """
        if "montecarlo_results" in st.session_state and "montecarlo_portfolio" in st.session_state:
            st.subheader("🎲 Análisis Monte Carlo")
            results = st.session_state["montecarlo_results"]
            
            col1, col2, col3 = st.columns(3)
            final_values = results.iloc[:, -1]
            
            with col1:
                st.metric("💰 Valor medio esperado", f"${final_values.mean():,.2f}")
            with col2:
                st.metric("📊 Percentil 5%", f"${final_values.quantile(0.05):,.2f}")
            with col3:
                st.metric("📈 Percentil 95%", f"${final_values.quantile(0.95):,.2f}")
            
            st.info("💡 Estos valores provienen de una simulación Monte Carlo. Consulta la pestaña '🎲 Monte Carlo' para ver visualizaciones y análisis más detallados.")
            st.divider()
        else:
            st.info("💡 No hay simulaciones Monte Carlo disponibles. El reporte a continuación se basa únicamente en análisis estadístico de datos históricos.")
            st.divider()
    
    @staticmethod
    def show_portfolio_report(portfolio: Any) -> None:
        """
        Muestra el reporte completo de la cartera.
        
        Args:
            portfolio: Objeto Portfolio con los datos de la cartera
        """
        st.divider()
        
        # Mostrar resumen Monte Carlo si existe
        MonteCarloReporter.show_montecarlo_summary()
        
        # Generar reporte en markdown
        st.subheader("📄 Reporte en Markdown")
        report_md = portfolio.report(risk_free_rate=0.02, include_warnings=True)
        
        # Mostrar reporte
        st.markdown(report_md)
        
        st.divider()
        
        # Botón para descargar reporte
        st.download_button(
            label="📥 Descargar reporte en Markdown",
            data=report_md,
            file_name=f"reporte_cartera_{portfolio.name.lower().replace(' ', '_')}.md",
            mime="text/markdown"
        )
        
        st.divider()
        
        # Generar visualizaciones
        st.subheader("📊 Visualizaciones de la cartera")
        
        try:
            # Crear figura en memoria
            fig = plt.figure(figsize=(16, 10))
            
            # Generar visualizaciones usando el método plots_report
            portfolio.plots_report(figsize=(16, 10), save_path=None)
            
            # Guardar en memory buffer para mostrar en Streamlit
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            
            st.image(buffer, width='stretch')
            plt.close('all')
            
            st.divider()
            
            # Botón para descargar visualizaciones
            st.download_button(
                label="📥 Descargar gráficos (PNG)",
                data=buffer.getvalue(),
                file_name=f"visualizaciones_cartera_{portfolio.name.lower().replace(' ', '_')}.png",
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"Error generando visualizaciones: {e}")
            st.code(traceback.format_exc())

