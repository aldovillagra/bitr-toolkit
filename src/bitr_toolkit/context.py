from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic_settings import BaseSettings

SettingsType = TypeVar("SettingsType", bound=BaseSettings)


@dataclass
class AppContext(Generic[SettingsType]):
    settings: SettingsType
