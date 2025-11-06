import pandas as pd
import pytest
from unittest.mock import patch, MagicMock, Mock
import requests

from data_extractor.adapters.tiingo_adapter import TiingoAdapter
from data_extractor.core.errors import ExtractionError


class TestTiingoAdapterUnit:
    """Tests unitarios para TiingoAdapter usando mocks."""
    
    @pytest.fixture
    def mock_api_key(self):
        """Fixture para proporcionar una API key de prueba."""
        return "test_api_key_12345"
    
    @pytest.fixture
    def mock_tiingo_response(self):
        """Fixture con respuesta típica de Tiingo API."""
        return [
            {
                "date": "2024-01-02T00:00:00.000Z",
                "close": 150.5,
                "high": 152.0,
                "low": 149.0,
                "open": 151.0,
                "volume": 1000000,
                "adjClose": 150.5,
                "adjHigh": 152.0,
                "adjLow": 149.0,
                "adjOpen": 151.0,
                "adjVolume": 1000000,
                "divCash": 0.0,
                "splitFactor": 1.0
            },
            {
                "date": "2024-01-03T00:00:00.000Z",
                "close": 151.0,
                "high": 152.5,
                "low": 150.0,
                "open": 150.5,
                "volume": 1100000,
                "adjClose": 151.0,
                "adjHigh": 152.5,
                "adjLow": 150.0,
                "adjOpen": 150.5,
                "adjVolume": 1100000,
                "divCash": 0.0,
                "splitFactor": 1.0
            },
            {
                "date": "2024-01-04T00:00:00.000Z",
                "close": 152.0,
                "high": 153.0,
                "low": 151.0,
                "open": 151.0,
                "volume": 1050000,
                "adjClose": 152.0,
                "adjHigh": 153.0,
                "adjLow": 151.0,
                "adjOpen": 151.0,
                "adjVolume": 1050000,
                "divCash": 0.0,
                "splitFactor": 1.0
            }
        ]
    
    def test_adapter_init_with_api_key(self, mock_api_key):
        """Test que TiingoAdapter se inicializa correctamente con API key."""
        adapter = TiingoAdapter(api_key=mock_api_key)
        
        assert adapter.api_key == mock_api_key
        assert adapter.name == "tiingo"
        assert adapter.base_url == "https://api.tiingo.com/tiingo/daily"
        assert adapter.supports_intraday == False
        assert adapter.allowed_intervals == ["1d"]
    
    def test_adapter_init_without_api_key_raises(self):
        """Test que TiingoAdapter lanza error sin API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key de Tiingo requerida"):
                TiingoAdapter()
    
    def test_adapter_init_with_env_var(self, mock_api_key):
        """Test que TiingoAdapter obtiene API key de variable de entorno."""
        with patch.dict('os.environ', {'TIINGO_API_KEY': mock_api_key}):
            adapter = TiingoAdapter()
            assert adapter.api_key == mock_api_key
    
    @patch('requests.get')
    def test_download_symbol_success(self, mock_get, mock_api_key, mock_tiingo_response):
        """Test descarga exitosa de datos desde Tiingo."""
        # Mock de la respuesta HTTP
        mock_response = Mock()
        mock_response.json.return_value = mock_tiingo_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        adapter = TiingoAdapter(api_key=mock_api_key)
        result = adapter.download_symbol(
            "AAPL", 
            start="2024-01-01", 
            end="2024-01-10", 
            interval="1d"
        )
        
        # Verificar estructura del DataFrame
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        assert len(result) == 3
        assert result.index.is_monotonic_increasing
        assert isinstance(result.index, pd.DatetimeIndex)
        
        # Verificar datos
        assert result["Close"].iloc[0] == pytest.approx(150.5)
        assert result["Close"].iloc[1] == pytest.approx(151.0)
        assert result["Close"].iloc[2] == pytest.approx(152.0)
        assert result["Volume"].iloc[0] == pytest.approx(1000000)
        
        # Verificar que se hizo la petición correcta
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'AAPL' in call_args[0][0]  # URL contiene símbolo
        assert call_args[1]['params']['token'] == mock_api_key
        assert call_args[1]['params']['startDate'] == "2024-01-01"
        assert call_args[1]['params']['endDate'] == "2024-01-10"
    
    @patch('requests.get')
    def test_download_symbol_empty_data(self, mock_get, mock_api_key):
        """Test que TiingoAdapter lanza error con datos vacíos."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        adapter = TiingoAdapter(api_key=mock_api_key)
        
        with pytest.raises(ExtractionError, match="No se encontraron datos"):
            adapter.download_symbol("INVALID", start="2024-01-01", end="2024-01-10", interval="1d")
    
    @patch('requests.get')
    def test_download_symbol_404_not_found(self, mock_get, mock_api_key):
        """Test manejo de símbolo no encontrado (404)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        adapter = TiingoAdapter(api_key=mock_api_key)
        
        with pytest.raises(ExtractionError, match="no encontrado"):
            adapter.download_symbol("INVALID", start="2024-01-01", end="2024-01-10", interval="1d")
    
    @patch('requests.get')
    def test_download_symbol_401_invalid_api_key(self, mock_get, mock_api_key):
        """Test manejo de API key inválida (401)."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        adapter = TiingoAdapter(api_key=mock_api_key)
        
        with pytest.raises(ExtractionError, match="API key.*inválida"):
            adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
    
    @patch('requests.get')
    def test_download_symbol_429_rate_limit(self, mock_get, mock_api_key):
        """Test manejo de límite de rate excedido (429)."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        adapter = TiingoAdapter(api_key=mock_api_key)
        
        with pytest.raises(ExtractionError, match="Límite de rate"):
            adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
    
    @patch('requests.get')
    def test_download_symbol_timeout(self, mock_get, mock_api_key):
        """Test manejo de timeout en petición."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        adapter = TiingoAdapter(api_key=mock_api_key, timeout=5)
        
        with pytest.raises(ExtractionError, match="Timeout"):
            adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
    
    def test_download_symbol_invalid_interval(self, mock_api_key):
        """Test que TiingoAdapter lanza error con intervalo inválido."""
        adapter = TiingoAdapter(api_key=mock_api_key)
        
        with pytest.raises(ExtractionError, match="no soportado"):
            adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1h")
    
    @patch('requests.get')
    def test_parse_to_dataframe_with_regular_columns(self, mock_get, mock_api_key):
        """Test parsing de respuesta con columnas regulares (no ajustadas)."""
        # Mock con respuesta sin columnas ajustadas (adjClose, adjOpen, etc.)
        response_no_adj = [
            {
                "date": "2024-01-02T00:00:00.000Z",
                "close": 150.5,
                "high": 152.0,
                "low": 149.0,
                "open": 151.0,
                "volume": 1000000,
            }
        ]
        
        mock_response = Mock()
        mock_response.json.return_value = response_no_adj
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        adapter = TiingoAdapter(api_key=mock_api_key)
        result = adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
        
        # Verificar que se crearon todas las columnas requeridas
        assert "Close" in result.columns
        assert "Adj Close" in result.columns
        assert result["Close"].iloc[0] == pytest.approx(150.5)
        assert result["Adj Close"].iloc[0] == pytest.approx(150.5)
    
    @patch('requests.get')
    def test_download_multiple_symbols_sequential(self, mock_get, mock_api_key, mock_tiingo_response):
        """Test descarga secuencial de múltiples símbolos."""
        mock_response = Mock()
        mock_response.json.return_value = mock_tiingo_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        adapter = TiingoAdapter(api_key=mock_api_key)
        
        # Descargar varios símbolos
        symbols = ["AAPL", "MSFT", "GOOGL"]
        results = {}
        
        for symbol in symbols:
            results[symbol] = adapter.download_symbol(
                symbol, 
                start="2024-01-01", 
                end="2024-01-10", 
                interval="1d"
            )
        
        # Verificar que se descargaron todos
        assert len(results) == 3
        for symbol, df in results.items():
            assert isinstance(df, pd.DataFrame)
            assert not df.empty
            assert len(df) == 3
    
    @patch('requests.get')
    def test_date_parsing_timezone_handling(self, mock_get, mock_api_key):
        """Test que TiingoAdapter maneja correctamente fechas con timezone."""
        # Respuesta con timezone UTC explícito
        response_with_tz = [
            {
                "date": "2024-01-02T00:00:00.000Z",
                "adjClose": 150.0,
                "adjHigh": 151.0,
                "adjLow": 149.0,
                "adjOpen": 150.5,
                "adjVolume": 1000000,
            }
        ]
        
        mock_response = Mock()
        mock_response.json.return_value = response_with_tz
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        adapter = TiingoAdapter(api_key=mock_api_key)
        result = adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
        
        # Verificar que el índice es DatetimeIndex sin timezone (normalizado por BaseAdapter)
        assert isinstance(result.index, pd.DatetimeIndex)
        # BaseAdapter._finalize_ohlcv() elimina timezone
        assert result.index.tz is None
    
    @patch('requests.get')
    def test_get_symbols_with_mock(self, mock_get, mock_api_key, mock_tiingo_response):
        """Test que get_symbols funciona correctamente con parámetros."""
        adapter = TiingoAdapter(api_key=mock_api_key)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_tiingo_response
        
        result = adapter.get_symbols(
            symbols=['AAPL'],
            start=pd.Timestamp('2024-01-01'),
            end=pd.Timestamp('2024-01-10'),
            interval='1d'
        )
        
        assert isinstance(result, dict)
        assert 'AAPL' in result
    
    @patch('requests.get')
    def test_adapter_respects_timeout_parameter(self, mock_get, mock_api_key, mock_tiingo_response):
        """Test que TiingoAdapter respeta el parámetro timeout."""
        mock_response = Mock()
        mock_response.json.return_value = mock_tiingo_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        custom_timeout = 15
        adapter = TiingoAdapter(api_key=mock_api_key, timeout=custom_timeout)
        
        adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
        
        # Verificar que el timeout se pasó a requests.get
        call_args = mock_get.call_args
        assert call_args[1]['timeout'] == custom_timeout
    
    @patch('requests.get')
    def test_data_normalization_consistency(self, mock_get, mock_api_key, mock_tiingo_response):
        """Test que los datos se normalizan consistentemente (parte de BaseAdapter)."""
        mock_response = Mock()
        mock_response.json.return_value = mock_tiingo_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        adapter = TiingoAdapter(api_key=mock_api_key)
        result = adapter.download_symbol("AAPL", start="2024-01-01", end="2024-01-10", interval="1d")
        
        # Verificar normalización de BaseAdapter
        # - Columnas en orden correcto
        expected_columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        assert list(result.columns) == expected_columns
        
        # - Todas las columnas son float64
        for col in expected_columns:
            assert result[col].dtype in ['float64', 'int64']
        
        # - Índice ordenado ascendente
        assert result.index.is_monotonic_increasing
        
        # - Sin duplicados en índice
        assert not result.index.has_duplicates

