"""../bot/services/dynamodb.py"""

from boto3.dynamodb.conditions import Key

from bot.services.dynamodb_constants import DynamoDBKeySchema
from clients.dynamodb_client import DynamoDBClient


class DynamoDBCrudManager:
    """A wrapper for interacting with DynamoDB using aioboto3."""

    def __init__(self, dynamodb_client: DynamoDBClient, table_name: str):
        self.table_name = table_name
        self.dynamodb_client = dynamodb_client
        self._table = None

    @property
    async def table(self):
        """Asynchronously retrieves and stores the DynamoDB table."""
        if self._table is None:
            self._table = await self.dynamodb_client.Table(self.table_name)
        return self._table

    async def get_item(self, pk: str, sk: str | None = None) -> dict:
        """Retrieves the user from the DynamoDB table asynchronously."""
        table = await self.table
        response = await table.get_item(
            Key={DynamoDBKeySchema.PK.value: pk, DynamoDBKeySchema.SK.value: sk}
        )
        return response.get("Item", {})

    async def put_item(self, item: dict):
        """Puts an item in the DynamoDB table asynchronously."""
        table = await self.table
        await table.put_item(Item=item)

    async def get_attribute(
        self,
        attribute: str,
        pk: str,
        sk: str,
    ) -> str | dict | list | None:
        """Retrieves an attribute from the DynamoDB table asynchronously."""
        item = await self.get_item(pk, sk)
        return item.get(attribute)

    async def update_attributes(
        self,
        attributes: dict,
        pk: str,
        sk: str,
    ):
        """Updates an attributes in the DynamoDB table asynchronously."""
        table = await self.table
        update_expression = "SET " + ", ".join(
            [f"{attr} = :{attr}" for attr in attributes]
        )
        expression_attribute_values = {
            f":{attr}": value for attr, value in attributes.items()
        }
        response = await table.update_item(
            Key={
                DynamoDBKeySchema.PK.value: pk,
                DynamoDBKeySchema.SK.value: sk,
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",
        )
        return response.get("Attributes", {})

    async def delete_attributes(
        self,
        attributes: list[str],
        pk: str,
        sk: str,
    ):
        """Deletes multiple attributes from the DynamoDB table asynchronously."""
        table = await self.table
        remove_expression = ", ".join(attributes)
        return await table.update_item(
            Key={
                DynamoDBKeySchema.PK.value: pk,
                DynamoDBKeySchema.SK.value: sk,
            },
            UpdateExpression=f"REMOVE {remove_expression}",
            ReturnValues="UPDATED_NEW",
        )

    async def get_items_from_index(self, index_name, pk, sk=None):
        """Retrieves an item from a DynamoDB index asynchronously."""
        table = await self.table
        key_condition = Key(DynamoDBKeySchema.GSI2_PK.value).eq(pk)
        if sk is not None:
            key_condition = key_condition & Key(DynamoDBKeySchema.GSI2_SK.value).eq(sk)

        response = await table.query(
            IndexName=index_name, KeyConditionExpression=key_condition
        )
        return response.get("Items", [])
