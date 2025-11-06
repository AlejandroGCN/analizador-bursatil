# providers/tiingo_provider.py
from __future__ import annotations
import logging
from typing import Optional

from data_extractor.core.base.base_provider import BaseProvider
from ..adapters.tiingo_adapter import TiingoAdapter

logger = logging.getLogger(__name__)


class TiingoProvider(BaseProvider):
    """
    Provider de Tiingo API basado en BaseProvider.
    
    Tiingo ofrece datos de calidad institucional para más de 70 exchanges globales.
    Requiere API key gratuita de https://www.tiingo.com/
    
    Ventajas:
    - Cobertura global (USA, Europa, Asia, Australia)
    - Datos de calidad institucional
    - 1000 símbolos únicos por día (free tier)
    - 500 requests por hora
    - Datos históricos hasta 30+ años
    - API limpia y bien documentada
    
    Limitaciones Free Tier:
    - Solo datos end-of-day (EOD)
    - No soporta datos intraday
    - Requiere API key (gratis pero con registro)
    """
    
    def __init__(
        self, 
        timeout: int = 30, 
        max_workers: int = 8,
        api_key: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Inicializa TiingoProvider.
        
        Args:
            timeout: Timeout para requests en segundos
            max_workers: Número de workers para descarga paralela
            api_key: API key de Tiingo (obtener gratis en tiingo.com)
                     Si no se proporciona, se busca en variable de entorno TIINGO_API_KEY
            **kwargs: Argumentos adicionales (ignorados)
        """
        adapter = TiingoAdapter(
            api_key=api_key,
            timeout=timeout, 
            max_workers=max_workers
        )
        super().__init__(source_name="tiingo", adapter=adapter)
        
        logger.info(
            "TiingoProvider inicializado (timeout=%s, max_workers=%s)", 
            timeout, max_workers
        )

