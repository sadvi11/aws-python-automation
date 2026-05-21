"""
dynamodb_table.py — DynamoDB Table Automation
────────────────────────────────────────────────────────────────
Automates DynamoDB table lifecycle:
  - Create table with GSI (Global Secondary Index)
  - Put / Get / Query / Delete items
  - List all tables
  - Delete table

Use case: Financial event tracking for SmartMoney Canada platform.
Each event has a user_id (partition key) and timestamp (sort key).

Run: python dynamodb_table.py
"""

import boto3
import json
import logging
from datetime import datetime
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION", "ca-central-1")
TABLE_NAME = "smartmoney-financial-events"


class DynamoDBManager:
    """Manages DynamoDB table lifecycle and item operations."""

    def __init__(self):
        self.client = boto3.client("dynamodb", region_name=AWS_REGION)
        self.resource = boto3.resource("dynamodb", region_name=AWS_REGION)
        self.table = None

    # ── Table Operations ──────────────────────────────────────────────────────

    def create_table(self, table_name: str = TABLE_NAME) -> dict:
        """
        Create DynamoDB table with:
        - Partition key: user_id (String)
        - Sort key: timestamp (String)
        - GSI: event_type-index on event_type + timestamp
        """
        try:
            table = self.client.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "user_id",   "KeyType": "HASH"},
                    {"AttributeName": "timestamp",  "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "user_id",    "AttributeType": "S"},
                    {"AttributeName": "timestamp",  "AttributeType": "S"},
                    {"AttributeName": "event_type", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "event_type-index",
                        "KeySchema": [
                            {"AttributeName": "event_type", "KeyType": "HASH"},
                            {"AttributeName": "timestamp",  "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "BillingMode": "PAY_PER_REQUEST",
                    }
                ],
                BillingMode="PAY_PER_REQUEST",  # On-demand — no capacity planning needed
                Tags=[
                    {"Key": "Project",     "Value": "SmartMoneyCanada"},
                    {"Key": "Environment", "Value": "dev"},
                    {"Key": "ManagedBy",   "Value": "aws-python-automation"},
                ],
            )
            logger.info(f"Creating table: {table_name}")

            # Wait until table is active
            waiter = self.client.get_waiter("table_exists")
            waiter.wait(TableName=table_name)
            logger.info(f"Table ACTIVE: {table_name}")
            self.table = self.resource.Table(table_name)
            return table

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceInUseException":
                logger.info(f"Table already exists: {table_name}")
                self.table = self.resource.Table(table_name)
                return {"TableName": table_name, "status": "already_exists"}
            raise

    def list_tables(self) -> list:
        """List all DynamoDB tables in the account."""
        response = self.client.list_tables()
        tables = response.get("TableNames", [])
        logger.info(f"Tables found: {tables}")
        return tables

    def describe_table(self, table_name: str = TABLE_NAME) -> dict:
        """Get table metadata — status, item count, GSIs."""
        response = self.client.describe_table(TableName=table_name)
        table = response["Table"]
        logger.info(f"Table: {table_name}")
        logger.info(f"  Status     : {table['TableStatus']}")
        logger.info(f"  Items      : {table.get('ItemCount', 0)}")
        logger.info(f"  Size bytes : {table.get('TableSizeBytes', 0)}")
        return table

    def delete_table(self, table_name: str = TABLE_NAME) -> None:
        """Delete the table — irreversible."""
        confirm = input(f"Delete table '{table_name}'? (yes/no): ")
        if confirm.lower() != "yes":
            logger.info("Cancelled.")
            return
        self.client.delete_table(TableName=table_name)
        logger.info(f"Deleted table: {table_name}")

    # ── Item Operations ───────────────────────────────────────────────────────

    def put_item(self, user_id: str, event_type: str, data: dict) -> None:
        """Write a financial event item to DynamoDB."""
        if not self.table:
            self.table = self.resource.Table(TABLE_NAME)

        item = {
            "user_id":    user_id,
            "timestamp":  datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data":       data,
            "created_at": datetime.utcnow().strftime("%Y-%m-%d"),
        }
        self.table.put_item(Item=item)
        logger.info(f"Put item: user={user_id}, event={event_type}")

    def get_item(self, user_id: str, timestamp: str) -> dict:
        """Retrieve a specific item by partition + sort key."""
        if not self.table:
            self.table = self.resource.Table(TABLE_NAME)

        response = self.table.get_item(
            Key={"user_id": user_id, "timestamp": timestamp}
        )
        item = response.get("Item", {})
        logger.info(f"Got item: {json.dumps(item, default=str)}")
        return item

    def query_by_user(self, user_id: str) -> list:
        """Query all events for a specific user (partition key scan)."""
        from boto3.dynamodb.conditions import Key
        if not self.table:
            self.table = self.resource.Table(TABLE_NAME)

        response = self.table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )
        items = response.get("Items", [])
        logger.info(f"Query user={user_id}: {len(items)} items found")
        return items

    def query_by_event_type(self, event_type: str) -> list:
        """Query all events by type using GSI (event_type-index)."""
        from boto3.dynamodb.conditions import Key
        if not self.table:
            self.table = self.resource.Table(TABLE_NAME)

        response = self.table.query(
            IndexName="event_type-index",
            KeyConditionExpression=Key("event_type").eq(event_type)
        )
        items = response.get("Items", [])
        logger.info(f"GSI query event_type={event_type}: {len(items)} items")
        return items

    def delete_item(self, user_id: str, timestamp: str) -> None:
        """Delete a specific item."""
        if not self.table:
            self.table = self.resource.Table(TABLE_NAME)

        self.table.delete_item(
            Key={"user_id": user_id, "timestamp": timestamp}
        )
        logger.info(f"Deleted item: user={user_id}, timestamp={timestamp}")


def main():
    print("=" * 50)
    print("DynamoDB Automation — SmartMoney Canada")
    print(f"Region: {AWS_REGION}")
    print("=" * 50)

    db = DynamoDBManager()

    # Step 1: Create table
    print("\n1. Creating table...")
    db.create_table()

    # Step 2: Put sample items
    print("\n2. Writing financial events...")
    db.put_item(
        user_id="user_001",
        event_type="document_upload",
        data={"filename": "td-bank-q1-2024.txt", "size_kb": 12}
    )
    db.put_item(
        user_id="user_001",
        event_type="sentiment_query",
        data={"headline": "TD Bank reports record profit", "result": "positive"}
    )
    db.put_item(
        user_id="user_002",
        event_type="sentiment_query",
        data={"headline": "Canadian housing market falls", "result": "negative"}
    )

    # Step 3: Query by user
    print("\n3. Querying events for user_001...")
    items = db.query_by_user("user_001")
    for item in items:
        print(f"  {item['event_type']} @ {item['timestamp']}")

    # Step 4: Query by event type using GSI
    print("\n4. Querying all sentiment_query events via GSI...")
    items = db.query_by_event_type("sentiment_query")
    print(f"  Found {len(items)} sentiment queries")

    # Step 5: Describe table
    print("\n5. Table metadata...")
    db.describe_table()

    print("\nDynamoDB automation complete.")
    print("To delete table: db.delete_table()")


if __name__ == "__main__":
    main()
