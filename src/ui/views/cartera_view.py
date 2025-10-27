from __future__ import annotations
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from ui.sidebars import CarteraParams


def tab_cartera(submit: bool, params: CarteraParams | None) -> None:
    """Contenido central de la pestaña 💼 Cartera."""
    from ui.utils import display_symbol_info
    
    st.subheader("💼 Construcción de cartera")
    
    # Input de símbolos en el panel central (más espacio para ver todos)
    st.text_input(
        "📝 Símbolos:", 
        key="cartera_symbols",
        placeholder="Ej: AAPL, MSFT, GOOGL",
        help="Escribe los símbolos separados por coma (ej: AAPL, MSFT, GOOGL)",
        label_visibility="visible"
    )
    
    # Mostrar información de símbolos (solo si no hay símbolos configurados)
    display_symbol_info("cartera_symbols", contexto="cartera")
    
    st.divider()

    if submit and params is not None:
        try:
            # Parsear símbolos y pesos
            symbols = [s.strip() for s in params.symbols.split(",") if s.strip()]
            weights_str = [w.strip() for w in params.weights.split(",") if w.strip()]
            
            if not symbols:
                st.error("❌ Debes especificar al menos un activo.")
                return
            
            if len(weights_str) != len(symbols):
                st.error(f"❌ Número de pesos ({len(weights_str)}) debe coincidir con número de símbolos ({len(symbols)}).")
                return
            
            weights = [float(w) for w in weights_str]
            
            # Validar que los pesos sumen aproximadamente 1
            total_weight = sum(weights)
            if not (0.99 <= total_weight <= 1.01):
                st.warning(f"⚠️ Los pesos suman {total_weight:.3f} (deberían sumar 1.0). Ajustando proporcionalmente...")
                weights = [w / total_weight for w in weights]
            
            # Guardar en session state
            st.session_state["portfolio_symbols"] = symbols
            st.session_state["portfolio_weights"] = weights
            st.session_state["portfolio_valor_inicial"] = params.valor_inicial
            
            st.success(f"✅ Cartera configurada con {len(symbols)} activos")
            
        except Exception as e:
            st.error(f"❌ Error configurando cartera: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # Mostrar cartera guardada
    if "portfolio_symbols" in st.session_state and "portfolio_weights" in st.session_state:
        current_symbols_input = st.session_state.get("cartera_symbols", "")
        current_symbols_list = [s.strip() for s in current_symbols_input.split(",") if s.strip()]
        
        # Solo mostrar si los símbolos coinciden con la cartera guardada
        if current_symbols_list == st.session_state["portfolio_symbols"]:
            st.info("Mostrando cartera configurada actual.")
            _show_portfolio_info(st.session_state["portfolio_symbols"], st.session_state["portfolio_weights"])
        else:
            st.info("💡 Los símbolos han cambiado. Ajusta los pesos y haz click en 'Aplicar pesos' para actualizar la cartera.")


def _show_portfolio_info(symbols: list, weights: list) -> None:
    """
    Muestra información detallada de la cartera configurada.
    
    Args:
        symbols: Lista de símbolos de la cartera
        weights: Lista de pesos (fracciones, no porcentajes)
    """
    # Obtener valor inicial de la cartera
    valor_inicial = st.session_state.get("portfolio_valor_inicial", 10000.0)
    
    st.subheader("📋 Composición de la cartera")
    
    # Calcular valores en dólares para cada activo
    valores_dolares = [w * valor_inicial for w in weights]
    
    # Crear DataFrame con porcentajes y valores absolutos
    portfolio_df = pd.DataFrame({
        "Activo": symbols,
        "Peso (%)": [f"{w*100:.2f}%" for w in weights],
        "Valor ($)": [f"${v:,.2f}" for v in valores_dolares]
    })
    
    st.dataframe(portfolio_df, width='stretch', hide_index=True)
    
    # Mostrar resumen visual con barras
    st.subheader("📊 Distribución visual")
    
    # Crear gráfico de barras con matplotlib
    import numpy as np
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.tab10(range(len(symbols)))
    bars = ax.bar(symbols, valores_dolares, color=colors)
    
    # Añadir etiquetas en las barras con formato de dinero
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:,.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Activo', fontsize=12, fontweight='bold')
    ax.set_ylabel('Valor ($)', fontsize=12, fontweight='bold')
    ax.set_title('Distribución de valores en la cartera', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    
    # Formatear eje Y para mostrar dólares
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close(fig)

