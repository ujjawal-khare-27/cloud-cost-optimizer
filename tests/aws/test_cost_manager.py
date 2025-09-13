import unittest
from unittest.mock import patch, MagicMock

from src.core.aws.cost_manager import AwsCostManager
from tests.aws.resource_handlers.mock import (
    mock_volume_response,
    mock_lb_response,
    mock_rds_instances_response,
    mock_cloudwatch_metric_response,
    mock_cloudwatch_empty_response,
    mock_lb_health_response_all_unhealthy,
    mock_lb_health_response_healthy,
)


class TestAwsCostManager(unittest.TestCase):
    def setUp(self):
        self._aws_cost_manager = AwsCostManager("us-east-1")

    @patch("src.core.utils.boto3.client")
    def test_aws_cost_manager_ebs(self, mock_boto3_client):
        # Create a mock EC2 client
        mock_ec2_client = MagicMock()
        mock_boto3_client.return_value = mock_ec2_client

        # Mock the describe_volumes response
        mock_ec2_client.describe_volumes.return_value = mock_volume_response

        # Create a new AwsCostManager instance after mocking boto3
        aws_cost_manager = AwsCostManager("us-east-1")
        unused_resources = aws_cost_manager.get_unused_resources(["ebs"])

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

        mock_ec2_client.describe_volumes.assert_called_once_with(Filters=[{"Name": "status", "Values": ["available"]}])

        assert expected_unused_resources == unused_resources[0].get("ebs")

    @patch("src.core.utils.boto3.client")
    def test_aws_cost_manager_lb(self, mock_boto3_client):
        # Create a mock ELB client
        mock_elb_client = MagicMock()
        mock_boto3_client.return_value = mock_elb_client

        # Mock the describe_load_balancers response
        mock_elb_client.describe_load_balancers.return_value = mock_lb_response

        # Mock health check responses - first call for test-lb-all-unhealthy, second for test-lb-healthy
        mock_elb_client.describe_instance_health.side_effect = [
            mock_lb_health_response_all_unhealthy,  # For test-lb-all-unhealthy
            mock_lb_health_response_healthy,  # For test-lb-healthy
        ]

        # Create a new AwsCostManager instance after mocking boto3
        aws_cost_manager = AwsCostManager("us-east-1")
        unused_resources = aws_cost_manager.get_unused_resources(["lb"])

        # Verify the result structure
        self.assertEqual(len(unused_resources), 1)
        self.assertIn("lb", unused_resources[0])

        lb_result = unused_resources[0]["lb"]
        self.assertIn("no_targets_lb", lb_result)
        self.assertIn("all_unhealthy", lb_result)

        # Verify we found the expected load balancers
        self.assertEqual(len(lb_result["no_targets_lb"]), 1)
        self.assertEqual(len(lb_result["all_unhealthy"]), 1)

        # Verify the specific load balancers found
        self.assertEqual(lb_result["no_targets_lb"][0]["LoadBalancerName"], "test-lb-no-targets")
        self.assertEqual(lb_result["all_unhealthy"][0]["LoadBalancerName"], "test-lb-all-unhealthy")

        # Verify the ELB client was called correctly
        mock_elb_client.describe_load_balancers.assert_called_once()
        mock_elb_client.describe_instance_health.assert_called()

    @patch("src.core.utils.boto3.client")
    def test_aws_cost_manager_rds(self, mock_boto3_client):
        """Test AwsCostManager with RDS service"""
        # Create mock clients for RDS and CloudWatch
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client, mock_rds_client, mock_cw_client]

        # Mock the describe_db_instances response
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response

        # Mock CloudWatch responses - first cluster has no connections, second has connections
        mock_cw_client.get_metric_data.side_effect = [
            mock_cloudwatch_empty_response,  # cluster1 has no connections
            mock_cloudwatch_metric_response,  # cluster2 has connections
            mock_cloudwatch_empty_response,  # cluster1 has no connections (duplicate call)
            mock_cloudwatch_metric_response,  # cluster2 has connections (duplicate call)
        ]

        # Create a new AwsCostManager instance after mocking boto3
        aws_cost_manager = AwsCostManager("us-east-1")
        unused_resources = aws_cost_manager.get_unused_resources(["rds"])

        mock_rds_client.describe_db_instances.assert_called_once()

        # Verify the result structure
        self.assertEqual(len(unused_resources), 1)
        self.assertIn("rds", unused_resources[0])

        rds_result = unused_resources[0]["rds"]
        self.assertIn("rds_with_no_connections", rds_result)
        self.assertIn("rds_instances_with_no_connections", rds_result)

        # Verify that we found the RDS instance with no connections
        self.assertEqual(len(rds_result["rds_with_no_connections"]), 1)
        self.assertEqual(len(rds_result["rds_instances_with_no_connections"]), 1)
        self.assertEqual(rds_result["rds_with_no_connections"][0]["DBInstanceIdentifier"], "test-db-instance-1")
        self.assertEqual(
            rds_result["rds_instances_with_no_connections"][0]["DBInstanceIdentifier"], "test-db-instance-1"
        )

    @patch("src.core.utils.boto3.client")
    def test_aws_cost_manager_rds_no_underutilized(self, mock_boto3_client):
        """Test AwsCostManager with RDS service when no resources are underutilized"""
        # Create mock clients for RDS and CloudWatch
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client, mock_rds_client, mock_cw_client]

        # Mock the describe_db_instances response
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response

        # Mock CloudWatch responses - all clusters have connections
        mock_cw_client.get_metric_data.side_effect = [
            mock_cloudwatch_metric_response,  # cluster1 has connections
            mock_cloudwatch_metric_response,  # cluster2 has connections
            mock_cloudwatch_metric_response,  # cluster1 has connections (duplicate call)
            mock_cloudwatch_metric_response,  # cluster2 has connections (duplicate call)
        ]

        # Create a new AwsCostManager instance after mocking boto3
        aws_cost_manager = AwsCostManager("us-east-1")
        unused_resources = aws_cost_manager.get_unused_resources(["rds"])

        # Verify the result structure
        self.assertEqual(len(unused_resources), 1)
        self.assertIn("rds", unused_resources[0])

        rds_result = unused_resources[0]["rds"]
        self.assertIn("rds_with_no_connections", rds_result)
        self.assertIn("rds_instances_with_no_connections", rds_result)

        # Verify that no underutilized resources were found
        self.assertEqual(len(rds_result["rds_with_no_connections"]), 0)
        self.assertEqual(len(rds_result["rds_instances_with_no_connections"]), 0)

    @patch("src.core.utils.boto3.client")
    def test_aws_cost_manager_multiple_services(self, mock_boto3_client):
        """Test AwsCostManager with multiple services including RDS"""
        # Create mock clients
        mock_ec2_client = MagicMock()
        mock_elb_client = MagicMock()
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [
            mock_ec2_client,
            mock_elb_client,
            mock_rds_client,
            mock_cw_client,
            mock_rds_client,
            mock_cw_client,
        ]

        # Mock responses
        mock_ec2_client.describe_volumes.return_value = mock_volume_response
        mock_elb_client.describe_load_balancers.return_value = mock_lb_response
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response
        mock_cw_client.get_metric_data.side_effect = [
            mock_cloudwatch_empty_response,  # cluster1 has no connections
            mock_cloudwatch_metric_response,  # cluster2 has connections
            mock_cloudwatch_empty_response,  # cluster1 has no connections (duplicate call)
            mock_cloudwatch_metric_response,  # cluster2 has connections (duplicate call)
        ]

        # Create a new AwsCostManager instance after mocking boto3
        aws_cost_manager = AwsCostManager("us-east-1")
        unused_resources = aws_cost_manager.get_unused_resources(["ebs", "lb", "rds"])

        # Verify we get results for all three services
        self.assertEqual(len(unused_resources), 3)

        # Check that all services are present
        service_names = [list(result.keys())[0] for result in unused_resources]
        self.assertIn("ebs", service_names)
        self.assertIn("lb", service_names)
        self.assertIn("rds", service_names)
