# src/ui/error_handler.py
"""
Componente para manejo de errores mejorado en la UI
"""

import streamlit as st
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
        st.code("Ejemplos válidos:\n- Yahoo: AAPL, MSFT, GOOGL\n- Binance: BTCUSDT, ETHUSDT\n- Tiingo: AAPL, MSFT, BP (requiere API key)")
        return None
    except ExtractionError as e:
        st.error(f"⚠️ **Error de extracción**: {e.message}")
        if "API key" in e.message and "Tiingo" in e.message:
            st.info("💡 **Solución**: Configura tu API key de Tiingo")
            st.code("Obtén tu API key gratuita en: https://www.tiingo.com/\nLuego configura: export TIINGO_API_KEY='tu_key'")
        elif "timeout" in e.message.lower():
            st.info("💡 **Solución**: Verifica tu conexión a Internet y vuelve a intentar")
        return None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        
        # Registrar el error completo en los logs
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        
        # Mostrar solo mensaje de error al usuario (sin detalles técnicos)
        st.error(f"❌ **Error inesperado**: {str(e)}")
        
        # Sugerencias generales
        st.info("💡 **Posibles soluciones**:")
        st.markdown("""
        - Verifica tu conexión a Internet
        - Asegúrate de que los símbolos sean válidos
        - Intenta con un rango de fechas más pequeño
        - Reinicia la aplicación si el problema persiste
        """)
        
        return None


