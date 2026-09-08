# Pay-Skills Inline OpenAPI Patterns

Working endpoint path definitions from the GenTech Labs PR #154 submission to `solana-foundation/pay-skills`. These are all verified to pass Greptile review and CI validation.

## Path Parameter Pattern

```json
"/api/v1/security/{chain}/{address}": {
  "get": {
    "summary": "Short action summary",
    "description": "One-line longer description of the endpoint.",
    "operationId": "actionResource",
    "parameters": [
      {
        "name": "chain",
        "in": "path",
        "required": true,
        "schema": { "type": "string" },
        "description": "Chain name"
      },
      {
        "name": "address",
        "in": "path",
        "required": true,
        "schema": { "type": "string", "pattern": "^0x[a-fA-F0-9]{40}$" },
        "description": "Contract address"
      }
    ],
    "responses": {
      "200": { "description": "Analysis report" },
      "402": { "description": "x402 payment required" }
    }
  }
}
```

## Query Parameter Pattern

```json
"/api/v1/deals/search": {
  "get": {
    "summary": "Search deals",
    "description": "Cross-store product search.",
    "operationId": "searchDeals",
    "parameters": [
      {
        "name": "q",
        "in": "query",
        "required": true,
        "schema": { "type": "string" },
        "description": "Search term"
      },
      {
        "name": "store",
        "in": "query",
        "required": false,
        "schema": { "type": "string" },
        "description": "Filter by retailer"
      },
      {
        "name": "limit",
        "in": "query",
        "required": false,
        "schema": { "type": "integer", "default": 10, "maximum": 50 }
      }
    ],
    "responses": {
      "200": { "description": "Search results" },
      "402": { "description": "x402 payment required" }
    }
  }
}
```

## POST Request Body Pattern

```json
"/api/v1/router/completion": {
  "post": {
    "summary": "Route AI completion",
    "description": "Route a task to the optimal AI model.",
    "operationId": "routeCompletion",
    "requestBody": {
      "required": true,
      "content": {
        "application/json": {
          "schema": {
            "type": "object",
            "required": ["prompt"],
            "properties": {
              "prompt": { "type": "string", "description": "Task prompt" },
              "domain": { "type": "string", "enum": ["coding", "creative", "analysis", "general"] },
              "max_cost": { "type": "number", "description": "Max cost in cents" }
            }
          }
        }
      }
    },
    "responses": {
      "200": { "description": "Completion result" },
      "402": { "description": "x402 payment required" }
    }
  }
}
```

## Tagged Path Pattern (Cryptocurrency-style)

```json
"/api/v1/price/{symbol}": {
  "get": {
    "summary": "Real-time price quote",
    "description": "Current price for a trading pair.",
    "operationId": "getPrice",
    "parameters": [
      {
        "name": "symbol",
        "in": "path",
        "required": true,
        "schema": { "type": "string", "pattern": "^[A-Z0-9-]+$" },
        "description": "Trading pair (e.g. BTC-USD)"
      }
    ],
    "responses": {
      "200": { "description": "Price quote data" },
      "402": { "description": "x402 payment required" }
    }
  }
}
```

## Enum Parameter Pattern (Chains)

```json
"/api/v1/gas/{chain}": {
  "get": {
    "summary": "Current gas prices",
    "description": "Real-time gas fees for EVM chain.",
    "operationId": "getGasPrice",
    "parameters": [
      {
        "name": "chain",
        "in": "path",
        "required": true,
        "schema": {
          "type": "string",
          "enum": ["ethereum", "base", "arbitrum", "optimism", "polygon", "avalanche", "bnb"]
        },
        "description": "EVM chain name"
      }
    ],
    "responses": {
      "200": { "description": "Gas price data" },
      "402": { "description": "x402 payment required" }
    }
  }
}
```

## Date Parameter Pattern

```json
{
  "name": "depart_date",
  "in": "query",
  "required": true,
  "schema": { "type": "string", "format": "date" },
  "description": "Departure date (YYYY-MM-DD)"
}
```

## Full Spec Top-Level Structure

Every PAY.md inline spec should include this at the root:

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "GenTech Labs — <Service Name>",
    "version": "1.0.0"
  },
  "paths": {
    "...": { "...": {} }
  },
  "x-payment": {
    "protocol": "x402",
    "network": "base",
    "token": "USDC"
  }
}
```

The `x-payment` field is optional but recommended — it explicitly documents the payment protocol in the spec so agents don't need to read the PAY.md body text.

## 12 Working Examples

All 12 GenTech provider files were successfully submitted with these patterns. Key stats:
- **Services**: 12
- **Total endpoints defined**: 24
- **Lines added**: 1,119
- **Lines removed**: 36
- **Review status**: Passes Greptile with populated paths
