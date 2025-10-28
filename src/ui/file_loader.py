"""
Módulo para cargar símbolos desde archivos
"""

import pandas as pd
import json
from typing import List, Optional
from pathlib import Path


def load_symbols_from_file(uploaded_file) -> Optional[List[str]]:
    """
    Extrae símbolos de un archivo subido.
    
    Args:
        uploaded_file: Archivo subido por el usuario
        
    Returns:
        Lista de símbolos extraídos o None si hay error
    """
    if uploaded_file is None:
        return None
    
    try:
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        if file_extension == '.csv':
            symbols = _load_from_csv(uploaded_file)
        elif file_extension in ['.xlsx', '.xls']:
            symbols = _load_from_excel(uploaded_file)
        elif file_extension == '.json':
            symbols = _load_from_json(uploaded_file)
        elif file_extension == '.txt':
            symbols = _load_from_txt(uploaded_file)
        else:
            return None
        
        return symbols
            
    except Exception:
        return None


def _load_from_csv(uploaded_file) -> List[str]:
    """Carga símbolos desde un archivo CSV."""
    df = pd.read_csv(uploaded_file)
    
    # Buscar columnas que puedan contener símbolos
    symbol_columns = ['symbol', 'ticker', 'symbols', 'tickers', 'stock', 'stocks']
    
    for col in symbol_columns:
        if col.lower() in [c.lower() for c in df.columns]:
            symbols = df[col].dropna().astype(str).tolist()
            return _sanitize_symbols([s.strip() for s in symbols if s.strip()])
    
    # Si no encuentra columnas específicas, usar la primera columna
    if len(df.columns) > 0:
        symbols = df.iloc[:, 0].dropna().astype(str).tolist()
        return _sanitize_symbols([s.strip() for s in symbols if s.strip()])
    
    return []


def _load_from_excel(uploaded_file) -> List[str]:
    """Carga símbolos desde un archivo Excel."""
    df = pd.read_excel(uploaded_file)
    
    # Buscar columnas que puedan contener símbolos
    symbol_columns = ['symbol', 'ticker', 'symbols', 'tickers', 'stock', 'stocks']
    
    for col in symbol_columns:
        if col.lower() in [c.lower() for c in df.columns]:
            symbols = df[col].dropna().astype(str).tolist()
            return _sanitize_symbols([s.strip() for s in symbols if s.strip()])
    
    # Si no encuentra columnas específicas, usar la primera columna
    if len(df.columns) > 0:
        symbols = df.iloc[:, 0].dropna().astype(str).tolist()
        return _sanitize_symbols([s.strip() for s in symbols if s.strip()])
    
    return []


def _load_from_json(uploaded_file) -> List[str]:
    """Carga símbolos desde un archivo JSON."""
    content = uploaded_file.read().decode('utf-8')
    data = json.loads(content)
    
    # Si es una lista simple
    if isinstance(data, list):
        return _sanitize_symbols([str(item).strip() for item in data if str(item).strip()])
    
    # Si es un objeto con claves específicas
    if isinstance(data, dict):
        symbol_keys = ['symbols', 'tickers', 'stocks', 'symbol', 'ticker']
        
        for key in symbol_keys:
            if key in data:
                symbols = data[key]
                if isinstance(symbols, list):
                    return _sanitize_symbols([str(item).strip() for item in symbols if str(item).strip()])
                elif isinstance(symbols, str):
                    return _sanitize_symbols([s.strip() for s in symbols.split(',') if s.strip()])
    
    return []


def _load_from_txt(uploaded_file) -> List[str]:
    """Carga símbolos desde un archivo de texto."""
    content = uploaded_file.read().decode('utf-8')
    lines = content.strip().split('\n')
    
    symbols = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):  # Ignorar líneas vacías y comentarios
            # Si la línea contiene comas, dividir por comas
            if ',' in line:
                symbols.extend([s.strip() for s in line.split(',') if s.strip()])
            else:
                symbols.append(line)
    
    return _sanitize_symbols(symbols)


def _sanitize_symbols(symbols: List[str]) -> List[str]:
    """
    Sanitiza una lista de símbolos eliminando caracteres inválidos y duplicados.
    
    Args:
        symbols: Lista de símbolos a sanitizar
        
    Returns:
        Lista de símbolos sanitizados
    """
    import re
    
    sanitized = []
    
    for symbol in symbols:
        # Remover caracteres no alfanuméricos (excepto puntos, guiones y barras)
        cleaned = re.sub(r'[^A-Z0-9.\-/]', '', symbol.upper())
        
        # Solo agregar si tiene al menos una letra y no es demasiado largo
        if cleaned and len(cleaned) <= 20 and any(c.isalpha() for c in cleaned):
            sanitized.append(cleaned)
    
    # Eliminar duplicados preservando orden
    seen = set()
    unique = []
    for symbol in sanitized:
        if symbol not in seen:
            seen.add(symbol)
            unique.append(symbol)
    
    return unique