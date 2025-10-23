# utils/logging_boot.py
from __future__ import annotations
import argparse, json, logging, logging.config, os, sys, yaml
from pathlib import Path

def _bin_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys.executable).resolve().parent
    # caso normal
    return Path(sys.argv[0]).resolve().parent

def resolve_log_cfg(cli_arg: str | None = None) -> Path | None:
    """
    Prioridad: 1) CLI --log-config  2) ENV LOG_CFG  3) ./logging.yaml junto al binario
    """
    # 1) CLI
    if cli_arg:
        p = Path(cli_arg).expanduser().resolve()
        if p.exists():
            return p

    # 2) ENV
    env = os.getenv("LOG_CFG")
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p

    # 3) default junto al binario
    p = (_bin_dir() / "logging.yaml").resolve()
    if p.exists():
        return p

    return None

def _make_log_dirs(cfg: dict, base_dir: Path) -> None:
    """
    Si algún handler usa archivo, crea su carpeta si no existe.
    Soporta rutas relativas al binario.
    """
    handlers = cfg.get("handlers", {})
    for h in handlers.values():
        if isinstance(h, dict) and h.get("class", "").endswith("FileHandler"):
            filename = h.get("filename")
            if filename:
                log_path = (base_dir / filename).resolve() if not os.path.isabs(filename) else Path(filename)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                # Reescribe filename con la ruta absoluta final
                h["filename"] = str(log_path)

def setup_logging_from_file(cfg_path: Path | None) -> None:
    if not cfg_path:
        # Fallback mínimo si no hay archivo
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.getLogger(__name__).warning("No se encontró logging.yaml; usando configuración básica.")
        return

    with cfg_path.open("r", encoding="utf-8") as f:
        if cfg_path.suffix.lower() in {".yml", ".yaml"}:
            cfg = yaml.safe_load(f)
        elif cfg_path.suffix.lower() == ".json":
            cfg = json.load(f)
        else:
            raise RuntimeError(f"Formato no soportado para logging: {cfg_path.suffix}")

    _make_log_dirs(cfg, base_dir=cfg_path.parent)
    logging.config.dictConfig(cfg)

def boot_logging_from_argv(default_path=None, default_level=logging.INFO):
    """
    Inicializa el logging desde YAML o crea uno básico si falla.
    Usa las rutas de LOG_CFG y LOG_FILE del entorno.
    """
    log_cfg = os.environ.get("LOG_CFG", "")
    log_file = os.environ.get("LOG_FILE", "")

    try:
        if log_cfg and pathlib.Path(log_cfg).exists():
            with open(log_cfg, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Inyecta la ruta de LOG_FILE si existe en entorno
            if log_file:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                for handler in config.get("handlers", {}).values():
                    if "filename" in handler:
                        handler["filename"] = log_file

            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)
        logging.info(f"Logging inicializado (cfg={log_cfg}, file={log_file})")
    except Exception as e:
        logging.basicConfig(level=default_level)
        logging.warning(f"No se pudo inicializar logging: {e}")
