from __future__ import annotations

from typing import Optional, Protocol, Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class ExtractionError(RuntimeError):
    """
    Error genérico de extracción con metadatos para trazabilidad.
    """

    def __init__(
            self,
            message: str,
            *,
            source: Optional[str] = None,
            symbol: Optional[str] = None,
            status: Optional[int] = None,
            retry_after: Optional[float] = None,
            cause: Optional[BaseException] = None,
            extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.source = source
        self.symbol = symbol
        self.status = status
        self.retry_after = retry_after
        self.extra = dict(extra or {})
        # Mantener cadena de excepción original
        if cause is not None:
            self.__cause__ = cause

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.source:
            parts.append(f"[source={self.source}]")
        if self.symbol:
            parts.append(f"[symbol={self.symbol}]")
        if self.status is not None:
            parts.append(f"[status={self.status}]")
        if self.retry_after is not None:
            parts.append(f"[retry_after={self.retry_after}]")
        if self.extra:
            parts.append(f"[extra={self.extra}]")
        return " ".join(parts)

    @classmethod
    def from_http(
            cls,
            message: str,
            *,
            source: str,
            symbol: Optional[str],
            status: Optional[int],
            headers: Optional[Dict[str, Any]] = None,
            cause: Optional[BaseException] = None,
            extra: Optional[Dict[str, Any]] = None,
    ) -> "ExtractionError":

        retry_after: Optional[float] = None
        if headers:
            ra = headers.get("Retry-After") or headers.get("retry-after")
            if ra is not None:
                try:
                    retry_after = float(ra)
                except (TypeError, ValueError):
                    retry_after = None

        return cls(
            message,
            source=source,
            symbol=symbol,
            status=status,
            retry_after=retry_after,
            cause=cause,
            extra=extra,
        )


class SymbolNotFound(ExtractionError):
    """El símbolo solicitado no existe en la fuente o la serie devuelta está vacía."""
    pass


class RateLimitError(ExtractionError):
    """Se alcanzó el límite de peticiones (rate limit) de la API."""
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, **kwargs)


class TemporaryNetworkError(ExtractionError):
    """Errores transitorios de red (timeouts, conexiones caídas)."""
    pass


class BadRequestError(ExtractionError):
    """Entrada inválida para la API (símbolo mal formado, parámetros inválidos)."""
    pass


class AuthError(ExtractionError):
    """Problemas de autenticación/autorización con la API."""
    pass

class NormalizationError(ExtractionError):
    """Error al intentar normalizar datos (estructura o columnas inesperadas)."""
    pass

class DataSource(Protocol):
    """
    Contrato de proveedor completo (patrón Source).
    Un `Source` combina la obtención del payload y su normalización,
    devolviendo directamente un DataFrame OHLCV listo para usar.
    """
    def get_data(
            self,
            symbol: str,
            start: Optional[pd.Timestamp],
            end: Optional[pd.Timestamp],
            interval: str,
    ) -> pd.DataFrame:
        """Descarga y normaliza un símbolo en un DataFrame OHLCV.
        Debe lanzar `SymbolNotFound` si el símbolo no existe o no retorna datos.
        """
        ...
