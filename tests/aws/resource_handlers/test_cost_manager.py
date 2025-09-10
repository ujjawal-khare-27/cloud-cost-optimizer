import unittest
from unittest.mock import patch, MagicMock

from src.core.aws.cost_manager import AwsCostManager
from tests.aws.resource_handlers.mock import mock_volume_response


class TestAwsCostManager(unittest.TestCase):
    def setUp(self):
        self._aws_cost_manager = AwsCostManager("us-east-1")

    @patch("src.core.aws.resource_handlers.ebs_resource_handlers.boto3.client")
    def test_aws_cost_manager(self, mock_boto3_client):
        # Create a mock EC2 client
        mock_ec2_client = MagicMock()
        mock_boto3_client.return_value = mock_ec2_client

        # Mock the describe_volumes response
        mock_ec2_client.describe_volumes.return_value = mock_volume_response

        # Create a new AwsCostManager instance after mocking boto3
        aws_cost_manager = AwsCostManager("us-east-1")
        unused_resources = aws_cost_manager.get_unused_resources(["ebs"])

        # Expected format based on the actual EbsResourceHandlers implementation
        expected_unused_resources = [
            {
                "VolumeId": "vol-0123456789abcdef0",
                "Size": 8,
                "State": "available",
                "AvailabilityZone": "us-east-1a",
                "CreateTime": "2023-10-01T12:34:56.000Z"
            },
            {
                "VolumeId": "vol-0abcdef1234567890",
                "Size": 20,
                "State": "available",
                "AvailabilityZone": "us-east-1b",
                "CreateTime": "2023-11-15T08:22:10.000Z"
            },
        ]

        # Verify the boto3 client was called correctly
        mock_boto3_client.assert_called_once_with("ec2", region_name="us-east-1")
        mock_ec2_client.describe_volumes.assert_called_once_with(
            Filters=[{"Name": "status", "Values": ["available"]}]
        )

        assert expected_unused_resources == unused_resources
