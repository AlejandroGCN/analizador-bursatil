
from data_extractor.core.base.base_provider import BaseProvider
from ..providers.yahoo_provider import YahooProvider
from ..providers.binance_provider import BinanceProvider

# Intentar importar TiingoProvider
try:
    from ..providers.tiingo_provider import TiingoProvider
    TIINGO_AVAILABLE = True
except ImportError:
    TiingoProvider = None
    TIINGO_AVAILABLE = False

# DEPRECADO: StooqProvider reemplazado por Tiingo (mejor cobertura y calidad)
# Se mantiene el código por retrocompatibilidad pero no se registra por defecto
try:
    from ..providers.stooq_provider import StooqProvider
    STOOQ_AVAILABLE = True
except ImportError:
    StooqProvider = None
    STOOQ_AVAILABLE = False

SourceName = str

# Mapa fuente → clase Provider
# Fuentes principales: Yahoo (global), Binance (cripto), Tiingo (institucional)
REGISTRY: dict[SourceName, type[BaseProvider]] = {
    "yahoo": YahooProvider,
    "binance": BinanceProvider,
}

# Añadir Tiingo solo si está disponible
if TIINGO_AVAILABLE:
    REGISTRY["tiingo"] = TiingoProvider

# NOTA: Stooq deprecado en favor de Tiingo
# Si necesitas Stooq por compatibilidad, descomenta la siguiente línea:
# if STOOQ_AVAILABLE:
#     REGISTRY["stooq"] = StooqProvider
