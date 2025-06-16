# QGold MCP Server

This MCP (Model Context Protocol) server provides tools for retrieving currency price information from the QGold Lambda functions.

## Setup

### Install dependencies:
```bash
# Using pip
pip install -r mcp_server/requirements.txt

# Or using uv (faster)
uv pip install -r mcp_server/requirements.txt
```

## Using The MCP Server In Q Cli

### Add MCP Server

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

