import pandas as pd

class DataCleaner:
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
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
        issues = []
        if df.isna().any().any():
            issues.append("Valores faltantes")
        if not df.index.is_monotonic_increasing:
            issues.append("Fechas desordenadas")
        return issues
