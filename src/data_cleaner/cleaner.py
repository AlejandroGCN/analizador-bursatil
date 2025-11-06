# -*- coding: utf-8 -*-
"""
Módulo de limpieza y validación de datos financieros.
"""
import pandas as pd


class DataCleaner:
    """
    Clase para limpiar y validar DataFrames de series temporales financieras.
    
    Proporciona métodos para detectar y corregir problemas comunes en datos
    financieros históricos, como duplicados, ordenamiento incorrecto y valores faltantes.
    
    Example:
        >>> cleaner = DataCleaner()
        >>> df_limpio = cleaner.clean_dataframe(df_raw)
        >>> issues = cleaner.validate(df_limpio)
        >>> if not issues:
        ...     print("Datos validados correctamente")
    """
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia un DataFrame de series temporales aplicando correcciones estándar.
        
        Operaciones realizadas:
        - Elimina filas duplicadas
        - Ordena índice cronológicamente (si es necesario)
        - Rellena valores faltantes usando forward-fill y backward-fill
        
        Args:
            df: DataFrame con índice temporal a limpiar
        
        Returns:
            DataFrame limpio con duplicados eliminados, índice ordenado
            y valores faltantes rellenados
        
        Note:
            Solo realiza cambios si detecta problemas. Si el DataFrame
            ya está limpio, se devuelve sin modificaciones.
        """
        if (df.index.has_duplicates or 
            not df.index.is_monotonic_increasing or
            df.isna().any().any()):
            df = df.copy()
            df = df.drop_duplicates()
            if not df.index.is_monotonic_increasing:
                df = df.sort_index()
            df = df.ffill().bfill()
        
        return df
    
    def validate(self, df: pd.DataFrame) -> list[str]:
        """
        Valida la calidad de un DataFrame de series temporales.
        
        Detecta problemas comunes que pueden afectar análisis posteriores:
        - Valores faltantes (NaN)
        - Fechas desordenadas (índice no monotónico)
        
        Args:
            df: DataFrame a validar
        
        Returns:
            Lista de strings describiendo los problemas encontrados.
            Lista vacía si el DataFrame está correcto.
        
        Example:
            >>> issues = cleaner.validate(df)
            >>> if issues:
            ...     print(f"Problemas encontrados: {', '.join(issues)}")
        """
        issues = []
        if df.isna().any().any():
            issues.append("Valores faltantes")
        if not df.index.is_monotonic_increasing:
            issues.append("Fechas desordenadas")
        return issues
