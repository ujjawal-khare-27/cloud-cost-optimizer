from dataclasses import dataclass
from typing import Dict

from src.core.aws.resource_handlers.resource_handler import ResourceHandler
from src.core.utils import AsyncClientManager


@dataclass
class EbsResourceHandlers(ResourceHandler):
    def __init__(self, region_name: str):
        self.region_name = region_name
        self._client_manager = AsyncClientManager(region_name)

    async def find_under_utilized_resource(self) -> Dict:
        async with self._client_manager as manager:
            async with manager.get_client("ec2") as ec2:
                volumes = await ec2.describe_volumes(Filters=[{"Name": "status", "Values": ["available"]}])
                volumes = volumes.get("Volumes", [])

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

        return {"unused_ebs_volumes": unused_vols}
