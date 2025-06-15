# Price Tracker Lambda

This project contains a serverless application that runs on a weekday schedule (Monday-Friday) to fetch price data for multiple assets from an API and store it in DynamoDB.

## Architecture

- **AWS Lambda**: Executes code to fetch price data for multiple assets and store in DynamoDB
- **EventBridge Scheduler**: Triggers the Lambda function on weekdays (M-F) at 12:00 PM UTC
- **DynamoDB**: Stores the retrieved price data with a date-based index for easy querying

## Tracked Assets

The Lambda function fetches price data for the following assets:
- XAU (Gold)
- XAG (Silver)
- XPD (Palladium)
- HG (Copper)
- BTC (Bitcoin)
- ETH (Ethereum)

## API Endpoint

The Lambda function makes requests to the following API endpoint for each asset:
```
https://api.gold-api.com/price/{symbol}
```

Where `{symbol}` is replaced with each asset symbol (XAU, XAG, XPD, HG, BTC, ETH).

## Data Structure

The Lambda function expects the API to return price data in the following format:
```json
{
  "name": "Gold",
  "price": 3433.399902,
  "symbol": "XAU",
  "updatedAt": "2025-06-14T22:54:24Z",
  "updatedAtReadable": "a few seconds ago"
}
```

The data is stored in DynamoDB with the following structure:
```json
{
  "id": "uuid-generated-for-record",
  "name": "Gold",
  "price": 3433.399902,
  "symbol": "XAU",
  "sourceUpdatedAt": "2025-06-14T22:54:24Z",
  "sourceUpdatedAtReadable": "a few seconds ago",
  "recordedAt": "2025-06-14T23:00:00Z",
  "date": "2025-06-14"
}
```

## Deployment Instructions

### Prerequisites
- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.10 or later

### Steps to Deploy

1. Install dependencies:
```
uv venv
source ./.venv/bin/activate
pip3 install -r requirements.txt -t layer/python
```

2. Deploy the application:
```
sam build
sam deploy --guided
```

3. During the guided deployment, you'll be prompted to provide:
   - Stack name
   - AWS Region
   - API endpoint URL
   - DynamoDB table name

## Configuration

You can modify the following parameters:
- `ApiEndpointBase`: The base URL of the API to fetch data from (https://api.gold-api.com/price)
- `TableName`: The name of the DynamoDB table
- `LogLevel`: The logging level for the Lambda function (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Customization

- To change the schedule, modify the `ScheduleExpression` in the `WeekdayScheduleRule` resource in `template.yaml`
- To modify the data processing logic, update the `lambda_function.py` file

## Cleanup

To remove all resources created by this application:
```
sam delete
```
