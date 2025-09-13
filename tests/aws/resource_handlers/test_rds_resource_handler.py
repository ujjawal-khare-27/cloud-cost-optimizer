import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.core.aws.resource_handlers.rds import RdsHandler
from src.models.cloudwatch import CloudWatchMetric
from tests.aws.resource_handlers.mock import (
    mock_rds_instances_response,
    mock_rds_empty_response,
    mock_cloudwatch_metric_response,
    mock_cloudwatch_empty_response,
)


class TestRdsResourceHandler(unittest.TestCase):
    def setUp(self):
        self.region_name = "us-east-1"
        self.rds_handler = RdsHandler(self.region_name)

    @patch("src.core.utils.boto3.client")
    def test_init(self, mock_boto3_client):
        """Test RdsHandler initialization"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]

        rds_handler = RdsHandler("us-west-2")

        # Verify both clients were created
        self.assertEqual(rds_handler._boto3, mock_rds_client)
        self.assertEqual(rds_handler._cw._cw, mock_cw_client)

    @patch("src.core.utils.boto3.client")
    def test_list_get_success(self, mock_boto3_client):
        """Test _list_get with successful response"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response

        rds_handler = RdsHandler("us-east-1")
        result = rds_handler._list_get()

        mock_rds_client.describe_db_instances.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["DBInstanceIdentifier"], "test-db-instance-1")
        self.assertEqual(result[1]["DBInstanceIdentifier"], "test-db-instance-2")

    @patch("src.core.utils.boto3.client")
    def test_list_get_api_error(self, mock_boto3_client):
        """Test _list_get when API call fails"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]
        mock_rds_client.describe_db_instances.side_effect = Exception("RDS API Error")

        rds_handler = RdsHandler("us-east-1")

        with self.assertRaises(Exception) as context:
            rds_handler._list_get()

        self.assertEqual("RDS API Error", str(context.exception))

    @patch("src.core.utils.boto3.client")
    def test_get_max_connection_for_instance_success(self, mock_boto3_client):
        """Test _get_max_connection_for_instance with successful response"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_metric_response

        rds_handler = RdsHandler("us-east-1")
        result = rds_handler._get_max_connection_for_instance("test-db-instance-1")

        # Verify CloudWatch was called with correct parameters
        mock_cw_client.get_metric_data.assert_called_once()
        call_args = mock_cw_client.get_metric_data.call_args

        # Check the metric parameters
        self.assertEqual(call_args[1]["Namespace"], "AWS/RDS")
        self.assertEqual(call_args[1]["Dimensions"], [{"Name": "DBInstanceIdentifier", "Value": "test-db-instance-1"}])

        # Should return the maximum value from the datapoints
        self.assertEqual(result, 5.0)  # Maximum value from mock_cloudwatch_metric_response

    @patch("src.core.utils.boto3.client")
    def test_get_max_connection_for_instance_empty_response(self, mock_boto3_client):
        """Test _get_max_connection_for_instance with empty response"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_empty_response

        rds_handler = RdsHandler("us-east-1")
        result = rds_handler._get_max_connection_for_instance("test-db-instance-1")

        # Should return 0 when no datapoints
        self.assertEqual(result, 0)

    @patch("src.core.utils.boto3.client")
    def test_get_max_connections_for_cluster_success(self, mock_boto3_client):
        """Test _get_max_connections_for_cluster with successful response"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]
        mock_cw_client.get_metric_data.return_value = mock_cloudwatch_metric_response

        rds_handler = RdsHandler("us-east-1")
        result = rds_handler._get_max_connections_for_cluster("test-cluster-1")

        # Verify CloudWatch was called with correct parameters
        mock_cw_client.get_metric_data.assert_called_once()
        call_args = mock_cw_client.get_metric_data.call_args

        # Check the metric parameters
        self.assertEqual(call_args[1]["Namespace"], "AWS/RDS")
        self.assertEqual(call_args[1]["MetricName"], "DatabaseConnections")
        self.assertEqual(call_args[1]["Dimensions"], [{"Name": "DBClusterIdentifier", "Value": "test-cluster-1"}])

        # Should return the maximum value from the datapoints
        self.assertEqual(result, 5.0)

    @patch("src.core.utils.boto3.client")
    def test_get_rds_with_no_connections(self, mock_boto3_client):
        """Test _get_rds_with_no_connections method"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]

        # Mock CloudWatch responses - first cluster has connections, second doesn't
        mock_cw_client.get_metric_data.side_effect = [
            {"Datapoints": [{"Maximum": 5.0}]},  # First cluster has connections
            {"Datapoints": [{"Maximum": 0.0}]},  # Second cluster has no connections
        ]

        rds_handler = RdsHandler("us-east-1")

        rds_list = [
            {"DBInstanceIdentifier": "db1", "DBClusterIdentifier": "cluster1"},
            {"DBInstanceIdentifier": "db2", "DBClusterIdentifier": "cluster2"},
        ]

        result = rds_handler._get_rds_with_no_connections(rds_list)

        # Should only return the RDS instance with no connections
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["DBInstanceIdentifier"], "db2")

    @patch("src.core.utils.boto3.client")
    def test_get_rds_instances_with_no_connections(self, mock_boto3_client):
        """Test _get_rds_instances_with_no_connections method"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]

        # Mock CloudWatch responses - first instance has connections, second doesn't
        mock_cw_client.get_metric_data.side_effect = [
            {"Datapoints": [{"Maximum": 3.0}]},  # First instance has connections
            {"Datapoints": [{"Maximum": 0.0}]},  # Second instance has no connections
        ]

        rds_handler = RdsHandler("us-east-1")

        rds_list = [
            {"DBInstanceIdentifier": "db-instance-1"},
            {"DBInstanceIdentifier": "db-instance-2"},
        ]

        result = rds_handler._get_rds_instances_with_no_connections(rds_list)

        # Should only return the RDS instance with no connections
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["DBInstanceIdentifier"], "db-instance-2")

    @patch("src.core.utils.boto3.client")
    def test_find_under_utilized_resource_comprehensive(self, mock_boto3_client):
        """Test find_under_utilized_resource with comprehensive scenario"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]

        # Mock RDS describe_db_instances response
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response

        # Mock CloudWatch responses for cluster connections
        mock_cw_client.get_metric_data.side_effect = [
            {"Datapoints": [{"Maximum": 0.0}]},  # cluster1 has no connections
            {"Datapoints": [{"Maximum": 5.0}]},  # cluster2 has connections
            {"Datapoints": [{"Maximum": 0.0}]},  # cluster1 has no connections (duplicate call)
            {"Datapoints": [{"Maximum": 5.0}]},  # cluster2 has connections (duplicate call)
        ]

        rds_handler = RdsHandler("us-east-1")
        result = rds_handler.find_under_utilized_resource()

        # Verify the structure of the result
        self.assertIn("rds_with_no_connections", result)
        self.assertIn("rds_instances_with_no_connections", result)

        # Should find RDS instances with no connections
        self.assertEqual(len(result["rds_with_no_connections"]), 1)
        self.assertEqual(result["rds_with_no_connections"][0]["DBInstanceIdentifier"], "test-db-instance-1")

    @patch("src.core.utils.boto3.client")
    def test_find_under_utilized_resource_no_underutilized(self, mock_boto3_client):
        """Test find_under_utilized_resource when no resources are underutilized"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]

        # Mock RDS describe_db_instances response
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response

        # Mock CloudWatch responses - all clusters have connections
        mock_cw_client.get_metric_data.side_effect = [
            {"Datapoints": [{"Maximum": 5.0}]},  # cluster1 has connections
            {"Datapoints": [{"Maximum": 3.0}]},  # cluster2 has connections
            {"Datapoints": [{"Maximum": 5.0}]},  # cluster1 has connections (duplicate call)
            {"Datapoints": [{"Maximum": 3.0}]},  # cluster2 has connections (duplicate call)
        ]

        rds_handler = RdsHandler("us-east-1")
        result = rds_handler.find_under_utilized_resource()

        # Should return empty lists
        self.assertEqual(result["rds_with_no_connections"], [])
        self.assertEqual(result["rds_instances_with_no_connections"], [])

    @patch("src.core.utils.boto3.client")
    def test_find_under_utilized_resource_empty_rds_list(self, mock_boto3_client):
        """Test find_under_utilized_resource with empty RDS list"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]

        # Mock empty RDS response
        mock_rds_client.describe_db_instances.return_value = mock_rds_empty_response

        rds_handler = RdsHandler("us-east-1")
        result = rds_handler.find_under_utilized_resource()

        # Should return empty lists
        self.assertEqual(result["rds_with_no_connections"], [])
        self.assertEqual(result["rds_instances_with_no_connections"], [])

        # CloudWatch should not be called when no RDS instances
        mock_cw_client.get_metric_data.assert_not_called()

    @patch("src.core.utils.boto3.client")
    def test_find_under_utilized_resource_cloudwatch_error(self, mock_boto3_client):
        """Test find_under_utilized_resource when CloudWatch fails"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]

        # Mock RDS describe_db_instances response
        mock_rds_client.describe_db_instances.return_value = mock_rds_instances_response

        # Mock CloudWatch error
        mock_cw_client.get_metric_data.side_effect = Exception("CloudWatch Error")

        rds_handler = RdsHandler("us-east-1")

        with self.assertRaises(Exception) as context:
            rds_handler.find_under_utilized_resource()

        self.assertEqual("CloudWatch Error", str(context.exception))

    @patch("src.core.utils.boto3.client")
    def test_get_max_connection_for_instance_with_missing_maximum(self, mock_boto3_client):
        """Test _get_max_connection_for_instance when datapoints don't have Maximum key"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]

        # Mock response without Maximum key
        response_without_maximum = {
            "Datapoints": [
                {"Timestamp": "2023-10-01T12:00:00.000Z", "Average": 2.0},
                {"Timestamp": "2023-10-01T12:10:00.000Z", "Sum": 1.0},
            ]
        }
        mock_cw_client.get_metric_data.return_value = response_without_maximum

        rds_handler = RdsHandler("us-east-1")
        result = rds_handler._get_max_connection_for_instance("test-db-instance-1")

        # Should return 0 when Maximum key is missing
        self.assertEqual(result, 0)

    @patch("src.core.utils.boto3.client")
    def test_get_max_connections_for_cluster_with_missing_maximum(self, mock_boto3_client):
        """Test _get_max_connections_for_cluster when datapoints don't have Maximum key"""
        mock_rds_client = MagicMock()
        mock_cw_client = MagicMock()
        mock_boto3_client.side_effect = [mock_rds_client, mock_cw_client]

        # Mock response without Maximum key
        response_without_maximum = {
            "Datapoints": [
                {"Timestamp": "2023-10-01T12:00:00.000Z", "Average": 2.0},
                {"Timestamp": "2023-10-01T12:10:00.000Z", "Sum": 1.0},
            ]
        }
        mock_cw_client.get_metric_data.return_value = response_without_maximum

        rds_handler = RdsHandler("us-east-1")
        result = rds_handler._get_max_connections_for_cluster("test-cluster-1")

        # Should return 0 when Maximum key is missing
        self.assertEqual(result, 0)
