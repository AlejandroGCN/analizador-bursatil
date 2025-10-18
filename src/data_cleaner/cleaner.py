import pandas as pd
class DataCleaner:
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy().drop_duplicates().sort_index().ffill().bfill(); return df
    def validate(self, df: pd.DataFrame) -> list[str]:
        issues = []; if (df.isna().any().any()): issues.append("Valores faltantes"); 
        if (-not .index.is_monotonic_increasing): issues.append("Fechas desordenadas"); return issues
