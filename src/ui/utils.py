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
    
    # Inicializar valores guardados si no existen
    if "saved_datos_simbolos" not in st.session_state:
        st.session_state.saved_datos_simbolos = ""
    if "saved_cartera_symbols" not in st.session_state:
        st.session_state.saved_cartera_symbols = ""
    if "saved_cartera_weights" not in st.session_state:
        st.session_state.saved_cartera_weights = ""


def apply_sidebar_styles() -> None:
    """
    Aplica estilos CSS al sidebar.
    Esta función centraliza el CSS para evitar duplicación.
    """
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #d4e4f7;
    }
    [data-testid="stSidebar"] > div {
        background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)


def render_symbol_import_controls(source_key: str, target_key: str, from_label: str, button_label: str) -> None:
    """
    Renderiza los controles para importar símbolos desde otra pestaña.
    
    Args:
        source_key: Key en session_state de donde importar (ej: "cartera_symbols")
        target_key: Key en session_state donde guardar (ej: "datos_simbolos")
        from_label: Nombre de la pestaña origen (ej: "Cartera")
        button_label: Texto del botón (ej: "💼 Importar símbolos desde Cartera")
    """
    btn_import = st.sidebar.button(button_label, key=f"btn_import_{target_key}", width='stretch')
    
    if btn_import:
        source_symbols = st.session_state.get(source_key, "")
        if source_symbols and source_symbols.strip():
            st.session_state[target_key] = source_symbols
            st.success(f"✅ Símbolos importados desde {from_label}")
        else:
            st.warning(f"⚠️ No hay símbolos en {from_label}")


def render_file_upload_controls(target_key: str, button_label: str, uploader_key: str) -> None:
    """
    Renderiza los controles para cargar símbolos desde archivo.
    
    Args:
        target_key: Key en session_state donde guardar los símbolos
        button_label: Texto del botón de carga
        uploader_key: Key única para el file_uploader
    """
    # Sección de carga de archivos
    uploaded_file = st.sidebar.file_uploader(
        "Selecciona un archivo",
        type=['csv', 'xlsx', 'xls', 'json', 'txt'],
        help="Formatos: CSV, Excel, JSON, TXT",
        key=uploader_key
    )
    
    btn_load = st.sidebar.button(button_label, key=f"btn_load_{uploader_key}", width='stretch')
    
    if btn_load and uploaded_file is not None:
        try:
            from ui.file_loader import load_symbols_from_file
            symbols = load_symbols_from_file(uploaded_file)
            if symbols:
                st.session_state[target_key] = ",".join(symbols)
                st.success(f"✅ {len(symbols)} símbolos cargados")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    elif btn_load:
        st.warning("⚠️ Primero selecciona un archivo")


def render_symbol_input(key: str, label: str = "📝 Símbolos:") -> None:
    """
    Renderiza un input de texto para símbolos.
    
    Args:
        key: Key único para el widget en session_state
        label: Etiqueta del input
    """
    st.text_input(
        label,
        key=key,
        placeholder="Ej: AAPL, MSFT, GOOGL",
        help="Escribe los símbolos separados por coma (ej: AAPL, MSFT, GOOGL)",
        label_visibility="visible"
    )


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
