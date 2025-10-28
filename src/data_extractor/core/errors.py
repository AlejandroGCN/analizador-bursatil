# core/errors.py
from __future__ import annotations
from typing import Any, Dict, Optional, Mapping
from datetime import datetime
import email.utils as eutils  # para parsear fechas HTTP en Retry-After

__all__ = [
    "ExtractionError",
    "SymbolNotFound",
    "RateLimitError",
    "TemporaryNetworkError",
    "BadRequestError",
    "AuthError",
    "NormalizationError",
    #
    "build_error_from_http",
]

class ExtractionError(RuntimeError):
    """
    Error base con metadatos comunes para trazabilidad.
    Úsalo como contenedor estándar en adapters/providers.
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
            endpoint: Optional[str] = None,
            method: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            code: Optional[str] = None,  # código específico de la API si aplica
    ) -> None:
        super().__init__(message)
        self.source = source
        self.symbol = symbol
        self.status = status
        self.retry_after = retry_after
        self.extra = dict(extra or {})
        self.endpoint = endpoint
        self.method = method
        self.params = dict(params or {})
        self.code = code
        if cause is not None:
            self.__cause__ = cause  # preserva el encadenado

    # -------- helpers de introspección --------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": str(super().__str__()),
            "source": self.source,
            "symbol": self.symbol,
            "status": self.status,
            "retry_after": self.retry_after,
            "extra": self.extra,
            "endpoint": self.endpoint,
            "method": self.method,
            "params": self.params,
            "code": self.code,
            "type": self.__class__.__name__,
        }

    @property
    def is_transient(self) -> bool:
        """Heurística: ¿merece reintento?"""
        return isinstance(self, (TemporaryNetworkError, RateLimitError)) or (
                self.status in (408, 425, 429, 500, 502, 503, 504)
        )

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.source:      parts.append(f"[source={self.source}]")
        if self.symbol:      parts.append(f"[symbol={self.symbol}]")
        if self.status:      parts.append(f"[status={self.status}]")
        if self.retry_after is not None: parts.append(f"[retry_after={self.retry_after}]")
        if self.code:        parts.append(f"[code={self.code}]")
        if self.endpoint:    parts.append(f"[endpoint={self.endpoint}]")
        if self.method:      parts.append(f"[method={self.method}]")
        if self.params:      parts.append(f"[params={_safe_params(self.params)}]")
        if self.extra:       parts.append(f"[extra={self.extra}]")
        return " ".join(parts)

    # -------- fábricas convenientes --------
    @classmethod
    def from_http(
            cls,
            message: str,
            *,
            source: str,
            symbol: Optional[str] = None,
            status: Optional[int] = None,
            headers: Optional[Mapping[str, Any]] = None,
            cause: Optional[BaseException] = None,
            extra: Optional[Dict[str, Any]] = None,
            endpoint: Optional[str] = None,
            method: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            code: Optional[str] = None,
    ) -> "ExtractionError":
        return build_error_from_http(
            message=message,
            source=source,
            symbol=symbol,
            status=status,
            headers=headers,
            cause=cause,
            extra=extra,
            endpoint=endpoint,
            method=method,
            params=params,
            code=code,
        )

class SymbolNotFound(ExtractionError):
    """Símbolo inexistente o serie vacía en la fuente."""

class RateLimitError(ExtractionError):
    """Se alcanzó el límite de peticiones de la API."""

class TemporaryNetworkError(ExtractionError):
    """Errores transitorios de red (timeouts, caídas, DNS, etc.)."""

class BadRequestError(ExtractionError):
    """Parametros inválidos o request mal formado para la API."""

class AuthError(ExtractionError):
    """Fallo de autenticación/autorización."""

class NormalizationError(ExtractionError):
    """Fallo al normalizar datos a la tipología esperada."""

# -----------------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------------

def _parse_retry_after(headers: Optional[Mapping[str, Any]]) -> Optional[float]:
    if not headers:
        return None
    ra = headers.get("Retry-After") or headers.get("retry-after")
    if ra is None:
        return None
    # Puede venir como segundos o como fecha HTTP (RFC 7231)
    try:
        # segundos
        return float(ra)
    except (TypeError, ValueError):
        try:
            # fecha absoluta -> segundos hasta esa fecha
            dt = eutils.parsedate_to_datetime(str(ra))
            if dt is None:
                return None
            now = datetime.now(dt.tzinfo).replace(tzinfo=dt.tzinfo)
            delta = (dt - now).total_seconds()
            return max(delta, 0.0)
        except (ValueError, TypeError, OverflowError):
            return None

def _safe_params(params: Dict[str, Any]) -> Dict[str, Any]:
    # Evitar filtrar claves sensibles a logs; extiende si necesitas
    redacted = {}
    for k, v in params.items():
        if "key" in k.lower() or "secret" in k.lower() or "token" in k.lower():
            redacted[k] = "***"
        else:
            redacted[k] = v
    return redacted

def build_error_from_http(
        *,
        message: str,
        source: str,
        symbol: Optional[str] = None,
        status: Optional[int] = None,
        headers: Optional[Mapping[str, Any]] = None,
        cause: Optional[BaseException] = None,
        extra: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None,
) -> ExtractionError:
    """
    Clasifica y construye la subclase adecuada en base a 'status' y payloads típicos.
    """
    retry_after = _parse_retry_after(headers)
    base_kwargs = {
        "source": source, "symbol": symbol, "status": status, "retry_after": retry_after,
        "cause": cause, "extra": extra, "endpoint": endpoint, "method": method, "params": params, "code": code,
    }

    # Clasificación por status HTTP (heurística común)
    if status in (401, 403):
        return AuthError(message, **base_kwargs)
    if status in (400, 404, 422):
        # 404 en APIs a veces significa símbolo inválido: deja que el adapter use SymbolNotFound si lo sabe.
        return BadRequestError(message, **base_kwargs)
    if status == 429:
        return RateLimitError(message or "Rate limit exceeded", **base_kwargs)
    if status in (408, 425, 500, 502, 503, 504):
        return TemporaryNetworkError(message, **base_kwargs)

    # Sin status o no clasificable → ExtractionError genérico
    return ExtractionError(message, **base_kwargs)
