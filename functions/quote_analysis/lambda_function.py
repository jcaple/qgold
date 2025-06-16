import os
import json
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from decimal import Decimal

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger()

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'PriceDataTable')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Lambda function to retrieve records from DynamoDB based on name and date range
    
    Expected event format:
    {
        "name": "gold",       # Required: The name/name to search for
        "start_date": "2023-05-01",  # Optional: Start date for range query
        "end_date": "2023-05-31"     # Optional: End date for range query
    }
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract parameters from the event
        name = event.get('name')
        start_date = event.get('start_date')
        end_date = event.get('end_date')
        
        if not name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required parameter: name'})
            }
        
        # Build filter expression for scan
        logger.info(f"Scanning for asset_name={name}")
        filter_expression = Attr('asset_name').eq(name)
        
        # Add date range to filter if provided
        if start_date and end_date:
            logger.info(f"With date range between {start_date} and {end_date}")
            filter_expression = filter_expression & Attr('date').between(start_date, end_date)
        elif start_date:
            logger.info(f"With date >= {start_date}")
            filter_expression = filter_expression & Attr('date').gte(start_date)
        elif end_date:
            logger.info(f"With date <= {end_date}")
            filter_expression = filter_expression & Attr('date').lte(end_date)
        
        # Use scan with filter expression instead of query
        filter_expression = Attr('asset_name').eq(name)
        
        # Add date range to filter if provided
        if start_date and end_date:
            filter_expression = filter_expression & Attr('date').between(start_date, end_date)
        elif start_date:
            filter_expression = filter_expression & Attr('date').gte(start_date)
        elif end_date:
            filter_expression = filter_expression & Attr('date').lte(end_date)
            
        # Execute the scan
        response = table.scan(
            FilterExpression=filter_expression
        )
        
        items = response.get('Items', [])
        logger.info(f"Found {len(items)} items")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'count': len(items),
                'items': items
            }, cls=DecimalEncoder)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Error retrieving data: {str(e)}"})
        }