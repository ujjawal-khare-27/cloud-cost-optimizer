import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

from src.core.aws.resource_handlers.cloudwatch import CloudWatch
from src.core.aws.resource_handlers.resource_handler import ResourceHandler
from src.core.utils import AsyncClientManager
from src.models.cloudwatch import CloudWatchMetric


class S3ResourceHandlers(ResourceHandler):
    def __init__(self, region_name: str):
        self.region_name = region_name
        self._client_manager = AsyncClientManager(region_name)
        self._cw = CloudWatch(region_name=region_name)

    async def _get_list(self):
        async with self._client_manager as manager:
            async with manager.get_client("s3") as s3:
                s3_list = await s3.list_buckets()
                return s3_list.get("Buckets", [])

    async def get_number_of_requests(self, bucket_name: str):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)

        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/S3",
            metric_name="NumberOfRequests",
            dimensions=[{"Name": "BucketName", "Value": bucket_name}],
            start_time=start_time,
            end_time=end_time,
            period=86400,
            statistics=["Sum"],
        )

        s3_metrics = await self._cw.get_metrics(cloudwatch_metric)

        return sum(metrics["Sum"] for metrics in s3_metrics["Datapoints"])

    async def get_bucket_size(self, bucket_name: str):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/S3",
            metric_name="BucketSizeBytes",
            dimensions=[
                {"Name": "BucketName", "Value": bucket_name},
                {"Name": "StorageType", "Value": "StandardStorage"},
            ],
            start_time=start_time,
            end_time=end_time,
            period=86400,
            statistics=["Average"],
        )

        s3_metrics = await self._cw.get_metrics(cloudwatch_metric)

        if s3_metrics["Datapoints"]:
            size_bytes = s3_metrics["Datapoints"][0]["Average"]
            size_gb = size_bytes / (1024 ** 3)
            return size_gb
        else:
            return None

    async def _get_s3_with_no_requests(self, s3_bucket_list: List[Dict]):
        buckets_with_no_requests = []
        requests_data = await asyncio.gather(*[self.get_number_of_requests(s3["Name"]) for s3 in s3_bucket_list])
        sizes = await asyncio.gather(*[self.get_bucket_size(s3["Name"]) for s3 in s3_bucket_list])

        for idx in range(len(s3_bucket_list)):
            if requests_data[idx] == 0:
                s3_details = s3_bucket_list[idx]
                s3_details["Size"] = sizes[idx]
                buckets_with_no_requests.append(s3_details)
        return buckets_with_no_requests

    async def find_under_utilized_resource(self):
        s3_list = await self._get_list()
        unused_s3 = await self._get_s3_with_no_requests(s3_list)

        return unused_s3
