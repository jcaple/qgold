from mcp.server.fastmcp import FastMCP
import time
from typing import Any, Dict, List, Optional
import mcp.types as types
import asyncio
import json
import os
import boto3
from pydantic import BaseModel
from datetime import datetime

# Initialize FastMCP
app = FastMCP("qgold_mcp")

# Initialize AWS Lambda client
lambda_client = boto3.client('lambda')
FUNCTION_NAME = "qgold-quote-analysis-function"

class DateRangeRequest(BaseModel):
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@app.tool("get_asset_prices")
def get_asset_prices(name: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve asset price information using specified date ranges.
    
    Args:
        name: The name of the asset (e.g., gold, silver, copper, bitcoin, ethereum, or palladium)
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
        
    Returns:
        Dictionary containing price data for the specified currency and date range
    """
    try:
        
        if not name:
            raise Exception("Missing required parameter: name")

        # If no start_date or end_date is provided, set them to None
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Validate date format if provided
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise Exception("Invalid start_date format. Use YYYY-MM-DD")
                
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise Exception("Invalid end_date format. Use YYYY-MM-DD")
        
        # Prepare payload for Lambda function
        payload = {
            "name": name.lower(),
        }
        
        if start_date:
            payload["start_date"] = start_date
        if end_date:
            payload["end_date"] = end_date
            
        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Parse Lambda response
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        
        if response['StatusCode'] != 200:
            raise Exception(f"Lambda function error: {response_payload}")
        
        # Extract and return the data
        body = json.loads(response_payload.get('body', '{}'))
        return {
            "count": body.get('count', 0),
            "items": body.get('items', [])
        }
        
    except Exception as e:
        raise Exception(f"Error retrieving currency data: {str(e)}")

if __name__ == "__main__":
    app.run()