import unittest
from unittest.mock import patch, MagicMock
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

    @patch("src.core.utils.boto3.client")
    def test_init(self, mock_boto3_client):
        """Test CloudWatch initialization"""
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client

        cloudwatch = CloudWatch("us-west-2")

        mock_boto3_client.assert_called_once_with("cloudwatch", region_name="us-west-2")
        self.assertEqual(cloudwatch._cw, mock_client)

    @patch("src.core.utils.boto3.client")
    def test_get_metrics_success(self, mock_boto3_client):
        """Test get_metrics with successful response"""
        mock_cw_client = MagicMock()
        mock_boto3_client.return_value = mock_cw_client
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_metric_response

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

        result = cloudwatch.get_metrics(cloudwatch_metric)

        # Verify the call was made correctly
        mock_cw_client.get_metric_data.assert_called_once_with(
            Namespace="AWS/RDS",
            MetricName="DatabaseConnections",
            Dimensions=[{"Name": "DBInstanceIdentifier", "Value": "test-db"}],
            StartTime=start_time,
            EndTime=end_time,
            Period=600,
            Statistics=["Maximum"],
            Unit="Count",
        )

        # Verify the result
        expected_datapoints = mock_cloudwatch_metric_response["Datapoints"]
        self.assertEqual(result, expected_datapoints)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["Maximum"], 5.0)

    @patch("src.core.utils.boto3.client")
    def test_get_metrics_empty_response(self, mock_boto3_client):
        """Test get_metrics with empty response"""
        mock_cw_client = MagicMock()
        mock_boto3_client.return_value = mock_cw_client
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_empty_response

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

        result = cloudwatch.get_metrics(cloudwatch_metric)

        self.assertEqual(result, [])
        mock_cw_client.get_metric_data.assert_called_once()

    @patch("src.core.utils.boto3.client")
    def test_get_metrics_api_error(self, mock_boto3_client):
        """Test get_metrics when API call fails"""
        mock_cw_client = MagicMock()
        mock_boto3_client.return_value = mock_cw_client
        mock_cw_client.get_metric_data.side_effect = Exception("CloudWatch API Error")

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
            cloudwatch.get_metrics(cloudwatch_metric)

        self.assertEqual("CloudWatch API Error", str(context.exception))

    @patch("src.core.utils.boto3.client")
    def test_get_metrics_with_default_values(self, mock_boto3_client):
        """Test get_metrics with default CloudWatchMetric values"""
        mock_cw_client = MagicMock()
        mock_boto3_client.return_value = mock_cw_client
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_metric_response

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

        result = cloudwatch.get_metrics(cloudwatch_metric)

        # Verify default values are used
        mock_cw_client.get_metric_data.assert_called_once_with(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": "i-1234567890abcdef0"}],
            StartTime=start_time,
            EndTime=end_time,
            Period=600,  # Default period
            Statistics=["Maximum"],  # Default statistics
            Unit="Count",  # Default unit
        )

        self.assertEqual(result, mock_cloudwatch_metric_response["Datapoints"])

    @patch("src.core.utils.boto3.client")
    def test_get_metrics_missing_datapoints(self, mock_boto3_client):
        """Test get_metrics when response doesn't contain Datapoints key"""
        mock_cw_client = MagicMock()
        mock_boto3_client.return_value = mock_cw_client

        # Response without Datapoints key
        response_without_datapoints = {
            "ResponseMetadata": {"RequestId": "12345678-90ab-cdef-1234-567890abcdef", "HTTPStatusCode": 200}
        }
        mock_cw_client.get_metric_data.return_value = response_without_datapoints

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

        result = cloudwatch.get_metrics(cloudwatch_metric)

        # Should return None when Datapoints key is missing
        self.assertIsNone(result)

    @patch("src.core.utils.boto3.client")
    def test_get_metrics_multiple_dimensions(self, mock_boto3_client):
        """Test get_metrics with multiple dimensions"""
        mock_cw_client = MagicMock()
        mock_boto3_client.return_value = mock_cw_client
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_metric_response

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

        result = cloudwatch.get_metrics(cloudwatch_metric)

        # Verify multiple dimensions are passed correctly
        expected_dimensions = [
            {"Name": "LoadBalancerName", "Value": "test-lb"},
            {"Name": "AvailabilityZone", "Value": "us-east-1a"},
        ]

        mock_cw_client.get_metric_data.assert_called_once_with(
            Namespace="AWS/ELB",
            MetricName="RequestCount",
            Dimensions=expected_dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=["Sum", "Average"],
            Unit="Count",
        )

        self.assertEqual(result, mock_cloudwatch_metric_response["Datapoints"])
