import os
import asyncio
from dataclasses import dataclass
from typing import List

from src.core.aws.config import Config
from src.core.aws.resource_handlers.ebs import EbsResourceHandlers
from src.core.aws.resource_handlers.lb import LoadBalancerResourceHandlers
from src.core.aws.resource_handlers.rds import RdsHandler
from src.core.utils.excel_report_generator import ExcelReportGenerator
from src.core.utils import get_common_elements, get_logger

logger = get_logger()


@dataclass
class AwsCostManager:

    def __init__(self, region: str):
        self._config = Config()
        self._supported_services = self._config.get_supported_services
        self._region = region
        self._resource_strategy = {
            "ebs": EbsResourceHandlers(self._region),
            "lb": LoadBalancerResourceHandlers(self._region),
            "rds": RdsHandler(self._region),
        }

    async def get_unused_resources(self, services: List[str] = []):
        unused_resources = []

        if len(services) != 0:
            services = get_common_elements(self._supported_services, services)
        else:
            services = self._supported_services

        for service in services:
            result = await self._resource_strategy[service].find_under_utilized_resource()
            unused_resources.append({service: result})

        return unused_resources

    async def get_unused_resources_report(self, services: List[str] = [], output_path: str = None) -> str:
        """
        Generate an Excel report for unused resources.

        Args:
            services: List of services to analyze. If empty, analyzes all supported services.
            output_path: Optional custom path for the Excel file.

        Returns:
            Path to the generated Excel report file.
        """
        unused_resources = await self.get_unused_resources(services)

        report_generator = ExcelReportGenerator()
        report_path = report_generator.generate_report(
            unused_resources=unused_resources, region=self._region, output_path=output_path
        )

        return report_path


if __name__ == "__main__":

    async def main():
        cost_manager = AwsCostManager(os.getenv("AWS_REGION"))

        report_path = await cost_manager.get_unused_resources_report()
        logger.info(f"Report generated successfully: {report_path}")

    asyncio.run(main())
