import unittest
from unittest.mock import patch, AsyncMock

from src.core.aws.resource_handlers.lb import LoadBalancerResourceHandlers
from tests.aws.resource_handlers.mock import (
    mock_lb_response,
    mock_lb_health_response_all_unhealthy,
    mock_lb_health_response_healthy,
)


class TestLoadBalancerResourceHandlers(unittest.TestCase):
    def setUp(self):
        self.region_name = "us-east-1"
        self.lb_handler = LoadBalancerResourceHandlers(self.region_name)

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_list(self, mock_get_client):
        """Test _get_list method"""
        mock_elb_client = AsyncMock()
        mock_elb_client.describe_load_balancers.return_value = mock_lb_response
        mock_get_client.return_value.__aenter__.return_value = mock_elb_client

        handler = LoadBalancerResourceHandlers("us-east-1")
        lb_list = await handler._get_list()

        mock_elb_client.describe_load_balancers.assert_called_once()
        self.assertEqual(len(lb_list), 3)
        self.assertEqual(lb_list[0]["LoadBalancerName"], "test-lb-no-targets")

    def test_get_lb_with_no_targets(self):
        """Test _get_lb_with_no_targets method"""
        handler = LoadBalancerResourceHandlers("us-east-1")

        # Test with load balancers that have no instances
        lb_list = [
            {"LoadBalancerName": "lb1", "Instances": []},
            {"LoadBalancerName": "lb2", "Instances": [{"InstanceId": "i-123"}]},
            {"LoadBalancerName": "lb3", "Instances": []},
        ]

        result = handler._get_lb_with_no_targets(lb_list)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["LoadBalancerName"], "lb1")
        self.assertEqual(result[1]["LoadBalancerName"], "lb3")

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_lb_with_all_unhealthy_targets(self, mock_get_client):
        """Test _get_lb_with_all_unhealthy_targets method"""
        mock_elb_client = AsyncMock()
        mock_get_client.return_value.__aenter__.return_value = mock_elb_client

        # Mock health check responses
        mock_elb_client.describe_instance_health.side_effect = [
            mock_lb_health_response_all_unhealthy,  # For test-lb-all-unhealthy
            mock_lb_health_response_healthy,  # For test-lb-healthy
        ]

        handler = LoadBalancerResourceHandlers("us-east-1")

        # Test with load balancers that have instances
        lb_list = [
            {
                "LoadBalancerName": "test-lb-all-unhealthy",
                "Instances": [{"InstanceId": "i-123"}, {"InstanceId": "i-456"}],
            },
            {
                "LoadBalancerName": "test-lb-healthy",
                "Instances": [{"InstanceId": "i-111"}, {"InstanceId": "i-222"}],
            },
        ]

        result = await handler._get_lb_with_all_unhealthy_targets(lb_list)

        # Should only return the load balancer with all unhealthy targets
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["LoadBalancerName"], "test-lb-all-unhealthy")

    @patch("src.core.utils.AsyncClientManager")
    async def test_get_lb_with_all_unhealthy_targets_no_instances(self, mock_get_client):
        """Test _get_lb_with_all_unhealthy_targets with load balancers that have no instances"""
        mock_elb_client = AsyncMock()
        mock_get_client.return_value.__aenter__.return_value = mock_elb_client

        handler = LoadBalancerResourceHandlers("us-east-1")

        # Test with load balancers that have no instances
        lb_list = [
            {"LoadBalancerName": "lb1", "Instances": []},
            {"LoadBalancerName": "lb2", "Instances": []},
        ]

        result = await handler._get_lb_with_all_unhealthy_targets(lb_list)

        # Should return empty list since no instances means no health checks
        self.assertEqual(len(result), 0)
        # Should not call describe_instance_health for load balancers with no instances
        mock_elb_client.describe_instance_health.assert_not_called()

    @patch("src.core.utils.AsyncClientManager")
    async def test_find_under_utilized_resource_comprehensive(self, mock_get_client):
        """Test find_under_utilized_resource with comprehensive scenario"""
        mock_elb_client = AsyncMock()
        mock_get_client.return_value.__aenter__.return_value = mock_elb_client

        # Mock describe_load_balancers response
        mock_elb_client.describe_load_balancers.return_value = mock_lb_response

        # Mock health check responses
        mock_elb_client.describe_instance_health.side_effect = [
            mock_lb_health_response_all_unhealthy,  # For test-lb-all-unhealthy
            mock_lb_health_response_healthy,  # For test-lb-healthy
        ]

        handler = LoadBalancerResourceHandlers("us-east-1")
        result = await handler.find_under_utilized_resource()

        assert len(result["no_targets_lb"]) == 1
        assert len(result["all_unhealthy"]) == 1

    @patch("src.core.utils.AsyncClientManager")
    async def test_find_under_utilized_resource_mixed_health_states(self, mock_get_client):
        """Test find_under_utilized_resource with mixed health states"""
        mock_elb_client = AsyncMock()
        mock_get_client.return_value.__aenter__.return_value = mock_elb_client

        # Mock response with mixed health states
        mixed_health_response = {
            "InstanceStates": [
                {
                    "InstanceId": "i-1234567890abcdef0",
                    "State": "OutOfService",
                    "ReasonCode": "Instance",
                    "Description": "Instance has failed health checks.",
                },
                {
                    "InstanceId": "i-0abcdef1234567890",
                    "State": "InService",
                    "ReasonCode": "N/A",
                    "Description": "Instance is healthy.",
                },
            ]
        }

        mock_elb_client.describe_load_balancers.return_value = {
            "LoadBalancerDescriptions": [
                {
                    "LoadBalancerName": "test-lb-mixed",
                    "Instances": [{"InstanceId": "i-123"}, {"InstanceId": "i-456"}],
                }
            ]
        }
        mock_elb_client.describe_instance_health.return_value = mixed_health_response

        handler = LoadBalancerResourceHandlers("us-east-1")
        result = await handler.find_under_utilized_resource()

        # Should return empty list since not ALL instances are unhealthy
        self.assertEqual({"no_targets_lb": [], "all_unhealthy": []}, result)

    @patch("src.core.utils.AsyncClientManager")
    async def test_find_under_utilized_resource_api_error_in_get_list(self, mock_get_client):
        """Test find_under_utilized_resource when describe_load_balancers fails"""
        mock_elb_client = AsyncMock()
        mock_get_client.return_value.__aenter__.return_value = mock_elb_client

        # Mock API error
        mock_elb_client.describe_load_balancers.side_effect = Exception("API Error")

        handler = LoadBalancerResourceHandlers("us-east-1")

        # Should raise the exception
        with self.assertRaises(Exception) as context:
            await handler.find_under_utilized_resource()

        self.assertEqual("API Error", str(context.exception))
