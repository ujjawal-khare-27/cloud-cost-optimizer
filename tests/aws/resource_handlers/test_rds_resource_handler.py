import unittest
from unittest.mock import patch, AsyncMock

from src.core.aws.resource_handlers.rds import RdsHandler
from tests.aws.resource_handlers.mock import (
    mock_rds_instances_response,
    mock_rds_empty_response,
)


class TestRdsResourceHandler(unittest.TestCase):
    def setUp(self):
        self.region_name = "us-east-1"
        self.rds_handler = RdsHandler(self.region_name)

    def test_init(self):
        """Test RdsHandler initialization"""
        rds_handler = RdsHandler("us-west-2")

        # Verify region name is set
        self.assertEqual(rds_handler.region_name, "us-west-2")
        # Verify CloudWatch instance is created
        self.assertIsNotNone(rds_handler._cw)

    @patch("src.core.utils.AsyncClientManager")
    async def test_list_get_success(self, mock_get_client):
        """Test _list_get with successful response"""
        mock_rds_client = AsyncMock()
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response
        mock_get_client.return_value.__aenter__.return_value = mock_rds_client

        rds_handler = RdsHandler("us-east-1")
        result = await rds_handler._list_get()

        mock_rds_client.describe_db_instances.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["DBInstanceIdentifier"], "test-db-instance-1")
        self.assertEqual(result[1]["DBInstanceIdentifier"], "test-db-instance-2")

    @patch("src.core.utils.AsyncClientManager")
    async def test_list_get_api_error(self, mock_get_client):
        """Test _list_get when API call fails"""
        mock_rds_client = AsyncMock()
        mock_rds_client.describe_db_instances.side_effect = Exception("RDS API Error")
        mock_get_client.return_value.__aenter__.return_value = mock_rds_client

        rds_handler = RdsHandler("us-east-1")

        with self.assertRaises(Exception) as context:
            await rds_handler._list_get()

        self.assertEqual("RDS API Error", str(context.exception))

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_max_connection_for_instance_success(self, mock_get_metrics):
        """Test _get_max_connection_for_instance with successful response"""
        mock_get_metrics.return_value = [
            {"Timestamp": "2023-10-01T12:00:00.000Z", "Maximum": 5.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:10:00.000Z", "Maximum": 3.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:20:00.000Z", "Maximum": 0.0, "Unit": "Count"},
        ]

        rds_handler = RdsHandler("us-east-1")
        result = await rds_handler._get_max_connection_for_instance("test-db-instance-1")

        # Should return the maximum value from the datapoints
        self.assertEqual(result, 5.0)  # Maximum value from mock response

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_max_connection_for_instance_empty_response(self, mock_get_metrics):
        """Test _get_max_connection_for_instance with empty response"""
        mock_get_metrics.return_value = []

        rds_handler = RdsHandler("us-east-1")
        result = await rds_handler._get_max_connection_for_instance("test-db-instance-1")

        # Should return 0 when no datapoints
        self.assertEqual(result, 0)

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_max_connections_for_cluster_success(self, mock_get_metrics):
        """Test _get_max_connections_for_cluster with successful response"""
        mock_get_metrics.return_value = [
            {"Timestamp": "2023-10-01T12:00:00.000Z", "Maximum": 5.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:10:00.000Z", "Maximum": 3.0, "Unit": "Count"},
            {"Timestamp": "2023-10-01T12:20:00.000Z", "Maximum": 0.0, "Unit": "Count"},
        ]

        rds_handler = RdsHandler("us-east-1")
        result = await rds_handler._get_max_connections_for_cluster("test-cluster-1")

        # Should return the maximum value from the datapoints
        self.assertEqual(result, 5.0)

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_rds_with_no_connections(self, mock_get_metrics):
        """Test _get_rds_with_no_connections method"""
        # Mock CloudWatch responses - first cluster has connections, second doesn't
        mock_get_metrics.side_effect = [
            [{"Maximum": 5.0}],  # First cluster has connections
            [],  # Second cluster has no connections
        ]

        rds_handler = RdsHandler("us-east-1")

        rds_list = [
            {"DBInstanceIdentifier": "db1", "DBClusterIdentifier": "cluster1"},
            {"DBInstanceIdentifier": "db2", "DBClusterIdentifier": "cluster2"},
        ]

        result = await rds_handler._get_rds_with_no_connections(rds_list)

        # Should only return the RDS instance with no connections
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["DBInstanceIdentifier"], "db2")

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_rds_instances_with_no_connections(self, mock_get_metrics):
        """Test _get_rds_instances_with_no_connections method"""
        # Mock CloudWatch responses - first instance has connections, second doesn't
        mock_get_metrics.side_effect = [
            [{"Maximum": 3.0}],  # First instance has connections
            [],  # Second instance has no connections
        ]

        rds_handler = RdsHandler("us-east-1")

        rds_list = [
            {"DBInstanceIdentifier": "db-instance-1"},
            {"DBInstanceIdentifier": "db-instance-2"},
        ]

        result = await rds_handler._get_rds_instances_with_no_connections(rds_list)

        # Should only return the RDS instance with no connections
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["DBInstanceIdentifier"], "db-instance-2")

    @patch("src.core.utils.AsyncClientManager")
    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_find_under_utilized_resource_comprehensive(self, mock_get_metrics, mock_get_client):
        """Test find_under_utilized_resource with comprehensive scenario"""
        mock_rds_client = AsyncMock()
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response
        mock_get_client.return_value.__aenter__.return_value = mock_rds_client

        # Mock CloudWatch responses for cluster connections
        mock_get_metrics.side_effect = [
            [],  # cluster1 has no connections
            [{"Maximum": 3.0}],  # cluster2 has connections
            [],  # cluster1 has no connections (duplicate call)
            [{"Maximum": 3.0}],  # cluster2 has connections (duplicate call)
        ]

        rds_handler = RdsHandler("us-east-1")
        result = await rds_handler.find_under_utilized_resource()

        # Verify the structure of the result
        self.assertIn("rds_with_no_connections", result)
        self.assertIn("rds_instances_with_no_connections", result)

        # Should find RDS instances with no connections
        self.assertEqual(len(result["rds_with_no_connections"]), 1)
        self.assertEqual(result["rds_with_no_connections"][0]["DBInstanceIdentifier"], "test-db-instance-1")

    @patch("src.core.utils.AsyncClientManager")
    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_find_under_utilized_resource_no_underutilized(self, mock_get_metrics, mock_get_client):
        """Test find_under_utilized_resource when no resources are underutilized"""
        mock_rds_client = AsyncMock()
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response
        mock_get_client.return_value.__aenter__.return_value = mock_rds_client

        # Mock CloudWatch responses - all clusters have connections
        mock_get_metrics.side_effect = [
            [{"Maximum": 3.0}],  # cluster1 has connections
            [{"Maximum": 5.0}],  # cluster2 has connections
            [{"Maximum": 3.0}],  # cluster1 has connections (duplicate call)
            [{"Maximum": 5.0}],  # cluster2 has connections (duplicate call)
        ]

        rds_handler = RdsHandler("us-east-1")
        result = await rds_handler.find_under_utilized_resource()

        # Should return empty lists
        self.assertEqual(result["rds_with_no_connections"], [])
        self.assertEqual(result["rds_instances_with_no_connections"], [])

    @patch("src.core.utils.AsyncClientManager")
    async def test_find_under_utilized_resource_empty_rds_list(self, mock_get_client):
        """Test find_under_utilized_resource with empty RDS list"""
        mock_rds_client = AsyncMock()
        mock_rds_client.describe_db_instances.return_value = mock_rds_empty_response
        mock_get_client.return_value.__aenter__.return_value = mock_rds_client

        rds_handler = RdsHandler("us-east-1")
        result = await rds_handler.find_under_utilized_resource()

        # Should return empty lists
        self.assertEqual(result["rds_with_no_connections"], [])
        self.assertEqual(result["rds_instances_with_no_connections"], [])

    @patch("src.core.utils.AsyncClientManager")
    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_find_under_utilized_resource_cloudwatch_error(self, mock_get_metrics, mock_get_client):
        """Test find_under_utilized_resource when CloudWatch fails"""
        mock_rds_client = AsyncMock()
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response
        mock_get_client.return_value.__aenter__.return_value = mock_rds_client

        # Mock CloudWatch error
        mock_get_metrics.side_effect = Exception("CloudWatch Error")

        rds_handler = RdsHandler("us-east-1")

        with self.assertRaises(Exception) as context:
            await rds_handler.find_under_utilized_resource()

        self.assertEqual("CloudWatch Error", str(context.exception))

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_max_connection_for_instance_with_missing_maximum(self, mock_get_metrics):
        """Test _get_max_connection_for_instance when datapoints don't have Maximum key"""
        # Mock response without Maximum key
        mock_get_metrics.return_value = [
            {"Timestamp": "2023-10-01T12:00:00.000Z", "Average": 2.0},
            {"Timestamp": "2023-10-01T12:10:00.000Z", "Sum": 1.0},
        ]

        rds_handler = RdsHandler("us-east-1")
        result = await rds_handler._get_max_connection_for_instance("test-db-instance-1")

        # Should return 0 when Maximum key is missing
        self.assertEqual(result, 0)

    @patch("src.core.aws.resource_handlers.cloudwatch.CloudWatch.get_metrics")
    async def test_get_max_connections_for_cluster_with_missing_maximum(self, mock_get_metrics):
        """Test _get_max_connections_for_cluster when datapoints don't have Maximum key"""
        # Mock response without Maximum key
        mock_get_metrics.return_value = [
            {"Timestamp": "2023-10-01T12:00:00.000Z", "Average": 2.0},
            {"Timestamp": "2023-10-01T12:10:00.000Z", "Sum": 1.0},
        ]

        rds_handler = RdsHandler("us-east-1")
        result = await rds_handler._get_max_connections_for_cluster("test-cluster-1")

        # Should return 0 when Maximum key is missing
        self.assertEqual(result, 0)
