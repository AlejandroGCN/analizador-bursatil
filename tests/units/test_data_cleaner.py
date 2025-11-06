# -*- coding: utf-8 -*-
"""Tests unitarios para DataCleaner."""
import pytest
import pandas as pd
import numpy as np
from data_cleaner.cleaner import DataCleaner


class TestDataCleaner:
    """Tests para la clase DataCleaner."""
    
    @pytest.fixture
    def cleaner(self):
        """Fixture con instancia de DataCleaner."""
        return DataCleaner()
    
    def test_clean_dataframe_already_clean(self, cleaner):
        """Test que DataFrame limpio no se modifica."""
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        }, index=dates)
        
        result = cleaner.clean_dataframe(df)
        
        # Deberia devolver el mismo DataFrame
        pd.testing.assert_frame_equal(result, df)
    
    def test_clean_dataframe_with_duplicates(self, cleaner):
        """Test limpieza de duplicados."""
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104]
        }, index=dates)
        
        # Duplicar una fila
        df = pd.concat([df, df.iloc[[2]]])
        
        result = cleaner.clean_dataframe(df)
        
        # Duplicados eliminados
        assert not result.index.has_duplicates
        assert len(result) == 5
    
    def test_clean_dataframe_unsorted_index(self, cleaner):
        """Test ordenamiento de indice."""
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104]
        }, index=pd.to_datetime(['2023-01-05', '2023-01-01', '2023-01-03', 
                                  '2023-01-02', '2023-01-04']))
        
        result = cleaner.clean_dataframe(df)
        
        # Debe estar ordenado
        assert result.index.is_monotonic_increasing
        assert result.index[0] == pd.Timestamp('2023-01-01')
        assert result.index[-1] == pd.Timestamp('2023-01-05')
    
    def test_clean_dataframe_with_nan(self, cleaner):
        """Test relleno de valores NaN."""
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        df = pd.DataFrame({
            'close': [100, np.nan, 102, np.nan, 104]
        }, index=dates)
        
        result = cleaner.clean_dataframe(df)
        
        # NaNs rellenados
        assert not result.isna().any().any()
        # Forward fill: NaN en posicion 1 se llena con 100
        assert result.iloc[1, 0] == 100
    
    def test_clean_dataframe_combined_issues(self, cleaner):
        """Test con multiples problemas: duplicados, desorden, NaN."""
        df = pd.DataFrame({
            'close': [100, 101, np.nan, 103]
        }, index=pd.to_datetime(['2023-01-03', '2023-01-01', '2023-01-04', '2023-01-02']))
        
        result = cleaner.clean_dataframe(df)
        
        assert result.index.is_monotonic_increasing
        assert not result.isna().any().any()
        assert len(result) == 4
    
    def test_validate_clean_data(self, cleaner):
        """Test validacion de datos limpios."""
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        df = pd.DataFrame({
            'close': range(100, 110)
        }, index=dates)
        
        issues = cleaner.validate(df)
        
        assert issues == []  # Sin problemas
    
    def test_validate_with_nan(self, cleaner):
        """Test validacion detecta NaN."""
        df = pd.DataFrame({
            'close': [100, np.nan, 102]
        })
        
        issues = cleaner.validate(df)
        
        assert 'Valores faltantes' in issues
    
    def test_validate_with_unsorted_dates(self, cleaner):
        """Test validacion detecta fechas desordenadas."""
        df = pd.DataFrame({
            'close': [100, 101, 102]
        }, index=pd.to_datetime(['2023-01-03', '2023-01-01', '2023-01-02']))
        
        issues = cleaner.validate(df)
        
        assert 'Fechas desordenadas' in issues
    
    def test_validate_multiple_issues(self, cleaner):
        """Test validacion detecta multiples problemas."""
        df = pd.DataFrame({
            'close': [100, np.nan, 102]
        }, index=pd.to_datetime(['2023-01-03', '2023-01-01', '2023-01-02']))
        
        issues = cleaner.validate(df)
        
        assert len(issues) == 2
        assert 'Valores faltantes' in issues
        assert 'Fechas desordenadas' in issues
