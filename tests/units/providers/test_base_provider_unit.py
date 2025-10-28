# tests/units/providers/test_base_provider_unit.py
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from data_extractor.core.base.base_provider import BaseProvider
from data_extractor.series.price_series import PriceSeries
from data_extractor.adapters.yahoo_adapter import YahooAdapter
from data_extractor.adapters.binance_adapter import BinanceAdapter


class TestBaseProviderUnit:
    """Tests unitarios para BaseProvider usando mocks."""
    
    def test_provider_initialization(self):
        """Test que BaseProvider se inicializa correctamente."""
        mock_adapter = MagicMock()
        provider = BaseProvider(source_name="test_source", adapter=mock_adapter)
        
        assert provider.source_name == "test_source"
        assert provider.adapter == mock_adapter
    
    def test_provider_get_symbols_single(self):
        """Test que BaseProvider maneja un solo símbolo correctamente."""
        # Mock adapter que devuelve datos simulados
        mock_adapter = MagicMock()
        mock_data = pd.DataFrame({
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.5],
            "Close": [101.0, 102.0],
            "Adj Close": [101.0, 102.0],
            "Volume": [1000, 1100],
        }, index=pd.to_datetime(["2024-01-01", "2024-01-02"]))
        
        mock_adapter.get_symbols.return_value = {"AAPL": mock_data}
        
        provider = BaseProvider(source_name="test", adapter=mock_adapter)
        result = provider.get_symbols(["AAPL"], start="2024-01-01", end="2024-01-02", interval="1d")
        
        assert "AAPL" in result
        assert isinstance(result["AAPL"], PriceSeries)  # Verificar que es PriceSeries
        assert result["AAPL"].symbol == "AAPL"
        assert not result["AAPL"].data.empty
    
    def test_provider_get_symbols_multiple(self):
        """Test que BaseProvider maneja múltiples símbolos correctamente."""
        mock_adapter = MagicMock()
        
        # Datos simulados para múltiples símbolos
        mock_data_aapl = pd.DataFrame({
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.5],
            "Close": [101.0, 102.0],
            "Adj Close": [101.0, 102.0],
            "Volume": [1000, 1100],
        }, index=pd.to_datetime(["2024-01-01", "2024-01-02"]))
        
        mock_data_msft = pd.DataFrame({
            "Open": [200.0, 201.0],
            "High": [202.0, 203.0],
            "Low": [199.0, 200.5],
            "Close": [201.0, 202.0],
            "Adj Close": [201.0, 202.0],
            "Volume": [2000, 2100],
        }, index=pd.to_datetime(["2024-01-01", "2024-01-02"]))
        
        mock_adapter.get_symbols.return_value = {
            "AAPL": mock_data_aapl,
            "MSFT": mock_data_msft
        }
        
        provider = BaseProvider(source_name="test", adapter=mock_adapter)
        result = provider.get_symbols(["AAPL", "MSFT"], start="2024-01-01", end="2024-01-02", interval="1d")
        
        assert len(result) == 2
        assert "AAPL" in result
        assert "MSFT" in result
        assert isinstance(result["AAPL"], PriceSeries)
        assert isinstance(result["MSFT"], PriceSeries)
        assert result["AAPL"].symbol == "AAPL"
        assert result["MSFT"].symbol == "MSFT"
    
    def test_provider_with_yahoo_adapter_mock(self):
        """Test BaseProvider con YahooAdapter usando mocks."""
        # Mock de YahooAdapter
        mock_yahoo_adapter = MagicMock()
        mock_data = pd.DataFrame({
            "Open": [150.0, 151.0],
            "High": [152.0, 153.0],
            "Low": [149.0, 150.5],
            "Close": [151.0, 152.0],
            "Adj Close": [151.0, 152.0],
            "Volume": [1500, 1600],
        }, index=pd.to_datetime(["2024-01-01", "2024-01-02"]))
        
        mock_yahoo_adapter.get_symbols.return_value = {"GOOGL": mock_data}
        
        provider = BaseProvider(source_name="yahoo", adapter=mock_yahoo_adapter)
        result = provider.get_symbols(["GOOGL"], start="2024-01-01", end="2024-01-02", interval="1d")
        
        assert "GOOGL" in result
        assert isinstance(result["GOOGL"], PriceSeries)
        assert result["GOOGL"].symbol == "GOOGL"
        assert result["GOOGL"].data["close"].iloc[0] == pytest.approx(151.0)
        assert result["GOOGL"].data["volume"].iloc[1] == pytest.approx(1600)
    
    def test_provider_with_binance_adapter_mock(self):
        """Test BaseProvider con BinanceAdapter usando mocks."""
        # Mock de BinanceAdapter
        mock_binance_adapter = MagicMock()
        mock_data = pd.DataFrame({
            "Open": [50000.0, 51000.0],
            "High": [52000.0, 53000.0],
            "Low": [49000.0, 50000.0],
            "Close": [51000.0, 52000.0],
            "Adj Close": [51000.0, 52000.0],
            "Volume": [1.5, 1.8],
        }, index=pd.to_datetime(["2024-01-01", "2024-01-02"]))
        
        mock_binance_adapter.get_symbols.return_value = {"BTCUSDT": mock_data}
        
        provider = BaseProvider(source_name="binance", adapter=mock_binance_adapter)
        result = provider.get_symbols(["BTCUSDT"], start="2024-01-01", end="2024-01-02", interval="1h")
        
        assert "BTCUSDT" in result
        assert isinstance(result["BTCUSDT"], PriceSeries)
        assert result["BTCUSDT"].symbol == "BTCUSDT"
        assert result["BTCUSDT"].data["close"].iloc[0] == pytest.approx(51000.0)
        assert result["BTCUSDT"].data["volume"].iloc[1] == pytest.approx(1.8)
    
    def test_provider_error_handling(self):
        """Test que BaseProvider maneja errores correctamente."""
        mock_adapter = MagicMock()
        mock_adapter.get_symbols.side_effect = Exception("API Error")
        
        provider = BaseProvider(source_name="test", adapter=mock_adapter)
        
        with pytest.raises(Exception):
            provider.get_symbols(["AAPL"], start="2024-01-01", end="2024-01-02", interval="1d")
    
    def test_provider_empty_result(self):
        """Test que BaseProvider maneja resultados vacíos correctamente."""
        mock_adapter = MagicMock()
        mock_adapter.get_symbols.return_value = {}
        
        provider = BaseProvider(source_name="test", adapter=mock_adapter)
        result = provider.get_symbols(["INVALID"], start="2024-01-01", end="2024-01-02", interval="1d")
        
        assert result == {}  # Resultado vacío cuando no hay datos
    
    def test_provider_with_align_parameters(self):
        """Test que BaseProvider pasa parámetros de alineación correctamente."""
        mock_adapter = MagicMock()
        mock_data = pd.DataFrame({
            "Open": [100.0],
            "High": [102.0],
            "Low": [99.0],
            "Close": [101.0],
            "Adj Close": [101.0],
            "Volume": [1000],
        }, index=pd.to_datetime(["2024-01-01"]))
        
        mock_adapter.get_symbols.return_value = {"AAPL": mock_data}
        
        provider = BaseProvider(source_name="test", adapter=mock_adapter)
        
        # Test con align="union"
        result1 = provider.get_symbols(["AAPL"], start="2024-01-01", end="2024-01-02", interval="1d", align="union")
        
        # Test con align="intersect"
        result2 = provider.get_symbols(["AAPL"], start="2024-01-01", end="2024-01-02", interval="1d", align="intersect")
        
        # Verificar que se llamó 2 veces
        assert mock_adapter.get_symbols.call_count == 2
        
        # Verificar que los resultados son PriceSeries
        assert isinstance(result1["AAPL"], PriceSeries)
        assert isinstance(result2["AAPL"], PriceSeries)
        assert result1["AAPL"].symbol == "AAPL"
        assert result2["AAPL"].symbol == "AAPL"
