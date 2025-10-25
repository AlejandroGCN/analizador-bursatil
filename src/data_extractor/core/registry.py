
from data_extractor.core.base.base_provider import BaseProvider
from ..providers.yahoo_provider import YahooProvider
from ..providers.binance_provider import BinanceProvider

# Intentar importar StooqProvider, puede fallar si pandas_datareader no está disponible
try:
    from ..providers.stooq_provider import StooqProvider
    STOOQ_AVAILABLE = True
except ImportError:
    StooqProvider = None
    STOOQ_AVAILABLE = False

SourceName = str

# Mapa fuente → clase Provider (solo incluir fuentes disponibles)
REGISTRY: dict[SourceName, type[BaseProvider]] = {
    "yahoo": YahooProvider,
    "binance": BinanceProvider,
}

# Añadir Stooq solo si está disponible
if STOOQ_AVAILABLE:
    REGISTRY["stooq"] = StooqProvider
