import boto3
from app.core.config import settings
from app.core.logging import logger

def get_dynamodb_resource():
    """Initializes the DynamoDB resource based on configuration."""
    params = {
        "region_name": settings.AWS_REGION
    }
    
    # Diagnostic Log
    logger.info(f"Connecting to DynamoDB - Region: {settings.AWS_REGION} | Endpoint: {settings.DYNAMODB_ENDPOINT_URL or 'AWS Cloud'}")

    if settings.AWS_ACCESS_KEY_ID:
        params["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
    if settings.AWS_SECRET_ACCESS_KEY:
        params["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    
    # For Local Development override if set
    if settings.DYNAMODB_ENDPOINT_URL:
        params["endpoint_url"] = settings.DYNAMODB_ENDPOINT_URL

    return boto3.resource("dynamodb", **params)

def init_db():
    """Creates the DynamoDB table if it doesn't exist."""
    dynamodb = get_dynamodb_resource()
    table_name = settings.DYNAMODB_TABLE_NAME
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        logger.info(f"DynamoDB Table '{table_name}' created successfully.")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        logger.info(f"DynamoDB Table '{table_name}' already exists.")
    except Exception as e:
        logger.error(f"Error initializing DynamoDB: {str(e)}")
        # Don't raise if it's just a fallback for local dev when service isn't up yet
        if "Connection refused" in str(e):
             logger.warning("Could not connect to DynamoDB. Ensure DynamoDB Local or AWS access is configured.")
        else:
            raise

def get_table():
    """Helper to get the DynamoDB table resource."""
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
