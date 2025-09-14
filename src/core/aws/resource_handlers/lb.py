from dataclasses import dataclass
from typing import Dict, List

from src.core.aws.resource_handlers.resource_handler import ResourceHandler
from src.core.utils import get_logger, AsyncClientManager

logger = get_logger()


@dataclass
class LoadBalancerResourceHandlers(ResourceHandler):
    def __init__(self, region_name: str):
        self.region_name = region_name
        self._client_manager = AsyncClientManager(region_name)

    async def _get_list(self):
        async with self._client_manager as manager:
            async with manager.get_client("elb") as elb:
                response = await elb.describe_load_balancers()
                return response.get("LoadBalancerDescriptions", [])

    @staticmethod
    def _get_lb_with_no_targets(lb_list: List[Dict]):
        lb_with_no_targets = []

        for lb in lb_list:
            if not lb.get("Instances"):
                lb_with_no_targets.append(lb)

        return lb_with_no_targets

    async def _get_lb_with_all_unhealthy_targets(self, lb_list: List[Dict]):
        lb_with_all_unhealthy_targets = []

        async with self._client_manager as manager:
            async with manager.get_client("elb") as elb:
                for lb in lb_list:
                    lb_name = lb.get("LoadBalancerName")
                    if not lb_name:
                        continue

                    # Skip load balancers with no instances
                    if not lb.get("Instances"):
                        continue

                    try:
                        health_response = await elb.describe_instance_health(LoadBalancerName=lb_name)
                        instances = health_response.get("InstanceStates", [])

                        if not instances:
                            continue

                        all_unhealthy = all(instance.get("State") == "OutOfService" for instance in instances)

                        if all_unhealthy:
                            lb_with_all_unhealthy_targets.append(lb)

                    except Exception as e:
                        logger.info(f"Error checking health for load balancer {lb_name}: {e}")
                        continue

        return lb_with_all_unhealthy_targets

    async def find_under_utilized_resource(self) -> Dict:
        lb_list = await self._get_list()
        no_targets = self._get_lb_with_no_targets(lb_list)
        all_unhealthy = await self._get_lb_with_all_unhealthy_targets(lb_list)

        underutilized_resource = {"no_targets_lb": no_targets, "all_unhealthy": all_unhealthy}

        return underutilized_resource
