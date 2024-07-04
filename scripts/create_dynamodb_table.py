"""create_dynamodb_table.py"""

import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

table = dynamodb.create_table(
    TableName="SuaalBMBot",
    KeySchema=[
        {"AttributeName": "PK", "KeyType": "HASH"},
        {"AttributeName": "SK", "KeyType": "RANGE"},
    ],
    AttributeDefinitions=[
        {"AttributeName": "PK", "AttributeType": "S"},
        {"AttributeName": "SK", "AttributeType": "S"},
        {
            "AttributeName": "GSI1_PK",
            "AttributeType": "S",
        },
        {
            "AttributeName": "GSI1_SK",
            "AttributeType": "S",
        },
        {
            "AttributeName": "GSI2_PK",
            "AttributeType": "S",
        },
        {
            "AttributeName": "GSI2_SK",
            "AttributeType": "S",
        },
    ],
    BillingMode="PROVISIONED",
    ProvisionedThroughput={
        "ReadCapacityUnits": 1,
        "WriteCapacityUnits": 1,
    },
    GlobalSecondaryIndexes=[
        {
            "IndexName": "GSI1_PK-GSI1_SK-index",
            "KeySchema": [
                {"AttributeName": "GSI1_PK", "KeyType": "HASH"},
                {
                    "AttributeName": "GSI1_SK",
                    "KeyType": "RANGE",
                },
            ],
            "Projection": {"ProjectionType": "ALL"},
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1,
            },
        },
        {
            "IndexName": "GSI2_PK-GSI2_SK-index",
            "KeySchema": [
                {"AttributeName": "GSI2_PK", "KeyType": "HASH"},
                {
                    "AttributeName": "GSI2_SK",
                    "KeyType": "RANGE",
                },
            ],
            "Projection": {"ProjectionType": "ALL"},
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1,
            },
        },
    ],
)

# Wait for the table to be created
table.meta.client.get_waiter("table_exists").wait(TableName="SuaalBM_BOT")
print("Table created successfully!")
