import unittest
from unittest.mock import patch, AsyncMock

from src.core.aws.resource_handlers.s3 import S3ResourceHandlers
from tests.aws.resource_handlers.mock import (
    mock_s3_buckets_response,
    mock_s3_empty_response,
    mock_s3_requests_metrics_response,
    mock_s3_no_requests_metrics_response,
    mock_s3_bucket_size_metrics_response,
    mock_s3_bucket_size_empty_response,
)


class TestS3ResourceHandlers(unittest.TestCase):
    def setUp(self):
        self.region_name = "us-east-1"
        self.s3_handler = S3ResourceHandlers(self.region_name)

    def test_init(self):
        """Test S3ResourceHandlers initialization"""
        s3_handler = S3ResourceHandlers("us-west-2")

        # Verify region name is set
        self.assertEqual(s3_handler.region_name, "us-west-2")
        # Verify CloudWatch instance is created
        self.assertIsNotNone(s3_handler._cw)
        # Verify client manager is created
        self.assertIsNotNone(s3_handler._client_manager)

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_list_success(self, mock_get_client):
        """Test _get_list with successful response"""
        mock_s3_client = AsyncMock()
        mock_s3_client.list_buckets.return_value = mock_s3_buckets_response
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler._get_list()

        mock_s3_client.list_buckets.assert_called_once()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["Name"], "test-bucket-1")
        self.assertEqual(result[1]["Name"], "test-bucket-2")
        self.assertEqual(result[2]["Name"], "test-bucket-3")

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_list_empty_response(self, mock_get_client):
        """Test _get_list with empty response"""
        mock_s3_client = AsyncMock()
        mock_s3_client.list_buckets.return_value = mock_s3_empty_response
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler._get_list()

        mock_s3_client.list_buckets.assert_called_once()
        self.assertEqual(len(result), 0)

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_list_api_error(self, mock_get_client):
        """Test _get_list when API call fails"""
        mock_s3_client = AsyncMock()
        mock_s3_client.list_buckets.side_effect = Exception("S3 API Error")
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client

        s3_handler = S3ResourceHandlers("us-east-1")

        with self.assertRaises(Exception) as context:
            await s3_handler._get_list()

        self.assertEqual("S3 API Error", str(context.exception))

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_number_of_requests_success(self, mock_get_metrics):
        """Test get_number_of_requests with successful response"""
        mock_get_metrics.return_value = mock_s3_requests_metrics_response

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler.get_number_of_requests("test-bucket-1")

        # Should return sum of all Sum values: 100.0 + 50.0 + 25.0 = 175.0
        self.assertEqual(result, 175.0)

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_number_of_requests_no_requests(self, mock_get_metrics):
        """Test get_number_of_requests with no requests"""
        mock_get_metrics.return_value = mock_s3_no_requests_metrics_response

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler.get_number_of_requests("test-bucket-1")

        # Should return sum of all Sum values: 0.0 + 0.0 + 0.0 = 0.0
        self.assertEqual(result, 0.0)

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_number_of_requests_empty_response(self, mock_get_metrics):
        """Test get_number_of_requests with empty response"""
        mock_get_metrics.return_value = {"Datapoints": []}

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler.get_number_of_requests("test-bucket-1")

        # Should return 0 when no datapoints
        self.assertEqual(result, 0)

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_number_of_requests_cloudwatch_error(self, mock_get_metrics):
        """Test get_number_of_requests when CloudWatch fails"""
        mock_get_metrics.side_effect = Exception("CloudWatch Error")

        s3_handler = S3ResourceHandlers("us-east-1")

        with self.assertRaises(Exception) as context:
            await s3_handler.get_number_of_requests("test-bucket-1")

        self.assertEqual("CloudWatch Error", str(context.exception))

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_bucket_size_success(self, mock_get_metrics):
        """Test get_bucket_size with successful response"""
        mock_get_metrics.return_value = mock_s3_bucket_size_metrics_response

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler.get_bucket_size("test-bucket-1")

        # Should return size in GB: 1073741824 bytes / (1024^3) = 1.0 GB
        self.assertEqual(result, 1.0)

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_bucket_size_empty_response(self, mock_get_metrics):
        """Test get_bucket_size with empty response"""
        mock_get_metrics.return_value = mock_s3_bucket_size_empty_response

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler.get_bucket_size("test-bucket-1")

        # Should return None when no datapoints
        self.assertIsNone(result)

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_bucket_size_cloudwatch_error(self, mock_get_metrics):
        """Test get_bucket_size when CloudWatch fails"""
        mock_get_metrics.side_effect = Exception("CloudWatch Error")

        s3_handler = S3ResourceHandlers("us-east-1")

        with self.assertRaises(Exception) as context:
            await s3_handler.get_bucket_size("test-bucket-1")

        self.assertEqual("CloudWatch Error", str(context.exception))

    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_number_of_requests")
    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_bucket_size")
    async def test_get_s3_with_no_requests_success(self, mock_get_bucket_size, mock_get_requests):
        """Test _get_s3_with_no_requests with mixed results"""
        # Mock bucket list
        s3_bucket_list = [
            {"Name": "test-bucket-1", "CreationDate": "2023-10-01T12:34:56.000Z"},
            {"Name": "test-bucket-2", "CreationDate": "2023-11-15T08:22:10.000Z"},
            {"Name": "test-bucket-3", "CreationDate": "2023-12-01T15:45:30.000Z"},
        ]

        # Mock responses: first bucket has requests, second and third don't
        mock_get_requests.side_effect = [100.0, 0.0, 0.0]
        mock_get_bucket_size.side_effect = [1.5, 2.0, None]

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler._get_s3_with_no_requests(s3_bucket_list)

        # Should return only buckets with 0 requests
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Name"], "test-bucket-2")
        self.assertEqual(result[0]["Size"], 2.0)
        self.assertEqual(result[1]["Name"], "test-bucket-3")
        self.assertEqual(result[1]["Size"], None)

    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_number_of_requests")
    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_bucket_size")
    async def test_get_s3_with_no_requests_all_have_requests(self, mock_get_bucket_size, mock_get_requests):
        """Test _get_s3_with_no_requests when all buckets have requests"""
        # Mock bucket list
        s3_bucket_list = [
            {"Name": "test-bucket-1", "CreationDate": "2023-10-01T12:34:56.000Z"},
            {"Name": "test-bucket-2", "CreationDate": "2023-11-15T08:22:10.000Z"},
        ]

        # Mock responses: all buckets have requests
        mock_get_requests.side_effect = [100.0, 50.0]
        mock_get_bucket_size.side_effect = [1.5, 2.0]

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler._get_s3_with_no_requests(s3_bucket_list)

        # Should return empty list
        self.assertEqual(len(result), 0)

    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_number_of_requests")
    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_bucket_size")
    async def test_get_s3_with_no_requests_empty_list(self, mock_get_bucket_size, mock_get_requests):
        """Test _get_s3_with_no_requests with empty bucket list"""
        s3_bucket_list = []

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler._get_s3_with_no_requests(s3_bucket_list)

        # Should return empty list
        self.assertEqual(len(result), 0)
        # Should not call the mock methods
        mock_get_requests.assert_not_called()
        mock_get_bucket_size.assert_not_called()

    @patch("src.core.utils.AsyncClientManager")
    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_number_of_requests")
    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_bucket_size")
    async def test_find_under_utilized_resource_comprehensive(self, mock_get_bucket_size, mock_get_requests, mock_get_client):
        """Test find_under_utilized_resource with comprehensive scenario"""
        mock_s3_client = AsyncMock()
        mock_s3_client.list_buckets.return_value = mock_s3_buckets_response
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client

        # Mock responses: first bucket has requests, second and third don't
        mock_get_requests.side_effect = [100.0, 0.0, 0.0]
        mock_get_bucket_size.side_effect = [1.5, 2.0, 0.5]

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler.find_under_utilized_resource()

        # Should return only buckets with 0 requests
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Name"], "test-bucket-2")
        self.assertEqual(result[0]["Size"], 2.0)
        self.assertEqual(result[1]["Name"], "test-bucket-3")
        self.assertEqual(result[1]["Size"], 0.5)

    @patch("src.core.utils.AsyncClientManager")
    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_number_of_requests")
    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_bucket_size")
    async def test_find_under_utilized_resource_no_underutilized(self, mock_get_bucket_size, mock_get_requests, mock_get_client):
        """Test find_under_utilized_resource when no resources are underutilized"""
        mock_s3_client = AsyncMock()
        mock_s3_client.list_buckets.return_value = mock_s3_buckets_response
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client

        # Mock responses: all buckets have requests
        mock_get_requests.side_effect = [100.0, 50.0, 25.0]
        mock_get_bucket_size.side_effect = [1.5, 2.0, 0.5]

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler.find_under_utilized_resource()

        # Should return empty list
        self.assertEqual(len(result), 0)

    @patch("src.core.utils.AsyncClientManager")
    async def test_find_under_utilized_resource_empty_bucket_list(self, mock_get_client):
        """Test find_under_utilized_resource with empty bucket list"""
        mock_s3_client = AsyncMock()
        mock_s3_client.list_buckets.return_value = mock_s3_empty_response
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client

        s3_handler = S3ResourceHandlers("us-east-1")
        result = await s3_handler.find_under_utilized_resource()

        # Should return empty list
        self.assertEqual(len(result), 0)

    @patch("src.core.utils.AsyncClientManager")
    @patch("src.core.aws.resource_handlers.s3.S3ResourceHandlers.get_number_of_requests")
    async def test_find_under_utilized_resource_cloudwatch_error(self, mock_get_requests, mock_get_client):
        """Test find_under_utilized_resource when CloudWatch fails"""
        mock_s3_client = AsyncMock()
        mock_s3_client.list_buckets.return_value = mock_s3_buckets_response
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client

        # Mock CloudWatch error
        mock_get_requests.side_effect = Exception("CloudWatch Error")

        s3_handler = S3ResourceHandlers("us-east-1")

        with self.assertRaises(Exception) as context:
            await s3_handler.find_under_utilized_resource()

        self.assertEqual("CloudWatch Error", str(context.exception))

    @patch("src.core.utils.AsyncClientManager")
    async def test_find_under_utilized_resource_s3_api_error(self, mock_get_client):
        """Test find_under_utilized_resource when S3 API fails"""
        mock_s3_client = AsyncMock()
        mock_s3_client.list_buckets.side_effect = Exception("S3 API Error")
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client

        s3_handler = S3ResourceHandlers("us-east-1")

        with self.assertRaises(Exception) as context:
            await s3_handler.find_under_utilized_resource()

        self.assertEqual("S3 API Error", str(context.exception))

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_number_of_requests_with_missing_sum(self, mock_get_metrics):
        """Test get_number_of_requests when datapoints don't have Sum key"""
        # Mock response without Sum key
        mock_get_metrics.return_value = {
            "Datapoints": [
                {"Timestamp": "2023-10-01T12:00:00.000Z", "Average": 2.0},
                {"Timestamp": "2023-10-01T12:10:00.000Z", "Maximum": 1.0},
            ]
        }

        s3_handler = S3ResourceHandlers("us-east-1")

        with self.assertRaises(KeyError):
            await s3_handler.get_number_of_requests("test-bucket-1")

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_bucket_size_with_missing_average(self, mock_get_metrics):
        """Test get_bucket_size when datapoints don't have Average key"""
        # Mock response without Average key
        mock_get_metrics.return_value = {
            "Datapoints": [
                {"Timestamp": "2023-10-01T12:00:00.000Z", "Sum": 2.0},
                {"Timestamp": "2023-10-01T12:10:00.000Z", "Maximum": 1.0},
            ]
        }

        s3_handler = S3ResourceHandlers("us-east-1")

        with self.assertRaises(KeyError):
            await s3_handler.get_bucket_size("test-bucket-1")