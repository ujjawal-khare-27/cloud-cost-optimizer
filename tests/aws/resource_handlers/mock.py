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
