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

- Developed and Tested on Ubuntu 22.04 bash shell
- An AWS Account
- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.10 or later (aliased as python3)
- AWS Q CLI installed and developer account login

## QGold Lambda Deployment Instructions

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
```

```bash
# Or using uv (faster)
uv pip install -r mcp_server/requirements.txt
```

### Using The MCP Server In Q Cli

#### Add MCP Server

Run the following commands inside the mcp_server directory:

```
q mcp add --name qgold --command python3
```

Edit the mcp.json file to look like the below:

```
vim .amazonq/mcp.json
```

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
q login
```

Then trust the MCP Server tool to start:

```
q chat --trust-tools=qgold___get_asset_prices,qgold___model_financial_projections
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

The following is an example of using the **model_financial_projections** tool to simulate a 4% withdrawl from a savings nest egg in a potential retirement scenario:

```
> Model the withdraw scenarios over 30 years with a starting principal amount of $800k with random annual growth.  If there is negative growth in a year, do not withdraw funds the following year.  Print the results in a table.
I'll model the withdrawal scenarios over 30 years with your specifications. Let me use the financial projection tool to calculate this.


🛠️  Using tool: model_financial_projections (trusted) from mcp server qgold
 ⋮ 
 ● Running model_financial_projections with the param:
 ⋮  {
 ⋮    "arguments": {
 ⋮      "growth_rate": 7,
 ⋮      "initial_amount": 800000,
 ⋮      "skip_withdrawal_after_loss": true,
 ⋮      "use_random_growth": true,
 ⋮      "withdrawal_rate": 4
 ⋮    },
 ⋮    "name": "model_financial_projections"
 ⋮  }
 ⋮ 
 ● Completed in 0.2s
## 30-Year Financial Projection with Random Growth

Here's the 30-year financial projection with an initial amount of $800,000, using random annual growth rates and skipping withdrawals after years with negative growth:

| Year | Starting Balance | Withdrawal | Balance After Withdrawal | Growth Rate | Growth Amount | Ending Balance |
|------|------------------|------------|--------------------------|-------------|---------------|----------------|
| 1    | $800,000.00      | $32,000.00 | $768,000.00              | 13.71%      | $105,294.45   | $873,294.45    |
| 2    | $873,294.45      | $34,931.78 | $838,362.67              | 3.54%       | $29,645.90    | $868,008.57    |
| 3    | $868,008.57      | $34,720.34 | $833,288.23              | -2.38%      | -$19,796.44   | $813,491.79    |
| 4    | $813,491.79      | $0.00      | $813,491.79              | 24.22%      | $197,055.96   | $1,010,547.75  |
| 5    | $1,010,547.75    | $40,421.91 | $970,125.84              | -14.24%     | -$138,175.17  | $831,950.67    |
| 6    | $831,950.67      | $0.00      | $831,950.67              | 6.07%       | $50,496.12    | $882,446.79    |
| 7    | $882,446.79      | $35,297.87 | $847,148.91              | -5.88%      | -$49,808.19   | $797,340.73    |
| 8    | $797,340.73      | $0.00      | $797,340.73              | -24.15%     | -$192,590.29  | $604,750.44    |
| 9    | $604,750.44      | $0.00      | $604,750.44              | 4.38%       | $26,503.18    | $631,253.62    |
| 10   | $631,253.62      | $25,250.14 | $606,003.48              | 15.50%      | $93,921.36    | $699,924.84    |
| 11   | $699,924.84      | $27,996.99 | $671,927.85              | -21.06%     | -$141,486.30  | $530,441.55    |
| 12   | $530,441.55      | $0.00      | $530,441.55              | -18.77%     | -$99,585.47   | $430,856.09    |
| 13   | $430,856.09      | $0.00      | $430,856.09              | 4.13%       | $17,785.55    | $448,641.63    |
| 14   | $448,641.63      | $17,945.67 | $430,695.97              | -7.99%      | -$34,415.90   | $396,280.07    |
| 15   | $396,280.07      | $0.00      | $396,280.07              | 31.36%      | $124,291.45   | $520,571.52    |
| 16   | $520,571.52      | $20,822.86 | $499,748.66              | -11.07%     | -$55,325.43   | $444,423.22    |
| 17   | $444,423.22      | $0.00      | $444,423.22              | 6.62%       | $29,419.11    | $473,842.34    |
| 18   | $473,842.34      | $18,953.69 | $454,888.64              | 3.92%       | $17,808.92    | $472,697.56    |
| 19   | $472,697.56      | $18,907.90 | $453,789.66              | -13.34%     | -$60,545.00   | $393,244.66    |
| 20   | $393,244.66      | $0.00      | $393,244.66              | 7.64%       | $30,036.21    | $423,280.87    |
| 21   | $423,280.87      | $16,931.23 | $406,349.64              | 1.75%       | $7,127.53     | $413,477.16    |
| 22   | $413,477.16      | $16,539.09 | $396,938.08              | 11.25%      | $44,642.72    | $441,580.80    |
| 23   | $441,580.80      | $17,663.23 | $423,917.57              | 3.50%       | $14,824.10    | $438,741.67    |
| 24   | $438,741.67      | $17,549.67 | $421,192.01              | 5.43%       | $22,878.99    | $444,070.99    |
| 25   | $444,070.99      | $17,762.84 | $426,308.15              | 5.90%       | $25,141.68    | $451,449.84    |
| 26   | $451,449.84      | $18,057.99 | $433,391.84              | -21.56%     | -$93,442.92   | $339,948.92    |
| 27   | $339,948.92      | $0.00      | $339,948.92              | 8.91%       | $30,295.74    | $370,244.66    |
| 28   | $370,244.66      | $14,809.79 | $355,434.87              | 1.30%       | $4,631.10     | $360,065.97    |
| 29   | $360,065.97      | $14,402.64 | $345,663.34              | 16.63%      | $57,498.45    | $403,161.79    |
| 30   | $403,161.79      | $16,126.47 | $387,035.32              | -0.02%      | -$91.53       | $386,943.79    |

### Summary:
• Initial amount: $800,000.00
• Final balance after 30 years: $386,943.79
• Total withdrawals over 30 years: $457,092.10

Note that in years following negative growth (years 4, 6, 8, 9, 12, 13, 15, 17, 20, and 27), no withdrawals were made as specified in your requirements. The model used a 4% withdrawal rate in years when withdrawals were permitted.
```