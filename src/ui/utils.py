"""Utilidades compartidas para las vistas."""
import streamlit as st


def initialize_symbols() -> None:
    """
    Inicializa las variables de símbolos SOLO si no existen.
    IMPORTANTE: Si ya existen, NO los modifica.
    
    Esta función debe llamarse una vez al inicio de la app para asegurar
    que las keys necesarias existan en session_state.
    """
    if "datos_simbolos" not in st.session_state:
        st.session_state.datos_simbolos = ""
    if "cartera_symbols" not in st.session_state:
        st.session_state.cartera_symbols = ""
    if "cartera_weights" not in st.session_state:
        st.session_state.cartera_weights = ""


def display_symbol_info(session_state_key: str, contexto: str = "") -> None:
    """
    Muestra información de símbolos configurados (read-only).
    Usado en las views de datos y cartera.
    
    Args:
        session_state_key: Key donde están los símbolos
        contexto: Contexto adicional (ej: "cartera", "datos")
    """
    simbolos_actuales = st.session_state.get(session_state_key, "")
    
    # Solo mostrar mensaje si NO hay símbolos configurados
    if not (simbolos_actuales and simbolos_actuales.strip()):
        if contexto == "datos":
            st.info("""
            💡 **Configura los símbolos para obtener datos**
            
            **Opciones:**
            1. Escribe los símbolos en el panel lateral (separados por comas)
            2. Importa símbolos desde la pestaña de Cartera
            3. Carga un archivo con los símbolos
            
            **Ejemplo:** `AAPL, MSFT, GOOGL`
            
            **Una vez configurados los símbolos:**
            - Configura los parámetros en el panel lateral (fecha, intervalo, tipo)
            - Pulsa el botón **"📥 Obtener datos"** (haz scroll hacia abajo en el panel lateral si es necesario)
            """)
        elif contexto == "cartera":
            st.info("""
            💡 **Configura los símbolos para analizar tu cartera**
            
            **Opciones:**
            1. Escribe los símbolos en el panel lateral (separados por comas)
            2. Importa símbolos desde la pestaña de Datos
            3. Carga un archivo con los símbolos
            
            **Ejemplo:** `AAPL, MSFT, GOOGL`
            
            **Una vez configurados los símbolos:**
            - Ajusta el valor inicial de la cartera y los pesos de cada activo
            - Pulsa el botón **"💼 Aplicar pesos"** para ver la distribución de tu cartera
            """)
        else:
            st.info("💡 **Configura los símbolos en el panel lateral para comenzar**")


def validate_and_clean_symbols(symbols_str: str) -> tuple[list[str], list[str]]:
    """
    Valida y limpia una cadena de símbolos, separándolos correctamente.
    
    Returns:
        (valid_symbols, invalid_symbols): Tupla con símbolos válidos e inválidos
    """
    if not symbols_str or not symbols_str.strip():
        return [], []
    
    # Limpiar la entrada: remover espacios extra y normalizar
    symbols_str = symbols_str.strip()
    
    # Intentar separar por comas primero
    potential_symbols = [s.strip() for s in symbols_str.replace(" ", ",").split(",") if s.strip()]
    
    valid_symbols = []
    invalid_symbols = []
    
    for symbol in potential_symbols:
        # Validaciones básicas
        is_valid = True
        reasons = []
        
        # 1. No debe tener múltiples puntos consecutivos o mal posicionados
        if symbol.count('.') > 1:
            is_valid = False
            reasons.append("demasiados puntos")
        elif '.' in symbol and not symbol.endswith(('.US', '.DE', '.FR', '.UK', '.JP', '.CA', '.AU', '.CN')):
            # Si tiene punto, debe ser una extensión conocida
            is_valid = False
            reasons.append("extensión desconocida")
        
        # 2. Longitud mínima y máxima
        if len(symbol) < 1 or len(symbol) > 15:
            is_valid = False
            reasons.append("longitud inválida")
        
        # 3. Solo letras, números, puntos y guiones
        if not all(c.isalnum() or c in '.-' for c in symbol):
            is_valid = False
            reasons.append("caracteres no permitidos")
        
        # 4. Debe empezar con letra
        if not symbol[0].isalpha():
            is_valid = False
            reasons.append("debe empezar con letra")
        
        if is_valid:
            valid_symbols.append(symbol)
        else:
            invalid_symbols.append(f"{symbol} ({', '.join(reasons)})")
    
    return valid_symbols, invalid_symbols
