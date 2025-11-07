"""Utilidades compartidas para las vistas."""
import streamlit as st
from typing import List, Dict, Tuple, Optional


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


def normalize_symbol(symbol: str) -> str:
    """
    Normaliza un símbolo para comparación case-insensitive.
    
    Función compartida para evitar duplicación de código en diferentes vistas.
    Convierte el símbolo a mayúsculas y elimina espacios en blanco.
    
    Args:
        symbol: Símbolo a normalizar
    
    Returns:
        Símbolo en mayúsculas y sin espacios
    """
    return str(symbol).strip().upper()


def create_normalized_symbol_dicts(
    available_symbols: List[str], 
    portfolio_symbols: List[str]
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Crea diccionarios de símbolos normalizados para comparación.
    
    Utilidad compartida para mapear símbolos normalizados a sus versiones
    originales, facilitando comparaciones case-insensitive entre cartera
    y datos disponibles.
    
    Args:
        available_symbols: Lista de símbolos disponibles en los datos
        portfolio_symbols: Lista de símbolos de la cartera
    
    Returns:
        Tuple con (diccionario símbolos disponibles, diccionario símbolos cartera)
    """
    available_symbols_dict = {normalize_symbol(k): k for k in available_symbols}
    portfolio_symbols_dict = {normalize_symbol(s): s for s in portfolio_symbols}
    return available_symbols_dict, portfolio_symbols_dict


def get_symbols_mapped_to_data_format(
    portfolio_symbols: List[str],
    available_symbols_dict: Dict[str, str]
) -> List[str]:
    """
    Obtiene símbolos de cartera mapeados al formato de los datos.
    
    Mapea los símbolos de la cartera a sus equivalentes en el formato
    de los datos descargados, usando normalización case-insensitive.
    
    Args:
        portfolio_symbols: Lista de símbolos de la cartera
        available_symbols_dict: Diccionario símbolo normalizado -> símbolo original en datos
    
    Returns:
        Lista de símbolos en formato de los datos
    """
    return [
        available_symbols_dict[normalize_symbol(s)] 
        for s in portfolio_symbols 
        if normalize_symbol(s) in available_symbols_dict
    ]


def render_symbol_import_controls(source_key: str, target_key: str, from_label: str, button_label: str) -> None:
    """
    Renderiza los controles para importar símbolos desde otra pestaña.
    
    Args:
        source_key: Key en session_state donde están los símbolos fuente
        target_key: Key en session_state donde se guardarán los símbolos
        from_label: Etiqueta descriptiva de la fuente (ej: "Cartera")
        button_label: Texto del botón
    """
    if source_key in st.session_state and st.session_state[source_key]:
        if st.sidebar.button(button_label, key=f"import_{target_key}"):
            st.session_state[target_key] = st.session_state[source_key]
            st.sidebar.success(f"✅ Símbolos importados desde {from_label}")
            st.rerun()


def render_file_upload_controls(target_key: str, button_label: str, uploader_key: str) -> None:
    """
    Renderiza los controles para cargar símbolos desde archivo.
    
    Soporta múltiples formatos: TXT, CSV, Excel (.xlsx, .xls), JSON
    
    Args:
        target_key: Key en session_state donde se guardarán los símbolos
        button_label: Texto del botón
        uploader_key: Key único para el widget de carga
    """
    from ui.file_loader import load_symbols_from_file
    
    # Key para rastrear el último archivo procesado
    last_processed_key = f"{uploader_key}_last_processed"
    
    uploaded_file = st.sidebar.file_uploader(
        button_label, 
        type=['txt', 'csv', 'xlsx', 'xls', 'json'], 
        key=uploader_key,
        help="Carga un archivo con símbolos. Formatos soportados: TXT, CSV, Excel, JSON"
    )
    
    # Solo procesar si hay un archivo nuevo (no el mismo que ya procesamos)
    if uploaded_file is not None:
        # Verificar si es un archivo nuevo
        current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        last_processed = st.session_state.get(last_processed_key, None)
        
        if current_file_id != last_processed:
            symbols = load_symbols_from_file(uploaded_file)
            
            if symbols:
                # Convertir lista de símbolos a string separado por comas
                symbols_str = ", ".join(symbols)
                
                # Actualizar session_state - esto actualizará automáticamente el widget text_input
                st.session_state[target_key] = symbols_str
                st.session_state[last_processed_key] = current_file_id
                
                # Mensajes de confirmación (más breve para no saturar)
                st.sidebar.success(f"✅ Archivo cargado: {len(symbols)} símbolo(s)")
                
                # Forzar rerun inmediato para que el widget se actualice
                st.rerun()
            else:
                st.sidebar.error("❌ No se pudieron extraer símbolos del archivo. Verifica el formato.")
                st.session_state[last_processed_key] = current_file_id  # Marcar como procesado aunque falle


def validate_and_clean_symbols(symbols_text: str) -> tuple[List[str], List[str]]:
    """
    Valida y limpia una cadena de símbolos.
    
    Args:
        symbols_text: Texto con símbolos separados por coma
    
    Returns:
        Tupla con (símbolos válidos, símbolos inválidos)
        Los símbolos válidos están limpios (sin espacios, sin duplicados)
    """
    if not symbols_text or not symbols_text.strip():
        return [], []
    
    # Dividir por comas y procesar cada símbolo
    raw_symbols = [s.strip() for s in symbols_text.split(',') if s.strip()]
    
    valid_symbols = []
    invalid_symbols = []
    seen_valid = set()
    seen_invalid = set()
    
    for raw_symbol in raw_symbols:
        # Limpiar y convertir a mayúsculas
        cleaned = raw_symbol.upper()
        
        # Validar: debe contener solo letras y números, mínimo 1 carácter
        if cleaned and cleaned.isalnum() and len(cleaned) >= 1:
            # Evitar duplicados en válidos
            if cleaned not in seen_valid:
                valid_symbols.append(cleaned)
                seen_valid.add(cleaned)
        else:
            # Símbolo inválido
            if cleaned not in seen_invalid:
                invalid_symbols.append(raw_symbol)
                seen_invalid.add(cleaned)
    
    return valid_symbols, invalid_symbols


def render_symbol_input(key: str) -> None:
    """
    Renderiza un widget de entrada de texto para símbolos.
    
    Args:
        key: Key única para el widget en session_state
    """
    # Usar text_input en lugar de text_area para que sea una línea única y compacta
    # Si la key ya existe en session_state, no pasar 'value' para evitar conflictos
    # Streamlit manejará automáticamente el valor cuando usas key=key
    if key in st.session_state:
        st.text_input(
            "Símbolos (separados por comas)",
            key=key,
            help="Introduce los símbolos separados por comas. Ejemplo: AAPL, MSFT, GOOGL"
        )
    else:
        # Solo pasar value cuando la key no existe (primera vez)
        st.text_input(
            "Símbolos (separados por comas)",
            value="",
            key=key,
            help="Introduce los símbolos separados por comas. Ejemplo: AAPL, MSFT, GOOGL"
        )


def display_symbol_info(contexto: str = "datos") -> None:
    """
    Muestra información y ayuda sobre cómo introducir símbolos.
    
    Args:
        contexto: Contexto en el que se muestra (datos, cartera, etc.)
    """
    if contexto == "datos":
        st.info("""
        **💡 Ayuda:** Introduce los símbolos de los activos que deseas analizar.
        
        **📝 Formas de introducir símbolos:**
        - **Manual**: Escribe en el campo de texto arriba, separados por comas (ej: `AAPL, MSFT, GOOGL`)
        - **Desde archivo**: Usa el botón "📂 Cargar desde archivo" en el panel lateral (TXT, CSV, JSON)
        
        **📥 Para obtener los datos (dos opciones):**
        
        **Opción A - Descarga rápida:** Escribe símbolos → Pulsa **Enter**
        
        **Opción B - Con parámetros:** Ajusta fechas/intervalo en el sidebar → Pulsa **'📥 Obtener datos'**
        
        **Ejemplos válidos:**
        - Yahoo Finance: `AAPL, MSFT, GOOGL, TSLA`
        - Binance: `BTCUSDT, ETHUSDT, BNBBTC`
        - Tiingo: `AAPL, MSFT, GOOGL, BP` (requiere API key gratuita)
        
        **Consejos:**
        - Verifica que los símbolos sean válidos para la fuente seleccionada
        - Los símbolos de acciones de EE.UU. en Yahoo no requieren sufijo
        - Para acciones internacionales en Yahoo, añade el sufijo del país (ej: `.DE`, `.FR`)
        """)
    elif contexto == "cartera":
        st.info("""
        **💡 Ayuda:** Construye tu cartera asignando pesos a cada activo.
        
        **📝 Formas de introducir símbolos:**
        - **Manual**: Escribe en el campo de texto arriba, separados por comas (ej: `AAPL, MSFT, GOOGL, TSLA`)
        - **Importar**: Usa el botón **"📥 Importar desde Datos"** en el panel lateral
        - **Desde archivo**: Usa el botón "📂 Cargar desde archivo" en el panel lateral (TXT, CSV, JSON)
        
        **📝 Para construir tu cartera (dos opciones):**
        
        **Opción A - Pesos iguales rápidos:** Escribe símbolos → Pulsa **Enter**
        
        **Opción B - Pesos personalizados:**
        1. Escribe símbolos en el campo de texto
        2. Ajusta pesos en el **panel lateral** (deben sumar 100%)
        3. Define valor inicial (ej: $10,000)
        4. Pulsa **'💼 Aplicar Pesos'**
        
        **⚠️ Importante:**
        - Los símbolos deben existir en los datos descargados (pestaña **📊 Datos**)
        - Los pesos **deben sumar exactamente 100%** (tolerancia: ±1%)
        - Si la suma es diferente, verás un error y deberás ajustarlos manualmente
        """)
