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


def show_connection_status():
    """Muestra el estado de conexión y fuentes disponibles."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 Estado de Conexión")
    
    # Verificar fuentes disponibles
    sources_status = {
        "Yahoo Finance": "✅ Disponible",
        "Binance": "✅ Disponible", 
        "Stooq": "⚠️ Limitado (Python 3.12+)"
    }
    
    for source, status in sources_status.items():
        st.sidebar.markdown(f"**{source}**: {status}")
    
    st.sidebar.info("💡 **Consejo**: Yahoo Finance es la opción más confiable")


def show_help_tooltip():
    """Muestra ayuda contextual en la sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ❓ Ayuda Rápida")
    
    with st.sidebar.expander("📋 Símbolos Recomendados"):
        st.markdown("""
        **Yahoo Finance:**
        - AAPL, MSFT, GOOGL, TSLA, AMZN
        
        **Binance:**
        - BTCUSDT, ETHUSDT, ADAUSDT, SOLUSDT
        
        **Stooq:**
        - AAPL.US, MSFT.US, GOOGL.US
        """)
    
    with st.sidebar.expander("⚙️ Configuraciones"):
        st.markdown("""
        **Para análisis diario:**
        - Intervalo: 1d
        - Rango: 2 años
        
        **Para análisis intradía:**
        - Intervalo: 1h
        - Rango: 30 días
        """)
    
    with st.sidebar.expander("🔧 Solución de Problemas"):
        st.markdown("""
        **Error de símbolo:**
        - Verifica que existe en la fuente
        - Usa formato correcto
        
        **Error de conexión:**
        - Verifica Internet
        - Cambia de fuente
        
        **App lenta:**
        - Reduce rango de fechas
        - Usa menos símbolos
        """)


def validate_symbols(symbols: str, source: str) -> tuple[bool, str]:
    """
    Valida que los símbolos sean apropiados para la fuente.
    
    Args:
        symbols: Cadena de símbolos separados por comas
        source: Fuente de datos
        
    Returns:
        Tupla (es_válido, mensaje)
    """
    if not symbols.strip():
        return False, "Por favor ingresa al menos un símbolo"
    
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    
    if not symbol_list:
        return False, "No se encontraron símbolos válidos"
    
    # Validaciones específicas por fuente
    if source == "binance":
        invalid_symbols = [s for s in symbol_list if not s.endswith("USDT")]
        if invalid_symbols:
            return False, f"Símbolos de Binance deben terminar en 'USDT': {', '.join(invalid_symbols)}"
    
    elif source == "stooq":
        invalid_symbols = [s for s in symbol_list if not s.endswith(".US")]
        if invalid_symbols:
            return False, f"Símbolos de Stooq deben terminar en '.US': {', '.join(invalid_symbols)}"
    
    return True, "Símbolos válidos"


def show_error_summary():
    """Muestra un resumen de errores comunes y sus soluciones."""
    st.markdown("### 🚨 Errores Comunes y Soluciones")
    
    error_solutions = {
        "SymbolNotFound": {
            "desc": "Símbolo no encontrado",
            "sol": "Verifica que el símbolo existe en la fuente seleccionada",
            "ejemplo": "AAPL para Yahoo, BTCUSDT para Binance"
        },
        "ExtractionError": {
            "desc": "Error de extracción de datos", 
            "sol": "Cambia de fuente o verifica tu conexión",
            "ejemplo": "Usa Yahoo Finance en lugar de Stooq"
        },
        "ConnectionError": {
            "desc": "Error de conexión",
            "sol": "Verifica tu conexión a Internet",
            "ejemplo": "Reintenta en unos minutos"
        }
    }
    
    for error_type, info in error_solutions.items():
        with st.expander(f"❌ {error_type}: {info['desc']}"):
            st.markdown(f"**Solución**: {info['sol']}")
            st.markdown(f"**Ejemplo**: {info['ejemplo']}")


def create_error_recovery_button():
    """Crea un botón para recuperarse de errores."""
    if st.button("🔄 Reintentar Análisis", help="Reintenta el análisis con la misma configuración"):
        st.rerun()
    
    if st.button("🧹 Limpiar Datos", help="Limpia los datos en caché y reinicia"):
        # Limpiar session state
        keys_to_clear = [key for key in st.session_state.keys() if key.startswith("data_")]
        for key in keys_to_clear:
            del st.session_state[key]
        st.rerun()
