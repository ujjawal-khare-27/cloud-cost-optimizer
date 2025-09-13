from src.core.utils import get_boto3_client
from src.models.cloudwatch import CloudWatchMetric


class CloudWatch:
    def __init__(self, region_name: str):
        self._cw = get_boto3_client(service_name="cloudwatch", region_name=region_name)

    def get_metrics(self, cloud_watch_metric: CloudWatchMetric):
        cw_metric = self._cw.get_metric_data(
            Namespace=cloud_watch_metric.namespace,
            MetricName=cloud_watch_metric.metric_name,
            Dimensions=cloud_watch_metric.dimensions,
            StartTime=cloud_watch_metric.start_time,
            EndTime=cloud_watch_metric.end_time,
            Period=cloud_watch_metric.period,
            Statistics=cloud_watch_metric.statistics,
            Unit=cloud_watch_metric.unit,
        )

        data_points = cw_metric.get("Datapoints")

        return data_points
