from dataclasses import dataclass
from typing import Dict, List

import boto3
from src.core.aws.resource_handlers.resource_handler import ResourceHandler


@dataclass
class EbsResourceHandlers(ResourceHandler):
    def __init__(self, region_name: str):
        self._boto3 = boto3.client("ec2", region_name=region_name)

    def find_under_utilized_resource(self) -> List[Dict]:
        volumes = self._boto3.describe_volumes(Filters=[{"Name": "status", "Values": ["available"]}]).get("Volumes", [])

        unused_vols = []
        for vol in volumes:
            unused_vols.append(
                {
                    "VolumeId": vol["VolumeId"],
                    "Size": vol["Size"],
                    "State": vol["State"],
                    "AvailabilityZone": vol["AvailabilityZone"],
                    "CreateTime": str(vol["CreateTime"]),
                }
            )

        return unused_vols
