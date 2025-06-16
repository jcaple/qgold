# Price Tracker Lambda

This project contains a serverless application that runs on a weekday schedule (Monday-Friday) to fetch price data for multiple assets from an API and store it in DynamoDB.

## Architecture

- **AWS Lambda**: Executes code to fetch price data for multiple assets and store in DynamoDB
- **EventBridge Scheduler**: Triggers the Lambda function on weekdays (M-F) at 22:00 PM UTC
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
  "name": "gold-2025-06-14",  // Composite key of asset name and date
  "asset_name": "gold",       // Original asset name in lowercase for querying
  "price": 3433.399902,
  "symbol": "XAU",
  "sourceUpdatedAt": "2025-06-14T22:54:24Z",
  "sourceUpdatedAtReadable": "a few seconds ago",
  "recordedAt": "2025-06-14T23:00:00Z",
  "date": "2025-06-14"
}
```

The table uses a composite primary key:
- Hash key: `name` (format: "{asset_name}-{date}")
- Range key: `date`

And includes these secondary indexes:
- `DateIndex`: For querying by date
- `IdIndex`: For querying by record ID
- `AssetNameDateIndex`: For querying by asset name and date range

## Deployment Instructions

### Prerequisites
- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.10 or later

### Steps to Deploy

1. Deploy the application:

```
sam build
sam deploy --guided --capabilities CAPABILITY_NAMED_IAM
```

The Makefile will also allow you to use this command to build and deploy:

```
make deploy
```

2. During the guided deployment, you'll be prompted to provide (or except defaults):
   - Stack name
   - AWS Region
   - API endpoint URL
   - DynamoDB table name

3.  Verify Deployment

```
make test-quote-retrieval
```

A successful response should look like this:

```
{
	"statusCode": 200,
	"body": "{\"message\": \"Price data processing complete\", \"timestamp\": \"2025-06-16T16:14:30.379948\", \"successful\": [\"XAU\", \"XAG\", \"XPD\", \"HG\", \"BTC\", \"ETH\"], \"failed\": []}"
}
```

To ensure the quote analysis function is working, run the following test:

```
make test-quote-analysis
```

The expected response should look like this:

```
{"statusCode": 200, "body": "{\"count\": 1, \"items\": [{\"date\": \"2025-06-16\", \"symbol\": \"XAU\", \"sourceUpdatedAtReadable\": \"a few seconds ago\", \"asset_name\": \"gold\", \"sourceUpdatedAt\": \"2025-06-16T16:14:27Z\", \"price\": 3401.129883, \"id\": \"330cfe64-64e9-4f75-b930-dc163b4c5ebf\", \"recordedAt\": \"2025-06-16T16:14:30.379948\", \"name\": \"gold-2025-06-16\"}]}"}
```

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
