from dataclasses import dataclass
from typing import Dict, List

import boto3

from src.core.aws.resource_handlers.resource_handler import ResourceHandler
from src.core.utils import get_logger

logger = get_logger()


@dataclass
class LoadBalancerResourceHandlers(ResourceHandler):
    def __init__(self, region_name: str):
        self._boto3 = boto3.client("elb", region_name=region_name)

    def _get_list(self):
        response = self._boto3.describe_load_balancers()
        return response.get("LoadBalancerDescriptions", [])

    @staticmethod
    def _get_lb_with_no_targets(lb_list: List[Dict]):
        lb_with_no_targets = []

        for lb in lb_list:
            if not lb.get("Instances"):
                lb_with_no_targets.append(lb)

        return lb_with_no_targets

    def _get_lb_with_all_unhealthy_targets(self, lb_list: List[Dict]):
        lb_with_all_unhealthy_targets = []

        for lb in lb_list:
            lb_name = lb.get("LoadBalancerName")
            if not lb_name:
                continue

            # Skip load balancers with no instances
            if not lb.get("Instances"):
                continue

            try:
                health_response = self._boto3.describe_instance_health(LoadBalancerName=lb_name)
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

    def find_under_utilized_resource(self) -> Dict:
        lb_list = self._get_list()
        no_targets = self._get_lb_with_no_targets(lb_list)
        all_unhealthy = self._get_lb_with_all_unhealthy_targets(lb_list)

        underutilized_resource = {"no_targets_lb": no_targets, "all_unhealthy": all_unhealthy}

        return underutilized_resource
