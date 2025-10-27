from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from typing import Optional


@dataclass
class DatosParams:
    fuente: str
    simbolos: str
    fecha_ini: Optional[pd.Timestamp]
    fecha_fin: Optional[pd.Timestamp]
    intervalo: str
    tipo: str


@dataclass
class CarteraParams:
    symbols: str
    weights: str
    valor_inicial: float


@dataclass
class MonteCarloParams:
    nsims: int
    horizonte: int
    vol_dinamica: bool
    valor_inicial: float


@dataclass
class ReporteParams:
    formato: str
    incluir_riesgo: bool


@dataclass
class ConfigParams:
    normalizacion: str

