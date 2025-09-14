import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from src.core.aws.resource_handlers.ebs import EbsResourceHandlers
from tests.aws.resource_handlers.mock import mock_volume_response


class TestEbsResourceHandlers(unittest.TestCase):
    def setUp(self):
        self.region_name = "us-east-1"
        self.ebs_handler = EbsResourceHandlers(self.region_name)

    @patch("src.core.utils.AsyncClientManager")
    async def test_find_under_utilized_resource_with_volumes(self, mock_get_client):
        """Test find_under_utilized_resource with available volumes"""
        # Create a mock EC2 client
        mock_ec2_client = AsyncMock()
        mock_ec2_client.describe_volumes.return_value = mock_volume_response
        mock_get_client.return_value.__aenter__.return_value = mock_ec2_client

        # Create a new EbsResourceHandlers instance after mocking boto3
        ebs_handler = EbsResourceHandlers("us-east-1")
        unused_resources = await ebs_handler.find_under_utilized_resource()

        # Expected format based on the actual EbsResourceHandlers implementation
        expected_unused_resources = {
            "unused_ebs_volumes": [
                {
                    "VolumeId": "vol-0123456789abcdef0",
                    "Size": 8,
                    "State": "available",
                    "AvailabilityZone": "us-east-1a",
                    "CreateTime": "2023-10-01T12:34:56.000Z",
                },
                {
                    "VolumeId": "vol-0abcdef1234567890",
                    "Size": 20,
                    "State": "available",
                    "AvailabilityZone": "us-east-1b",
                    "CreateTime": "2023-11-15T08:22:10.000Z",
                },
            ]
        }

        # Verify the boto3 client was called correctly
        mock_ec2_client.describe_volumes.assert_called_once_with(Filters=[{"Name": "status", "Values": ["available"]}])

        self.assertEqual(expected_unused_resources, unused_resources)

    @patch("src.core.utils.AsyncClientManager")
    async def test_find_under_utilized_resource_empty_response(self, mock_get_client):
        """Test find_under_utilized_resource with empty response"""
        # Create a mock EC2 client
        mock_ec2_client = AsyncMock()
        mock_ec2_client.describe_volumes.return_value = {"Volumes": []}
        mock_get_client.return_value.__aenter__.return_value = mock_ec2_client

        # Create a new EbsResourceHandlers instance after mocking boto3
        ebs_handler = EbsResourceHandlers("us-east-1")
        unused_resources = await ebs_handler.find_under_utilized_resource()

        # Should return empty list
        self.assertEqual({"unused_ebs_volumes": []}, unused_resources)

    @patch("src.core.utils.AsyncClientManager")
    async def test_find_under_utilized_resource_api_error(self, mock_get_client):
        """Test find_under_utilized_resource when API call fails"""
        # Create a mock EC2 client
        mock_ec2_client = AsyncMock()
        mock_ec2_client.describe_volumes.side_effect = Exception("API Error")
        mock_get_client.return_value.__aenter__.return_value = mock_ec2_client

        # Create a new EbsResourceHandlers instance after mocking boto3
        ebs_handler = EbsResourceHandlers("us-east-1")

        # Should raise the exception
        with self.assertRaises(Exception) as context:
            await ebs_handler.find_under_utilized_resource()

        self.assertEqual("API Error", str(context.exception))
