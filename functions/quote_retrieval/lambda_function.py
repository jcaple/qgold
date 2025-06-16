import json
import boto3
import requests
from datetime import datetime
import os
import logging
import uuid
from decimal import Decimal

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Configure logging
logger = logging.getLogger()
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger.setLevel(getattr(logging, log_level))

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# List of symbols to fetch
SYMBOLS = ['XAU', 'XAG', 'XPD', 'HG', 'BTC', 'ETH']

def lambda_handler(event, context):
    """
    Lambda function that retrieves price data for multiple symbols from an API and stores it in DynamoDB.
    Triggered by EventBridge scheduler on weekdays (M-F).
    
    API endpoint: https://api.gold-api.com/price/{symbol}
    Symbols: XAU, XAG, XPD, HG, BTC, ETH
    
    Expected API response format for each symbol:
    {
        "name": "Gold",
        "price": 3433.399902,
        "symbol": "XAU",
        "updatedAt": "2025-06-14T22:54:24Z",
        "updatedAtReadable": "a few seconds ago"
    }
    """
    logger.info(f"Lambda function invoked with event: {json.dumps(event)}")
    
    try:
        # Get the table name from environment variable
        table_name = os.environ.get('DYNAMODB_TABLE_NAME')
        if not table_name:
            logger.error("DYNAMODB_TABLE_NAME environment variable not set")
            raise ValueError("DYNAMODB_TABLE_NAME environment variable not set")
            
        logger.info(f"Using DynamoDB table: {table_name}")
        table = dynamodb.Table(table_name)
        
        # Get API endpoint base URL from environment variable
        api_endpoint_base = os.environ.get('API_ENDPOINT_BASE')
        if not api_endpoint_base:
            logger.error("API_ENDPOINT_BASE environment variable not set")
            raise ValueError("API_ENDPOINT_BASE environment variable not set")
        
        # Common timestamp for all records in this execution
        execution_timestamp = datetime.utcnow().isoformat()
        execution_date = execution_timestamp.split('T')[0]
        
        # Track successful and failed API calls
        successful_symbols = []
        failed_symbols = []
        
        # Process each symbol
        for symbol in SYMBOLS:
            try:
                # Construct the full API endpoint for this symbol
                api_endpoint = f"{api_endpoint_base}/{symbol}"
                logger.info(f"Making API request for symbol {symbol} to: {api_endpoint}")
                
                # Make API call to retrieve data
                start_time = datetime.utcnow()
                response = requests.get(api_endpoint)
                request_duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"API request for {symbol} completed in {request_duration:.2f} seconds with status code: {response.status_code}")
                
                # Check if the API call was successful
                if response.status_code == 200:
                    # Parse the API response
                    price_data = response.json()
                    logger.info(f"Successfully parsed API response for {symbol}: {json.dumps(price_data)}")
                    
                    # Generate a unique ID for this record
                    record_id = str(uuid.uuid4())
                    
                    # Create the item to store in DynamoDB
                    # Use name-date as a composite key to ensure uniqueness per day
                    item = {
                        'id': record_id,
                        'name': price_data.get('name').lower() + "-" + execution_date,  # Composite key: name-date
                        'price': Decimal(str(price_data.get('price'))),  # Convert float to Decimal
                        'symbol': price_data.get('symbol'),
                        'sourceUpdatedAt': price_data.get('updatedAt'),
                        'sourceUpdatedAtReadable': price_data.get('updatedAtReadable'),
                        'recordedAt': execution_timestamp,
                        'date': execution_date,
                        'asset_name': price_data.get('name').lower()  # Store original name for queries
                    }
                    
                    logger.info(f"Storing price record for {symbol} with ID: {record_id}")
                    # Use the custom encoder for logging the item with Decimal values
                    logger.debug(f"Item data: {json.dumps(item, cls=DecimalEncoder)}")
                    
                    # Store in DynamoDB
                    table.put_item(Item=item)
                    successful_symbols.append(symbol)
                    
                else:
                    error_msg = f"API call for {symbol} failed with status code: {response.status_code}, response: {response.text}"
                    logger.error(error_msg)
                    failed_symbols.append(symbol)
                    
            except Exception as e:
                logger.error(f"Error processing symbol {symbol}: {str(e)}", exc_info=True)
                failed_symbols.append(symbol)
        
        # Log summary of processing
        logger.info(f"Processing complete. Successful symbols: {successful_symbols}. Failed symbols: {failed_symbols}")
        
        # Return summary of processing
        return {
            'statusCode': 200 if not failed_symbols else 207,  # 207 Multi-Status if some failed
            'body': json.dumps({
                'message': 'Price data processing complete',
                'timestamp': execution_timestamp,
                'successful': successful_symbols,
                'failed': failed_symbols
            }, cls=DecimalEncoder)
        }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f'API request error: {str(e)}', cls=DecimalEncoder)
        }
    except boto3.exceptions.Boto3Error as e:
        logger.error(f"AWS error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f'AWS error: {str(e)}', cls=DecimalEncoder)
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing data: {str(e)}', cls=DecimalEncoder)
        }
