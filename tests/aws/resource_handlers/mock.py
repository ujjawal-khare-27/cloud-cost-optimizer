mock_volume_response = {
    "Volumes": [
        {
            "Attachments": [],
            "AvailabilityZone": "us-east-1a",
            "CreateTime": "2023-10-01T12:34:56.000Z",
            "Encrypted": False,
            "Size": 8,
            "SnapshotId": "",
            "State": "available",
            "VolumeId": "vol-0123456789abcdef0",
            "Iops": 100,
            "Tags": [{"Key": "Name", "Value": "unused-volume"}],
            "VolumeType": "gp2",
        },
        {
            "Attachments": [],
            "AvailabilityZone": "us-east-1b",
            "CreateTime": "2023-11-15T08:22:10.000Z",
            "Encrypted": True,
            "Size": 20,
            "SnapshotId": "snap-0abc1234def567890",
            "State": "available",
            "VolumeId": "vol-0abcdef1234567890",
            "Iops": 3000,
            "Tags": [{"Key": "Environment", "Value": "test"}],
            "VolumeType": "gp3",
        },
    ],
    "ResponseMetadata": {
        "RequestId": "12345678-90ab-cdef-1234-567890abcdef",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "content-type": "json",
            "date": "Wed, 10 Sep 2025 12:00:00 GMT",
        },
        "RetryAttempts": 0,
    },
}

mock_lb_response = {
    "LoadBalancerDescriptions": [
        {
            "LoadBalancerName": "test-lb-no-targets",
            "DNSName": "test-lb-no-targets-1234567890.us-east-1.elb.amazonaws.com",
            "CanonicalHostedZoneNameID": "Z35SXDOTRQ7X7K",
            "ListenerDescriptions": [
                {
                    "Listener": {
                        "Protocol": "HTTP",
                        "LoadBalancerPort": 80,
                        "InstanceProtocol": "HTTP",
                        "InstancePort": 80,
                    },
                    "PolicyNames": [],
                }
            ],
            "Policies": {"AppCookieStickinessPolicies": [], "LBCookieStickinessPolicies": []},
            "BackendServerDescriptions": [],
            "AvailabilityZones": ["us-east-1a", "us-east-1b"],
            "Subnets": ["subnet-12345", "subnet-67890"],
            "VPCId": "vpc-12345678",
            "Instances": [],
            "HealthCheck": {
                "Target": "HTTP:80/",
                "Interval": 30,
                "Timeout": 5,
                "UnhealthyThreshold": 2,
                "HealthyThreshold": 10,
            },
            "SourceSecurityGroup": {
                "OwnerAlias": "123456789012",
                "GroupName": "default",
            },
            "SecurityGroups": ["sg-12345678"],
            "CreatedTime": "2023-10-01T12:34:56.000Z",
            "Scheme": "internet-facing",
        },
        {
            "LoadBalancerName": "test-lb-all-unhealthy",
            "DNSName": "test-lb-all-unhealthy-1234567890.us-east-1.elb.amazonaws.com",
            "CanonicalHostedZoneNameID": "Z35SXDOTRQ7X7K",
            "ListenerDescriptions": [
                {
                    "Listener": {
                        "Protocol": "HTTP",
                        "LoadBalancerPort": 80,
                        "InstanceProtocol": "HTTP",
                        "InstancePort": 80,
                    },
                    "PolicyNames": [],
                }
            ],
            "Policies": {"AppCookieStickinessPolicies": [], "LBCookieStickinessPolicies": []},
            "BackendServerDescriptions": [],
            "AvailabilityZones": ["us-east-1a", "us-east-1b"],
            "Subnets": ["subnet-12345", "subnet-67890"],
            "VPCId": "vpc-12345678",
            "Instances": [
                {"InstanceId": "i-1234567890abcdef0"},
                {"InstanceId": "i-0abcdef1234567890"},
            ],
            "HealthCheck": {
                "Target": "HTTP:80/",
                "Interval": 30,
                "Timeout": 5,
                "UnhealthyThreshold": 2,
                "HealthyThreshold": 10,
            },
            "SourceSecurityGroup": {
                "OwnerAlias": "123456789012",
                "GroupName": "default",
            },
            "SecurityGroups": ["sg-12345678"],
            "CreatedTime": "2023-10-01T12:34:56.000Z",
            "Scheme": "internet-facing",
        },
        {
            "LoadBalancerName": "test-lb-healthy",
            "DNSName": "test-lb-healthy-1234567890.us-east-1.elb.amazonaws.com",
            "CanonicalHostedZoneNameID": "Z35SXDOTRQ7X7K",
            "ListenerDescriptions": [
                {
                    "Listener": {
                        "Protocol": "HTTP",
                        "LoadBalancerPort": 80,
                        "InstanceProtocol": "HTTP",
                        "InstancePort": 80,
                    },
                    "PolicyNames": [],
                }
            ],
            "Policies": {"AppCookieStickinessPolicies": [], "LBCookieStickinessPolicies": []},
            "BackendServerDescriptions": [],
            "AvailabilityZones": ["us-east-1a", "us-east-1b"],
            "Subnets": ["subnet-12345", "subnet-67890"],
            "VPCId": "vpc-12345678",
            "Instances": [
                {"InstanceId": "i-1111111111111111"},
                {"InstanceId": "i-2222222222222222"},
            ],
            "HealthCheck": {
                "Target": "HTTP:80/",
                "Interval": 30,
                "Timeout": 5,
                "UnhealthyThreshold": 2,
                "HealthyThreshold": 10,
            },
            "SourceSecurityGroup": {
                "OwnerAlias": "123456789012",
                "GroupName": "default",
            },
            "SecurityGroups": ["sg-12345678"],
            "CreatedTime": "2023-10-01T12:34:56.000Z",
            "Scheme": "internet-facing",
        },
    ],
    "ResponseMetadata": {
        "RequestId": "12345678-90ab-cdef-1234-567890abcdef",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "content-type": "json",
            "date": "Wed, 10 Sep 2025 12:00:00 GMT",
        },
        "RetryAttempts": 0,
    },
}

mock_lb_health_response_all_unhealthy = {
    "InstanceStates": [
        {
            "InstanceId": "i-1234567890abcdef0",
            "State": "OutOfService",
            "ReasonCode": "Instance",
            "Description": "Instance has failed at least the UnhealthyThreshold number of health checks consecutively.",
        },
        {
            "InstanceId": "i-0abcdef1234567890",
            "State": "OutOfService",
            "ReasonCode": "Instance",
            "Description": "Instance has failed at least the UnhealthyThreshold number of health checks consecutively.",
        },
    ],
    "ResponseMetadata": {
        "RequestId": "12345678-90ab-cdef-1234-567890abcdef",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "content-type": "json",
            "date": "Wed, 10 Sep 2025 12:00:00 GMT",
        },
        "RetryAttempts": 0,
    },
}

mock_lb_health_response_healthy = {
    "InstanceStates": [
        {
            "InstanceId": "i-1111111111111111",
            "State": "InService",
            "ReasonCode": "N/A",
            "Description": "Instance is in pending state.",
        },
        {
            "InstanceId": "i-2222222222222222",
            "State": "InService",
            "ReasonCode": "N/A",
            "Description": "Instance is in pending state.",
        },
    ],
    "ResponseMetadata": {
        "RequestId": "12345678-90ab-cdef-1234-567890abcdef",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "content-type": "json",
            "date": "Wed, 10 Sep 2025 12:00:00 GMT",
        },
        "RetryAttempts": 0,
    },
}
