from contextlib import asynccontextmanager

import aioboto3


class AsyncClientManager:
    """Manages async AWS clients with session reuse"""

    def __init__(self, region_name: str):
        self.region_name = region_name
        self._session = None

    async def __aenter__(self):
        self._session = aioboto3.Session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._session = None

    @asynccontextmanager
    async def get_client(self, service_name: str):
        """Get an async client for the specified service"""
        # Create a new client each time but reuse the session
        client = self._session.client(service_name, region_name=self.region_name)
        async with client as c:
            yield c
