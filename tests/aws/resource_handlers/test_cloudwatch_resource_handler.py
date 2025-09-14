import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from src.core.aws.resource_handlers.cloudwatch import CloudWatch
from src.models.cloudwatch import CloudWatchMetric
from tests.aws.resource_handlers.mock import (
    mock_cloudwatch_metric_response,
    mock_cloudwatch_empty_response,
)


class TestCloudWatchResourceHandler(unittest.TestCase):
    def setUp(self):
        self.region_name = "us-east-1"
        self.cloudwatch = CloudWatch(self.region_name)

    def test_init(self):
        """Test CloudWatch initialization"""
        cloudwatch = CloudWatch("us-west-2")
        self.assertEqual(cloudwatch.region_name, "us-west-2")

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_metrics_success(self, mock_client_manager_class):
        """Test get_metrics with successful response"""
        # Mock the AsyncClientManager instance
        mock_client_manager = AsyncMock()
        mock_client_manager_class.return_value = mock_client_manager
        
        # Mock the get_client context manager
        mock_cw_client = AsyncMock()
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_metric_response
        mock_client_manager.get_client.return_value.__aenter__.return_value = mock_cw_client

        # Create CloudWatch instance after mocking
        cloudwatch = CloudWatch("us-east-1")

        # Create test metric
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=120)

        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/RDS",
            metric_name="DatabaseConnections",
            dimensions=[{"Name": "DBInstanceIdentifier", "Value": "test-db"}],
            start_time=start_time,
            end_time=end_time,
            period=600,
            statistics=["Maximum"],
            unit="Count",
        )

        result = await cloudwatch.get_metrics(cloudwatch_metric)

        # Verify the call was made correctly
        expected_metric_data_queries = [
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/RDS",
                        "MetricName": "DatabaseConnections",
                        "Dimensions": [{"Name": "DBInstanceIdentifier", "Value": "test-db"}],
                    },
                    "Period": 600,
                    "Stat": "Maximum",
                    "Unit": "Count",
                },
                "ReturnData": True,
            }
        ]

        mock_cw_client.get_metric_data.assert_called_once_with(
            MetricDataQueries=expected_metric_data_queries,
            StartTime=start_time,
            EndTime=end_time,
        )

        # Verify the result
        expected_datapoints = [
            {"Timestamp": "2023-10-01T12:00:00.000Z", "Maximum": 5.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:10:00.000Z", "Maximum": 3.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:20:00.000Z", "Maximum": 0.0, "Unit": "Count"},
        ]
        self.assertEqual(result, expected_datapoints)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["Maximum"], 5.0)

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_metrics_empty_response(self, mock_client_manager_class):
        """Test get_metrics with empty response"""
        # Mock the AsyncClientManager instance
        mock_client_manager = AsyncMock()
        mock_client_manager_class.return_value = mock_client_manager
        
        # Mock the get_client context manager
        mock_cw_client = AsyncMock()
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_empty_response
        mock_client_manager.get_client.return_value.__aenter__.return_value = mock_cw_client

        cloudwatch = CloudWatch("us-east-1")

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=120)

        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/RDS",
            metric_name="DatabaseConnections",
            dimensions=[{"Name": "DBInstanceIdentifier", "Value": "test-db"}],
            start_time=start_time,
            end_time=end_time,
        )

        result = await cloudwatch.get_metrics(cloudwatch_metric)

        self.assertEqual(result, [])
        mock_cw_client.get_metric_data.assert_called_once()

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_metrics_api_error(self, mock_get_client):
        """Test get_metrics when API call fails"""
        mock_cw_client = AsyncMock()
        mock_cw_client.get_metric_data.side_effect = Exception("CloudWatch API Error")
        mock_get_client.return_value.__aenter__.return_value = mock_cw_client

        cloudwatch = CloudWatch("us-east-1")

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=120)

        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/RDS",
            metric_name="DatabaseConnections",
            dimensions=[{"Name": "DBInstanceIdentifier", "Value": "test-db"}],
            start_time=start_time,
            end_time=end_time,
        )

        with self.assertRaises(Exception) as context:
            await cloudwatch.get_metrics(cloudwatch_metric)

        self.assertEqual("CloudWatch API Error", str(context.exception))

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_metrics_with_default_values(self, mock_get_client):
        """Test get_metrics with default CloudWatchMetric values"""
        mock_cw_client = AsyncMock()
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_metric_response
        mock_get_client.return_value.__aenter__.return_value = mock_cw_client

        cloudwatch = CloudWatch("us-east-1")

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=120)

        # Create metric with minimal required fields (defaults will be used)
        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions=[{"Name": "InstanceId", "Value": "i-1234567890abcdef0"}],
            start_time=start_time,
            end_time=end_time,
        )

        result = await cloudwatch.get_metrics(cloudwatch_metric)

        # Verify default values are used
        expected_metric_data_queries = [
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/EC2",
                        "MetricName": "CPUUtilization",
                        "Dimensions": [{"Name": "InstanceId", "Value": "i-1234567890abcdef0"}],
                    },
                    "Period": 600,  # Default period
                    "Stat": "Maximum",  # Default statistics
                    "Unit": "Count",  # Default unit
                },
                "ReturnData": True,
            }
        ]

        mock_cw_client.get_metric_data.assert_called_once_with(
            MetricDataQueries=expected_metric_data_queries,
            StartTime=start_time,
            EndTime=end_time,
        )

        expected_datapoints = [
            {"Timestamp": "2023-10-01T12:00:00.000Z", "Maximum": 5.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:10:00.000Z", "Maximum": 3.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:20:00.000Z", "Maximum": 0.0, "Unit": "Count"},
        ]
        self.assertEqual(result, expected_datapoints)

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_metrics_missing_datapoints(self, mock_get_client):
        """Test get_metrics when response doesn't contain MetricDataResults key"""
        mock_cw_client = AsyncMock()
        mock_get_client.return_value.__aenter__.return_value = mock_cw_client

        # Response without MetricDataResults key
        response_without_results = {
            "ResponseMetadata": {"RequestId": "12345678-90ab-cdef-1234-567890abcdef", "HTTPStatusCode": 200}
        }
        mock_cw_client.get_metric_data.return_value = response_without_results

        cloudwatch = CloudWatch("us-east-1")

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=120)

        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/RDS",
            metric_name="DatabaseConnections",
            dimensions=[{"Name": "DBInstanceIdentifier", "Value": "test-db"}],
            start_time=start_time,
            end_time=end_time,
        )

        result = await cloudwatch.get_metrics(cloudwatch_metric)

        # Should return empty list when MetricDataResults key is missing
        self.assertEqual(result, [])

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_metrics_multiple_dimensions(self, mock_get_client):
        """Test get_metrics with multiple dimensions"""
        mock_cw_client = AsyncMock()
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_metric_response
        mock_get_client.return_value.__aenter__.return_value = mock_cw_client

        cloudwatch = CloudWatch("us-east-1")

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=120)

        cloudwatch_metric = CloudWatchMetric(
            namespace="AWS/ELB",
            metric_name="RequestCount",
            dimensions=[
                {"Name": "LoadBalancerName", "Value": "test-lb"},
                {"Name": "AvailabilityZone", "Value": "us-east-1a"},
            ],
            start_time=start_time,
            end_time=end_time,
            period=300,
            statistics=["Sum", "Average"],
            unit="Count",
        )

        result = await cloudwatch.get_metrics(cloudwatch_metric)

        # Verify multiple dimensions are passed correctly
        expected_metric_data_queries = [
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/ELB",
                        "MetricName": "RequestCount",
                        "Dimensions": [
                            {"Name": "LoadBalancerName", "Value": "test-lb"},
                            {"Name": "AvailabilityZone", "Value": "us-east-1a"},
                        ],
                    },
                    "Period": 300,
                    "Stat": "Sum",  # First statistic from the list
                    "Unit": "Count",
                },
                "ReturnData": True,
            }
        ]

        mock_cw_client.get_metric_data.assert_called_once_with(
            MetricDataQueries=expected_metric_data_queries,
            StartTime=start_time,
            EndTime=end_time,
        )

        expected_datapoints = [
            {"Timestamp": "2023-10-01T12:00:00.000Z", "Sum": 5.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:10:00.000Z", "Sum": 3.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:20:00.000Z", "Sum": 0.0, "Unit": "Count"},
        ]
        self.assertEqual(result, expected_datapoints)
