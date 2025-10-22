from typing import Dict, Type
from .errors import DataSource
from ..providers.yahoo_provider import YahooProvider

REGISTRY: Dict[str, Type[DataSource]] = {
    "yahoo": YahooProvider,
}