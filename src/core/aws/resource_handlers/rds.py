from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.core.aws.resource_handlers.cloudwatch import CloudWatch
from src.core.aws.resource_handlers.resource_handler import ResourceHandler
from src.core.utils import get_logger, get_boto3_client
from src.models.cloudwatch import CloudWatchMetric

logger = get_logger()


@dataclass
class RdsHandler(ResourceHandler):
    def __init__(self, region_name: str):
        self._boto3 = get_boto3_client(service_name="rds", region_name=region_name)
        self._cw = CloudWatch(region_name=region_name)

    def _list_get(self):
        rds_list = self._boto3.describe_db_instances()
        return rds_list.get("DBInstances", [])

    def _get_max_connection_for_instance(self, instance_id: str):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=120)

        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/RDS",
            metric_name="DatabaseConnections",
            dimensions=[{"Name": "DBInstanceIdentifier", "Value": instance_id}],
            start_time=start_time,
            end_time=end_time,
        )

        rds_instance_connection_metrics = self._cw.get_metrics(cloudwatch_metric)

        if not rds_instance_connection_metrics:
            return 0

        return max(metric.get("Maximum", 0) for metric in rds_instance_connection_metrics)

    def _get_max_connections_for_cluster(self, cluster_id: str):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=120)

        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/RDS",
            metric_name="DatabaseConnections",
            dimensions=[{"Name": "DBClusterIdentifier", "Value": cluster_id}],
            start_time=start_time,
            end_time=end_time,
        )

        rds_connection_metrics = self._cw.get_metrics(cloudwatch_metric)

        if not rds_connection_metrics:
            return 0

        return max(metric.get("Maximum", 0) for metric in rds_connection_metrics)

    def _get_rds_with_no_connections(self, rds_list: List[Dict]) -> List[Any]:
        rds_with_no_connections = []
        for rds in rds_list:
            max_connection = self._get_max_connections_for_cluster(rds.get("DBClusterIdentifier"))

            if max_connection == 0:
                rds_with_no_connections.append(rds)

        return rds_with_no_connections

    def _get_rds_instances_with_no_connections(self, rds_list: List[Dict]):
        rds_instances_with_no_connections = []
        for rds in rds_list:
            max_connection = self._get_max_connection_for_instance(rds.get("DBInstanceIdentifier"))

            if max_connection == 0:
                rds_instances_with_no_connections.append(rds)

        return rds_instances_with_no_connections

    def find_under_utilized_resource(self) -> Dict:
        rds_list = self._list_get()

        rds_with_no_connections = self._get_rds_with_no_connections(rds_list)
        rds_instances_with_no_connections = self._get_rds_with_no_connections(rds_list)

        return {
            "rds_with_no_connections": rds_with_no_connections,
            "rds_instances_with_no_connections": rds_instances_with_no_connections,
        }
