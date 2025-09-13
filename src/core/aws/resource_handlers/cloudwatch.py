from src.core.utils import get_boto3_client
from src.models.cloudwatch import CloudWatchMetric


class CloudWatch:
    def __init__(self, region_name: str):
        self._cw = get_boto3_client(service_name="cloudwatch", region_name=region_name)

    def get_metrics(self, cloud_watch_metric: CloudWatchMetric):
        # Convert dimensions to the format expected by get_metric_data
        dimensions_dict = {}
        for dim in cloud_watch_metric.dimensions:
            dimensions_dict[dim["Name"]] = dim["Value"]
        
        # Create MetricDataQueries structure for get_metric_data API
        metric_data_queries = [
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": cloud_watch_metric.namespace,
                        "MetricName": cloud_watch_metric.metric_name,
                        "Dimensions": [
                            {"Name": name, "Value": value}
                            for name, value in dimensions_dict.items()
                        ]
                    },
                    "Period": cloud_watch_metric.period,
                    "Stat": cloud_watch_metric.statistics[0] if cloud_watch_metric.statistics else "Maximum",
                    "Unit": cloud_watch_metric.unit,
                },
                "ReturnData": True,
            }
        ]
        
        cw_metric = self._cw.get_metric_data(
            MetricDataQueries=metric_data_queries,
            StartTime=cloud_watch_metric.start_time,
            EndTime=cloud_watch_metric.end_time,
        )

        # Extract datapoints from the response
        metric_results = cw_metric.get("MetricDataResults", [])
        if metric_results:
            data_points = metric_results[0].get("Values", [])
            timestamps = metric_results[0].get("Timestamps", [])
            
            # Combine values and timestamps into the expected format
            combined_datapoints = []
            for i, (value, timestamp) in enumerate(zip(data_points, timestamps)):
                datapoint = {
                    "Timestamp": timestamp,
                    cloud_watch_metric.statistics[0] if cloud_watch_metric.statistics else "Maximum": value,
                    "Unit": cloud_watch_metric.unit,
                }
                combined_datapoints.append(datapoint)
            
            return combined_datapoints
        
        return []
