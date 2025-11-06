# -*- coding: utf-8 -*-
"""Tests unitarios para DataExtractor."""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from data_extractor.extractor import DataExtractor, _ensure_dt
from data_extractor.config import ExtractorConfig
from data_extractor.core.errors import ExtractionError


class TestEnsureDt:
    """Tests para la funcion _ensure_dt."""
    
    def test_none_returns_none(self):
        """Test que None retorna None."""
        assert _ensure_dt(None) is None
    
    def test_string_converts_to_timestamp(self):
        """Test conversion de string a Timestamp."""
        result = _ensure_dt('2023-01-01')
        assert isinstance(result, pd.Timestamp)
        assert result == pd.Timestamp('2023-01-01')
    
    def test_timestamp_passthrough(self):
        """Test que Timestamp se mantiene."""
        ts = pd.Timestamp('2023-01-01')
        result = _ensure_dt(ts)
        assert result == ts


class TestDataExtractorInit:
    """Tests para inicializacion de DataExtractor."""
    
    def test_init_default_config(self):
        """Test inicializacion con configuracion por defecto."""
        extractor = DataExtractor()
        assert extractor.cfg is not None
        assert extractor.source is not None
        assert extractor.cfg.source == 'yahoo'  # default
    
    def test_init_custom_config(self):
        """Test inicializacion con configuracion personalizada."""
        cfg = ExtractorConfig(source='yahoo', timeout=60, interval='1h')
        extractor = DataExtractor(cfg)
        assert extractor.cfg.source == 'yahoo'
        assert extractor.cfg.timeout == 60
        assert extractor.cfg.interval == '1h'
    
    def test_init_tiingo_with_api_key(self):
        """Test inicializacion de Tiingo con API key."""
        # Verificar que el TiingoProvider se inicializa correctamente con API key
        cfg = ExtractorConfig(source='tiingo', api_key='test_key_12345')
        extractor = DataExtractor(cfg)
        # Verificar que el provider se creo
        assert extractor.source is not None
        # Verificar que la config tiene la API key
        assert extractor.cfg.api_key == 'test_key_12345'
    
    def test_init_invalid_source_raises(self):
        """Test que fuente invalida levanta ValueError."""
        cfg = ExtractorConfig(source='invalid_source_xyz')
        with pytest.raises(ValueError, match="Fuente no registrada"):
            DataExtractor(cfg)


class TestGetMarketData:
    """Tests para get_market_data."""
    
    @pytest.fixture
    def mock_provider(self):
        """Fixture con provider mockeado."""
        mock = Mock()
        mock.get_symbols = Mock(return_value={'AAPL': Mock()})
        return mock
    
    @pytest.fixture
    def extractor_with_mock(self, mock_provider):
        """Fixture con DataExtractor y provider mockeado."""
        extractor = DataExtractor()
        extractor.source = mock_provider
        return extractor
    
    def test_single_symbol_as_string(self, extractor_with_mock, mock_provider):
        """Test get_market_data con un solo simbolo como string."""
        result = extractor_with_mock.get_market_data('AAPL', start='2023-01-01')
        
        # Verificar llamada al provider
        mock_provider.get_symbols.assert_called_once()
        call_args = mock_provider.get_symbols.call_args
        assert call_args.kwargs['symbols'] == ['AAPL']
    
    def test_multiple_symbols_as_list(self, extractor_with_mock, mock_provider):
        """Test get_market_data con multiples simbolos."""
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        result = extractor_with_mock.get_market_data(symbols, start='2023-01-01')
        
        call_args = mock_provider.get_symbols.call_args
        assert call_args.kwargs['symbols'] == symbols
    
    def test_empty_symbols_raises(self, extractor_with_mock):
        """Test que lista vacia levanta ValueError."""
        with pytest.raises(ValueError, match="Debe indicar al menos un símbolo"):
            extractor_with_mock.get_market_data([])
    
    def test_duplicate_symbols_removed(self, extractor_with_mock, mock_provider):
        """Test que simbolos duplicados se eliminan preservando orden."""
        result = extractor_with_mock.get_market_data(['AAPL', 'MSFT', 'AAPL'], start='2023-01-01')
        
        call_args = mock_provider.get_symbols.call_args
        symbols = call_args.kwargs['symbols']
        assert symbols == ['AAPL', 'MSFT']
        assert symbols.index('AAPL') < symbols.index('MSFT')  # Orden preservado
    
    def test_date_range_validation(self, extractor_with_mock):
        """Test que rango de fechas invalido levanta ValueError."""
        with pytest.raises(ValueError, match="Rango de fechas inválido"):
            extractor_with_mock.get_market_data(
                'AAPL', 
                start='2023-12-31', 
                end='2023-01-01'
            )
    
    def test_interval_parameter(self, extractor_with_mock, mock_provider):
        """Test que parametro interval se pasa correctamente."""
        extractor_with_mock.get_market_data('AAPL', interval='1h')
        
        call_args = mock_provider.get_symbols.call_args
        assert call_args.kwargs['interval'] == '1h'
    
    def test_interval_defaults_to_config(self, mock_provider):
        """Test que interval usa valor de configuracion si no se especifica."""
        cfg = ExtractorConfig(interval='1d')
        extractor = DataExtractor(cfg)
        extractor.source = mock_provider
        
        extractor.get_market_data('AAPL')
        
        call_args = mock_provider.get_symbols.call_args
        assert call_args.kwargs['interval'] == '1d'
    
    def test_kind_parameter(self, extractor_with_mock, mock_provider):
        """Test diferentes tipos de datos."""
        extractor_with_mock.get_market_data('AAPL', kind='returns_log')
        
        call_args = mock_provider.get_symbols.call_args
        assert call_args.kwargs['kind'] == 'returns_log'
    
    def test_extra_params_passed_through(self, extractor_with_mock, mock_provider):
        """Test que parametros extras se pasan al provider."""
        extractor_with_mock.get_market_data(
            'AAPL',
            align='intersect',
            ffill=True,
            bfill=False
        )
        
        call_args = mock_provider.get_symbols.call_args
        assert call_args.kwargs['align'] == 'intersect'
        assert call_args.kwargs['ffill'] is True
        assert call_args.kwargs['bfill'] is False
    
    def test_config_defaults_applied(self, mock_provider):
        """Test que valores por defecto de config se aplican."""
        cfg = ExtractorConfig(align='union', ffill=True, bfill=True)
        extractor = DataExtractor(cfg)
        extractor.source = mock_provider
        
        extractor.get_market_data('AAPL')
        
        call_args = mock_provider.get_symbols.call_args
        assert call_args.kwargs['align'] == 'union'
        assert call_args.kwargs['ffill'] is True
        assert call_args.kwargs['bfill'] is True
    
    def test_extraction_error_propagates(self, extractor_with_mock, mock_provider):
        """Test que ExtractionError se propaga."""
        mock_provider.get_symbols.side_effect = ExtractionError("Test error")
        
        with pytest.raises(ExtractionError, match="Test error"):
            extractor_with_mock.get_market_data('AAPL')
    
    def test_generic_exception_wrapped(self, extractor_with_mock, mock_provider):
        """Test que excepciones genericas se envuelven en ExtractionError."""
        mock_provider.get_symbols.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(ExtractionError, match="Fallo en extracción"):
            extractor_with_mock.get_market_data('AAPL')
    
    def test_timestamp_conversion_start_end(self, extractor_with_mock, mock_provider):
        """Test conversion de fechas string a Timestamp."""
        extractor_with_mock.get_market_data(
            'AAPL',
            start='2023-01-01',
            end='2023-12-31'
        )
        
        call_args = mock_provider.get_symbols.call_args
        start = call_args.kwargs['start']
        end = call_args.kwargs['end']
        
        assert isinstance(start, pd.Timestamp)
        assert isinstance(end, pd.Timestamp)
        assert start == pd.Timestamp('2023-01-01')
        assert end == pd.Timestamp('2023-12-31')
    
    def test_none_dates_passed_through(self, extractor_with_mock, mock_provider):
        """Test que None en fechas se mantiene como None."""
        extractor_with_mock.get_market_data('AAPL')
        
        call_args = mock_provider.get_symbols.call_args
        # start y end deben ser None si no se especifican
        assert call_args.kwargs['start'] is None
        assert call_args.kwargs['end'] is None
    
    def test_returns_provider_result(self, extractor_with_mock, mock_provider):
        """Test que el resultado del provider se retorna."""
        expected = {'AAPL': Mock(), 'MSFT': Mock()}
        mock_provider.get_symbols.return_value = expected
        
        result = extractor_with_mock.get_market_data(['AAPL', 'MSFT'])
        
        assert result == expected

