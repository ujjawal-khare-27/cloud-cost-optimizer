import os
from dataclasses import dataclass
from typing import List, Any

from src.core.aws.constants import CONFIG_MAP


@dataclass
class Config:
    _env: str
    _config: dict[str, Any]

    def __init__(self):
        self._env = os.getenv("ENV", "prod")
        self._config = CONFIG_MAP[self._env]

    @property
    def get_supported_services(self) -> List[str]:
        return self._config.get("services")