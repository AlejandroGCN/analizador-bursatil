
from data_extractor.core.base.base_provider import BaseProvider
from ..providers.yahoo_provider import YahooProvider
from ..providers.binance_provider import BinanceProvider
from ..providers.stooq_provider import StooqProvider

SourceName = str

# Mapa fuente → clase Provider
REGISTRY: dict[SourceName, type[BaseProvider]] = {
    "yahoo": YahooProvider,
    "stooq": StooqProvider,
    "binance": BinanceProvider,
}
