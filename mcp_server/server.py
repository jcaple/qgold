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
import random

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

@app.tool("model_financial_projections")
def model_financial_projections(initial_amount: float, growth_rate: float, use_random_growth: Optional[bool] = False, withdrawal_rate: Optional[float] = 4.0, skip_withdrawal_after_loss: Optional[bool] = False) -> Dict[str, Any]:
    """
    Calculate a 30-year financial projection with annual withdrawals and growth.
    
    Args:
        initial_amount: Initial savings amount in dollars
        growth_rate: Annual growth rate percentage (ignored if use_random_growth is True)
        use_random_growth: If True, use random rates between -25% and 25% averaging 7% over 5 years
        withdrawal_rate: Annual withdrawal rate percentage (default 4%)
        skip_withdrawal_after_loss: If True, skip withdrawal in years following negative returns
        
    Returns:
        Dictionary containing yearly projection data
    """
    try:
        projection = []
        current_balance = initial_amount
        random_rates = []
        previous_rate = None
        
        for year in range(1, 31):
            # Calculate withdrawal (skip if previous year was negative and flag is set)
            if skip_withdrawal_after_loss and previous_rate is not None and previous_rate < 0:
                withdrawal = 0
                balance_after_withdrawal = current_balance
            else:
                withdrawal = current_balance * (withdrawal_rate / 100)
                balance_after_withdrawal = current_balance - withdrawal
            
            # Determine growth rate for this year
            if use_random_growth:
                rate = random.uniform(-25, 25)
                random_rates.append(rate)
                
                # Adjust every 5 years to maintain 7% average
                if year % 5 == 0:
                    five_year_avg = sum(random_rates[-5:]) / 5
                    adjustment = 7 - five_year_avg
                    rate += adjustment
                    random_rates[-1] = rate
            else:
                rate = growth_rate
            
            # Apply growth
            growth_amount = balance_after_withdrawal * (rate / 100)
            ending_balance = balance_after_withdrawal + growth_amount
            
            projection.append({
                "year": year,
                "starting_balance": round(current_balance, 2),
                "withdrawal_amount": round(withdrawal, 2),
                "balance_after_withdrawal": round(balance_after_withdrawal, 2),
                "growth_rate_percent": round(rate, 2),
                "growth_amount": round(growth_amount, 2),
                "ending_balance": round(ending_balance, 2)
            })
            
            current_balance = ending_balance
            previous_rate = rate
        
        return {
            "years": projection,
            "summary": {
                "initial_amount": initial_amount,
                "final_balance": round(current_balance, 2),
                "total_withdrawals": round(sum(row["withdrawal_amount"] for row in projection), 2)
            }
        }
        
    except Exception as e:
        raise Exception(f"Error calculating financial projection: {str(e)}")

if __name__ == "__main__":
    app.run()