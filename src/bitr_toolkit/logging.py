from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path
from typing import Literal

LogFormat = Literal["simple", "verbose"]


def setup_logging(
    *,
    level: str = "INFO",
    debug: bool = False,
    log_format: LogFormat = "simple",
    log_file: str | Path | None = None,
    log_dir: str | Path = "logs",
) -> logging.Logger:
    """
    Configura logging para la aplicación.

    La configuración anterior se reemplaza mediante force=True.
    Esto evita handlers duplicados cuando se ejecutan tests o comandos
    múltiples dentro del mismo proceso.
    """
    effective_level = (
        logging.DEBUG
        if debug
        else getattr(
            logging,
            level.upper(),
            logging.INFO,
        )
    )

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    if log_format == "verbose":
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(filename)s:%(lineno)d | %(message)s"
        )

    handlers: list[logging.Handler] = []
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    resolved_log_file: Path | None = None

    if log_file:
        resolved_log_file = Path(log_file).expanduser()
    else:
        log_dir_path = Path(log_dir).expanduser()
        resolved_log_file = log_dir_path / "application.log"

    if resolved_log_file:
        if resolved_log_file.exists() and resolved_log_file.is_dir():
            raise ValueError(f"log_file apunta a un directorio: {resolved_log_file}")

        resolved_log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            resolved_log_file,
            maxBytes=20 * 1024 * 1024,
            backupCount=9,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=effective_level,
        handlers=handlers,
        force=True,
    )
    return logging.getLogger()
