# src/ui/error_handler.py
"""
Componente para manejo de errores mejorado en la UI
"""

import streamlit as st
import traceback
from typing import Any, Callable, Optional
from data_extractor.core.errors import ExtractionError, SymbolNotFound


def error_boundary(func: Callable, *args, **kwargs) -> Any:
    """
    Decorador para manejar errores de forma elegante en Streamlit.
    
    Args:
        func: Función a ejecutar
        *args: Argumentos posicionales
        **kwargs: Argumentos con nombre
        
    Returns:
        Resultado de la función o None si hay error
    """
    try:
        return func(*args, **kwargs)
    except SymbolNotFound as e:
        st.error(f"🚫 **Símbolo no encontrado**: {e.message}")
        st.info(f"💡 **Sugerencia**: Verifica que el símbolo '{e.symbol}' existe en la fuente '{e.source}'")
        st.code("Ejemplos válidos:\n- Yahoo: AAPL, MSFT, GOOGL\n- Binance: BTCUSDT, ETHUSDT\n- Stooq: AAPL.US, MSFT.US")
        return None
    except ExtractionError as e:
        st.error(f"⚠️ **Error de extracción**: {e.message}")
        if "pandas_datareader" in e.message:
            st.info("💡 **Solución**: Usa Yahoo Finance o Binance en lugar de Stooq")
            st.code("Fuentes recomendadas:\n- Yahoo Finance: Para acciones\n- Binance: Para criptomonedas")
        elif "timeout" in e.message.lower():
            st.info("💡 **Solución**: Verifica tu conexión a Internet y vuelve a intentar")
        return None
    except Exception as e:
        st.error(f"❌ **Error inesperado**: {str(e)}")
        
        # Mostrar detalles del error en un expander
        with st.expander("🔍 Detalles técnicos del error"):
            st.code(traceback.format_exc())
        
        # Sugerencias generales
        st.info("💡 **Posibles soluciones**:")
        st.markdown("""
        - Verifica tu conexión a Internet
        - Asegúrate de que los símbolos sean válidos
        - Intenta con un rango de fechas más pequeño
        - Reinicia la aplicación si el problema persiste
        """)
        
        return None


