import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from data_extractor.adapters.stooq_adapter import StooqAdapter, _PDR_OK
from data_extractor.core.errors import ExtractionError, SymbolNotFound

# Mock _PDR_OK to be True for testing purposes
@pytest.fixture(autouse=True)
def mock_pdr_ok():
    with patch('data_extractor.adapters.stooq_adapter._PDR_OK', True):
        yield

class TestStooqAdapterUnit:
    """Tests unitarios para StooqAdapter usando mocks."""
    
    def test_stooq_ok_builds_dataframe(self):
        """Test que StooqAdapter construye DataFrame correctamente con mock."""
        # Mock de pandas_datareader
        mock_data = pd.DataFrame({
            "Close": [10.5, 11.0, 11.2],
            "Open": [10.0, 10.6, 11.1],
            "High": [11.0, 11.2, 11.5],
            "Low": [9.8, 10.2, 10.8],
            "Volume": [100, 120, 110],
        }, index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]))
        
        # Mock del módulo pdr y su función DataReader
        mock_pdr = MagicMock()
        mock_pdr.DataReader.return_value = mock_data
        
        with patch('data_extractor.adapters.stooq_adapter.pdr', mock_pdr):
            adapter = StooqAdapter()
            result = adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
            
            # Verificar estructura del DataFrame
            assert list(result.columns) == ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
            assert result.index.is_monotonic_increasing
            assert len(result) == 3
            
            # Verificar que se llamó al DataReader
            mock_pdr.DataReader.assert_called_once()
    
    def test_stooq_invalid_interval_raises(self):
        """Test que StooqAdapter lanza error con intervalo inválido."""
        adapter = StooqAdapter()
        
        with pytest.raises(ExtractionError):
            adapter.download_symbol("AAPL", start=None, end=None, interval="1h")
    
    def test_stooq_empty_raises(self):
        """Test que StooqAdapter lanza error cuando DataReader devuelve DataFrame vacío."""
        # Mock que devuelve DataFrame vacío
        empty_df = pd.DataFrame()
        
        mock_pdr = MagicMock()
        mock_pdr.DataReader.return_value = empty_df
        
        with patch('data_extractor.adapters.stooq_adapter.pdr', mock_pdr):
            adapter = StooqAdapter()
            
            with pytest.raises(SymbolNotFound):
                adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
    
    def test_stooq_with_different_column_order(self):
        """Test que StooqAdapter maneja diferentes órdenes de columnas."""
        # Mock con columnas en orden diferente
        mock_data = pd.DataFrame({
            "Volume": [100, 120],
            "Low": [9.8, 10.2],
            "High": [11.0, 11.2],
            "Open": [10.0, 10.6],
            "Close": [10.5, 11.0],
        }, index=pd.to_datetime(["2024-01-02", "2024-01-03"]))
        
        mock_pdr = MagicMock()
        mock_pdr.DataReader.return_value = mock_data
        
        with patch('data_extractor.adapters.stooq_adapter.pdr', mock_pdr):
            adapter = StooqAdapter()
            result = adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
            
            # Verificar que las columnas están en el orden correcto
            expected_columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
            assert list(result.columns) == expected_columns
            
            # Verificar que los datos son correctos (usar approx para floats)
            assert result["Close"].iloc[0] == pytest.approx(10.5)
            assert result["Volume"].iloc[1] == pytest.approx(120)
    
    def test_stooq_timeout_handling(self):
        """Test que StooqAdapter maneja timeouts correctamente."""
        adapter = StooqAdapter(timeout=5)
        
        # Mock que simula timeout
        mock_pdr = MagicMock()
        mock_pdr.DataReader.side_effect = Exception("Timeout")
        
        with patch('data_extractor.adapters.stooq_adapter.pdr', mock_pdr):
            with pytest.raises(Exception):
                adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
    
    def test_stooq_multiple_symbols(self):
        """Test que StooqAdapter puede manejar múltiples símbolos."""
        mock_data = pd.DataFrame({
            "Close": [10.5, 11.0],
            "Open": [10.0, 10.6],
            "High": [11.0, 11.2],
            "Low": [9.8, 10.2],
            "Volume": [100, 120],
        }, index=pd.to_datetime(["2024-01-02", "2024-01-03"]))
        
        mock_pdr = MagicMock()
        mock_pdr.DataReader.return_value = mock_data
        
        with patch('data_extractor.adapters.stooq_adapter.pdr', mock_pdr):
            adapter = StooqAdapter()
            
            # Test con símbolo que existe
            result = adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
            assert not result.empty
            
            # Test con símbolo que no existe (DataFrame vacío)
            mock_pdr.DataReader.return_value = pd.DataFrame()
            
            with pytest.raises(SymbolNotFound):
                adapter.download_symbol("INVALID", start="2024-01-01", end="2024-01-10", interval="1d")
