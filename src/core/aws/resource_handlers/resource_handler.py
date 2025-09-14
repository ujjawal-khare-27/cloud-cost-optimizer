from abc import ABC
from typing import Dict, List


class ResourceHandler(ABC):

    async def find_under_utilized_resource(self) -> List[Dict]:
        pass
