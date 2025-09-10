from dataclasses import dataclass
from typing import List

from src.core.aws.config import Config
from src.core.aws.resource_handlers.ebs_resource_handlers import EbsResourceHandlers
from src.core.utils import get_common_elements


@dataclass
class AwsCostManager:

    def __init__(self, region: str):
        self._config = Config()
        self._supported_services = self._config.get_supported_services
        self._region = region
        self._resource_strategy = {
            "ebs": EbsResourceHandlers(self._region)
        }

    def get_unused_resources(self, services: List[str] = []):
        unused_resources = []

        services = get_common_elements(self._supported_services, services)
        for service in services:
            unused_resources += self._resource_strategy[service].find_under_utilized_resource()

        return unused_resources
