# core/registry.py
from typing import Dict, Type
from .base import DataSource
from ..providers.yahoo_provider import YahooProvider  # <- antes: YahooSource
import logging
logger = logging.getLogger(__name__)

REGISTRY: Dict[str, Type[DataSource]] = {
    "yahoo": YahooProvider,  # <- antes: YahooSource
    # "alpha_vantage": AlphaVantageProvider,
}
logger.info("REGISTRY inicializado con fuentes: %s", list(REGISTRY.keys()))
