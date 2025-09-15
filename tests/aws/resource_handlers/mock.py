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

# CloudWatch mock data
mock_cloudwatch_metric_response = {
    "MetricDataResults": [
        {
            "Id": "m1",
            "Label": "DatabaseConnections",
            "Timestamps": ["2023-10-01T12:00:00.000Z", "2023-10-01T12:10:00.000Z", "2023-10-01T12:20:00.000Z"],
            "Values": [5.0, 3.0, 0.0],
            "StatusCode": "Complete",
        }
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

mock_cloudwatch_empty_response = {
    "MetricDataResults": [],
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

# Mock response for RDS with no connections (all values are 0.0)
mock_cloudwatch_no_connections_response = {
    "MetricDataResults": [
        {
            "Id": "m1",
            "Label": "DatabaseConnections",
            "Timestamps": ["2023-10-01T12:00:00.000Z", "2023-10-01T12:10:00.000Z", "2023-10-01T12:20:00.000Z"],
            "Values": [0.0, 0.0, 0.0],
            "StatusCode": "Complete",
        }
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

# Mock response for RDS with some connections (mixed values)
mock_cloudwatch_some_connections_response = {
    "MetricDataResults": [
        {
            "Id": "m1",
            "Label": "DatabaseConnections",
            "Timestamps": ["2023-10-01T12:00:00.000Z", "2023-10-01T12:10:00.000Z", "2023-10-01T12:20:00.000Z"],
            "Values": [3.0, 2.0, 1.0],
            "StatusCode": "Complete",
        }
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

# RDS mock data
mock_rds_instances_response = {
    "DBInstances": [
        {
            "DBInstanceIdentifier": "test-db-instance-1",
            "DBInstanceClass": "db.t3.micro",
            "Engine": "mysql",
            "DBInstanceStatus": "available",
            "MasterUsername": "admin",
            "DBName": "testdb",
            "AllocatedStorage": 20,
            "InstanceCreateTime": "2023-10-01T12:34:56.000Z",
            "DBInstanceArn": "arn:aws:rds:us-east-1:123456789012:db:test-db-instance-1",
            "VpcSecurityGroups": [{"VpcSecurityGroupId": "sg-12345678", "Status": "active"}],
            "DBSubnetGroup": {
                "DBSubnetGroupName": "default",
                "DBSubnetGroupDescription": "default",
                "VpcId": "vpc-12345678",
                "SubnetGroupStatus": "Complete",
            },
            "DBParameterGroups": [{"DBParameterGroupName": "default.mysql8.0", "ParameterApplyStatus": "in-sync"}],
            "AvailabilityZone": "us-east-1a",
            "DBInstancePort": 3306,
            "StorageType": "gp2",
            "StorageEncrypted": False,
            "DBClusterIdentifier": "test-cluster-1",
        },
        {
            "DBInstanceIdentifier": "test-db-instance-2",
            "DBInstanceClass": "db.t3.small",
            "Engine": "postgres",
            "DBInstanceStatus": "available",
            "MasterUsername": "admin",
            "DBName": "testdb2",
            "AllocatedStorage": 50,
            "InstanceCreateTime": "2023-11-15T08:22:10.000Z",
            "DBInstanceArn": "arn:aws:rds:us-east-1:123456789012:db:test-db-instance-2",
            "VpcSecurityGroups": [{"VpcSecurityGroupId": "sg-87654321", "Status": "active"}],
            "DBSubnetGroup": {
                "DBSubnetGroupName": "default",
                "DBSubnetGroupDescription": "default",
                "VpcId": "vpc-87654321",
                "SubnetGroupStatus": "Complete",
            },
            "DBParameterGroups": [{"DBParameterGroupName": "default.postgres13", "ParameterApplyStatus": "in-sync"}],
            "AvailabilityZone": "us-east-1b",
            "DBInstancePort": 5432,
            "StorageType": "gp3",
            "StorageEncrypted": True,
            "DBClusterIdentifier": "test-cluster-2",
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

mock_rds_empty_response = {
    "DBInstances": [],
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

# S3 mock data
mock_s3_buckets_response = {
    "Buckets": [
        {"Name": "test-bucket-1", "CreationDate": "2023-10-01T12:34:56.000Z"},
        {"Name": "test-bucket-2", "CreationDate": "2023-11-15T08:22:10.000Z"},
        {"Name": "test-bucket-3", "CreationDate": "2023-12-01T15:45:30.000Z"},
    ],
    "Owner": {"DisplayName": "test-user", "ID": "1234567890123456789012345678901234567890123456789012345678901234"},
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

mock_s3_empty_response = {
    "Buckets": [],
    "Owner": {"DisplayName": "test-user", "ID": "1234567890123456789012345678901234567890123456789012345678901234"},
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

# S3 CloudWatch metrics mock data
mock_s3_requests_metrics_response = {
    "Datapoints": [
        {"Timestamp": "2023-10-01T12:00:00.000Z", "Sum": 100.0, "Unit": "Count"},
        {"Timestamp": "2023-10-01T12:10:00.000Z", "Sum": 50.0, "Unit": "Count"},
        {"Timestamp": "2023-10-01T12:20:00.000Z", "Sum": 25.0, "Unit": "Count"},
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

mock_s3_no_requests_metrics_response = {
    "Datapoints": [
        {"Timestamp": "2023-10-01T12:00:00.000Z", "Sum": 0.0, "Unit": "Count"},
        {"Timestamp": "2023-10-01T12:10:00.000Z", "Sum": 0.0, "Unit": "Count"},
        {"Timestamp": "2023-10-01T12:20:00.000Z", "Sum": 0.0, "Unit": "Count"},
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

mock_s3_bucket_size_metrics_response = {
    "Datapoints": [
        {"Timestamp": "2023-10-01T12:00:00.000Z", "Average": 1073741824.0, "Unit": "Bytes"},  # 1 GB
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

mock_s3_bucket_size_empty_response = {
    "Datapoints": [],
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
