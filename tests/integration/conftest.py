import os
import sys
import pathlib
import logging
import logging.config
import socket
import pytest
import pandas as pd

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
VAR_LOG_DIR = REPO_ROOT / "var" / "logs"
VAR_LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = VAR_LOG_DIR / "tests.log"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

LOGGING_CFG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": str(LOG_FILE),
            "maxBytes": 1048576,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        # Tu namespace completo
        "data_extractor": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "data_extractor.adapters.yahoo_adapter": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "data_extractor.adapters.binance_adapter": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "data_extractor.adapters.tiingo_adapter": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        # DEPRECADO: Stooq reemplazado por Tiingo
        # "data_extractor.adapters.stooq_adapter": {
        #     "level": "INFO",
        #     "handlers": ["console", "file"],
        #     "propagate": False,
        # },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"],  # el root solo a consola; los tuyos ya van a fichero
    },
}

logging.config.dictConfig(LOGGING_CFG)
logging.getLogger("data_extractor").info("Logging inicializado -> %s", LOG_FILE)
print(f"[LOGGING] Escribiendo logs en: {LOG_FILE}")
# =============================================================================


def _can_resolve_and_connect(host: str = "8.8.8.8", port: int = 53, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

@pytest.fixture(autouse=True)
def skip_if_offline():
    if not _can_resolve_and_connect():
        pytest.skip("Sin conexión a Internet: se omiten tests de integración", allow_module_level=True)

@pytest.fixture
def recent_window_days():
    end = pd.Timestamp.utcnow().floor('h')
    start = end - pd.Timedelta(days=3)
    # fuerza naive
    if getattr(start, "tzinfo", None):
        start = start.tz_localize(None)
    if getattr(end, "tzinfo", None):
        end = end.tz_localize(None)
    return start, end
