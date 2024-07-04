"""../clients/dynamodb_client.py"""

from typing import Any

import aioboto3
from aioboto3.session import ResourceCreatorContext


class DynamoDBClient:
    """A wrapper for interacting with DynamoDB using aioboto3."""

    def __init__(self, region_name: str):
        self._region_name = region_name
        self._session = aioboto3.Session(
            region_name=self._region_name,
        )
        self._resource: ResourceCreatorContext

    def __getattr__(self, name: str) -> Any:
        assert self._resource is not None, "Resource is not initialized."
        return getattr(self._resource, name)

    async def __aenter__(self):
        self._resource = await self._session.resource(
            "dynamodb",
        ).__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        assert self._resource is not None, "Resource is not initialized."
        await self._resource.__aexit__(exc_type, exc_value, traceback)
