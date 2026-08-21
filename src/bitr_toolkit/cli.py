from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from pydantic_settings import BaseSettings

from .context import AppContext
from .logging import setup_logging
from .settings import load_settings


def create_app(
    *,
    app_name: str,
    settings_cls: type[BaseSettings],
    help_text: str,
    no_args_is_help: bool = True,
) -> typer.Typer:
    """
    Crea una aplicación Typer con configuración y logging inicializados.
    """
    app = typer.Typer(
        name=app_name,
        help=help_text,
        no_args_is_help=no_args_is_help,
    )

    @app.callback()
    def main(
        ctx: typer.Context,
        config: Path | None = typer.Option(
            None,
            "--config",
            "-c",
            help="Ruta del archivo TOML o JSON.",
            exists=False,
            dir_okay=False,
        ),
        debug: bool | None = typer.Option(
            None,
            "--debug/--no-debug",
            help="Activa o desactiva el modo debug.",
        ),
        interactive: bool = typer.Option(
            False,
            "--interactive",
            help="Permite crear configuración preguntando al usuario.",
        ),
    ) -> None:
        settings = load_settings(
            settings_cls=settings_cls,
            app_name=app_name,
            config_path=config,
            interactive=interactive,
            create_if_missing=True,
        )

        if debug is not None:
            settings.debug = debug

        setup_logging(
            level=settings.log_level,
            debug=settings.debug,
            log_format=settings.log_format,
            log_file=settings.log_file or None,
            log_dir=settings.log_dir,
        )

        ctx.obj = AppContext(settings=settings)

    return app


def get_context(
    ctx: typer.Context,
    settings_cls: type[BaseSettings],
) -> AppContext[Any]:
    """Obtiene y valida el contexto de la aplicación."""
    context = ctx.ensure_object(AppContext)

    if not isinstance(context.settings, settings_cls):
        raise typer.BadParameter("El contexto no contiene la clase Settings esperada")

    return context
