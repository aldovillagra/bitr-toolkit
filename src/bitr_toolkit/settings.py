from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any, TypeVar, TypeVar

import tomli_w
import typer
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

SettingsType = TypeVar("SettingsType", bound=BaseSettings)


def default_config_path(app_name: str) -> Path:
    """
    Retorna la ruta estándar del archivo TOML de configuración
    """
    return Path.home() / f".{app_name}.toml"


def load_config_file(path: Path) -> dict[str, Any]:
    """
    Carga un archivo TOML o JSON.

    El archivo debe contener un objeto/diccionario en la raíz.
    """
    if not path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {path}")

    suffix = path.suffix.lower()

    if suffix == ".toml":
        with path.open("rb") as file:
            data = tomllib.load(file)
    elif suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError(
            f"Formato no soportado: {suffix}. Formátos válidos: .toml y json"
        )

    if not isinstance(data, dict):
        raise ValueError(
            f"El archivo {path} debe contener un objeto/diccionario en la raíz"
        )

    return data


def dump_settings(settings: BaseModel) -> str:
    """
    Serializa settings en TOML.

    model_dump(mode='json') permite serializar Path y otros tipos compatibles.
    """
    data = settings.model_dump(mode="json")
    return tomli_w.dumps(data)


def create_default_config(
    settings_cls: type[SettingsType],
    path: Path,
) -> None:
    """Crea un archivo TOML con los valores por defecto."""
    path.parent.mkdir(parents=True, exist_ok=True)

    default_settings = settings_cls()
    path.write_text(
        dump_settings(default_settings),
        encoding="utf-8",
    )


def load_settings(
    settings_cls: type[SettingsType],
    app_name: str,
    config_path: Path | None = None,
    *,
    create_if_missing: bool = True,
    interactive: bool = False,
) -> SettingsType:
    """
    Carga configuración de una aplicación.

    Precedencia actual:

    1. Valores por defecto de Pydantic.
    2. Archivo TOML/JSON.
    3. Variables de entorno.
    4. Argumentos explícitos entregados al constructor.

    Nota:
    Para mantener la precedencia correcta entre TOML y variables de entorno,
    se cargan las variables del archivo .env antes de construir Settings.
    """
    path = config_path or default_config_path(app_name)

    # Carga .env sin obligar a que exista.
    dotenv_path = Path(".env")
    if dotenv_path.exists():
        if not create_if_missing:
            return settings_cls()

        if interactive:
            typer.echo(f"No existe el archivo de configuracion: {path}")
            typer.echo("\nConfiguración por defecto:\n")
            typer.echo(dump_settings(settings_cls()))

            if not typer.confirm("¿Crear archivo de configuración?", default=True):
                raise typer.Exit(code=1)

            create_default_config(settings_cls, path)
            typer.echo(f"Configuración creada: {path}")
        else:
            # En ejecución no inreactiva no se debe bloquear el proceso.
            create_default_config(settings_cls, path)

    file_data = load_config_file(path)

    # los valores del archivo se usan como argumentos explícitos.
    # en pydantic settings, los argumentos explicitos tienen prioridad
    # sobre los environment variables.
    return settings_cls(**file_data)


def reload_settings_from_env(
    settings_cls: type[SettingsType],
    env_path: Path,
) -> SettingsType:
    """
    Carga una nueva instancia usando un archivo .env especifico.
    """
    if not env_path.exists():
        raise FileNotFoundError(f"Archivo .env no encontrado: {env_path}")

    load_dotenv(env_path, override=True)
    return settings_cls()
