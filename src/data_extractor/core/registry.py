
from .base_provider import BaseProvider
from ..providers.yahoo_provider import YahooProvider
from ..providers.alpha_vantage_provider import AlphaVantageProvider
from ..providers.binance_provider import BinanceProvider

SourceName = str

# Mapa fuente → clase Provider
REGISTRY: dict[SourceName, type[BaseProvider]] = {
    "yahoo": YahooProvider,
    "alpha_vantage": AlphaVantageProvider,
    "binance": BinanceProvider,
}
