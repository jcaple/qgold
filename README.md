# QGold

This project provides an MCP Server that can be plugged in to LLM tools, like the Q CLI, for natural language questions related to the price performance of certain metal and digital currency assets, like gold, silver and bitcoin, over time.

## Architecture

- **AWS Lambda**: Executes code to fetch price data for multiple assets and stores in DynamoDB
- **EventBridge Scheduler**: Triggers the Lambda function on weekdays (M-F) at 22:00 PM UTC/6pm EST
- **DynamoDB**: Stores the retrieved price data with a date-based index for easy querying
- **Q CLI**: Uses this MCP Server as a cli tool to learn about asset prices stored in DynamoDB

The 'functions' directory contains the AWS lambda functions.

The 'mcp_server' directory contains the MCP server to be used in the AWS Q CLI.

The Makefile consolidates some helpful commands for building and testing the lambda functions.

## Tracked Assets

The Lambda function fetches price data for the following assets:

- XAU (Gold)
- XAG (Silver)
- XPD (Palladium)
- HG (Copper)
- BTC (Bitcoin)
- ETH (Ethereum)

## API Endpoint

The Lambda function makes requests to the following API endpoint for each asset price:

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

## Project Dev Environment Prerequisites

- An AWS Account
- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.10 or later (aliased as python3)

## Lambda Deployment Instructions

The lambda functions live in the 'functions' directory.

### Steps to Deploy

1. Deploy the application:

To deploy using the sam cli and the template.yaml CloudFormation template provided:

```
sam build
sam deploy --guided --capabilities CAPABILITY_NAMED_IAM
```

The included Makefile will also allow you to use these commands to build and deploy:

```
make deploy
```

2. During the guided deployment, you'll be prompted to provide (or accept defaults):
   - Stack name
   - AWS Region
   - API endpoint URL
   - DynamoDB table name

3.  Verify Deployment

```
make test-quote-retrieval
```

**Note**: when successful, this test should populate the DynamoDB QGoldPriceDataTable table with an initial record set.  Otherwise, the database will remain empty until the EventBridge schedule runs to execute the data loading lambda.

A successful response from the test should look like this:

```
{
	"statusCode": 200,
	"body": "{\"message\": \"Price data processing complete\", \"timestamp\": \"2025-06-16T16:14:30.379948\", \"successful\": [\"XAU\", \"XAG\", \"XPD\", \"HG\", \"BTC\", \"ETH\"], \"failed\": []}"
}
```

To ensure the quote analysis lambda function is working, run the following test:

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

However, it is probably best to just leave these alone.

## Customization

- To change the schedule, modify the `ScheduleExpression` in the `WeekdayScheduleRule` resource in `template.yaml`
- To modify the data processing logic, update the `lambda_function.py` file

The DynamoDB indexes are setup such that the data is updated daily (as opposed to taking into account time as well).

## Cleanup

To remove all resources created by this application:

```
sam delete
```

## QGold MCP Server

This MCP (Model Context Protocol) server provides tools for retrieving currency price information from the QGold Lambda functions.

### Setup

#### Install dependencies:

```bash
# Using pip
pip install -r mcp_server/requirements.txt

# Or using uv (faster)
uv pip install -r mcp_server/requirements.txt
```

### Using The MCP Server In Q Cli

#### Add MCP Server

```
q mcp add --name qgold --command python3
vim .amazonq/mcp.json
```

Edit mcp.json to look like this:

```
{
  "mcpServers": {
    "qgold": {
      "command": "python3",
      "args": ["server.py"]
    }
  }
}
```

Run q cli like this:

```
q chat --trust-tools=qgold___get_asset_prices
```

### get_asset_prices

Retrieves currency price information using specified date ranges.

**Parameters:**
- `name` (required): The name of the currency (e.g., gold, silver)
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

### Sample Chat Sessions

```
> what about today's copper price
Let me check the current price of copper for you.


🛠️  Using tool: get_asset_prices (trusted) from mcp server qgold
 ⋮ 
 ● Running get_asset_prices with the param:
 ⋮  {
 ⋮    "arguments": {
 ⋮      "name": "copper"
 ⋮    },
 ⋮    "name": "get_asset_prices"
 ⋮  }
 ⋮ 
 ● Completed in 0.66s
Based on the latest data, the current price of copper is $4.41 per pound as of June 16, 2025. This price was last updated just a few seconds ago at 16:14:28 UTC today.

> What are the prices of XAG today?
I'll help you check the current price of silver (XAG) today.


🛠️  Using tool: get_asset_prices (trusted) from mcp server qgold
 ⋮ 
 ● Running get_asset_prices with the param:
 ⋮  {
 ⋮    "arguments": {
 ⋮      "name": "silver"
 ⋮    },
 ⋮    "name": "get_asset_prices"
 ⋮  }
 ⋮ 
 ● Completed in 0.51s
Based on the latest data, the current price of silver (XAG) is $36.42 per troy ounce as of June 16, 2025. This price was last updated just a few seconds ago at 16:14:26 UTC today.

> what are today's prices for gold, silver, copper and btc?
I'll retrieve the current prices for gold, silver, copper, and bitcoin for you.


🛠️  Using tool: get_asset_prices (trusted) from mcp server qgold
 ⋮ 
 ● Running get_asset_prices with the param:
 ⋮  {
 ⋮    "arguments": {
 ⋮      "name": "gold"
 ⋮    },
 ⋮    "name": "get_asset_prices"
 ⋮  }
 ⋮ 
 ● Completed in 0.74s



🛠️  Using tool: get_asset_prices (trusted) from mcp server qgold
 ⋮ 
 ● Running get_asset_prices with the param:
 ⋮  {
 ⋮    "arguments": {
 ⋮      "name": "silver"
 ⋮    },
 ⋮    "name": "get_asset_prices"
 ⋮  }
 ⋮ 
 ● Completed in 0.54s



🛠️  Using tool: get_asset_prices (trusted) from mcp server qgold
 ⋮ 
 ● Running get_asset_prices with the param:
 ⋮  {
 ⋮    "arguments": {
 ⋮      "name": "copper"
 ⋮    },
 ⋮    "name": "get_asset_prices"
 ⋮  }
 ⋮ 
 ● Completed in 0.62s



🛠️  Using tool: get_asset_prices (trusted) from mcp server qgold
 ⋮ 
 ● Running get_asset_prices with the param:
 ⋮  {
 ⋮    "arguments": {
 ⋮      "name": "bitcoin"
 ⋮    },
 ⋮    "name": "get_asset_prices"
 ⋮  }
 ⋮ 
 ● Completed in 0.44s
Here are today's prices for all the assets you requested (June 16, 2025):

• Gold (XAU): $3,401.13 per troy ounce
• Silver (XAG): $36.42 per troy ounce
• Copper (HG): $4.41 per pound
• Bitcoin (BTC): $107,604.82

All prices were last updated just a few seconds ago, around 16:14 UTC today.

```