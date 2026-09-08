# Travala Travel MCP Quick Reference

**MCP Server:** `https://travel-mcp.travala.com/mcp`
**No API key required** for search endpoints.
**Payment:** x402 (USDC on Base, ~$0.01/tx, gasless)

## Tools

| Tool | Purpose | Required Params |
|------|---------|-----------------|
| `travala_search_hotel` | Search hotels | location, checkIn, checkOut, rooms |
| `travala_search_package` | Room types + rates | hotelId |
| `travala_book` | Book + pay | packageId, sessionId, customer info |
| `travala_book_status` | Check failed bookings | packageId, sessionId |
| `travala_manage_bookings` | Look up booking | bookingId, lastName |
| `travala_cancel_booking` | Cancel booking | bookingId, lastName, email |

## Flow

```
search_hotel → search_package → book → (x402 payment) → confirmation
                                    ↓ (on failure)
                              book_status → retry or report
```

## Agent Rewards

- Register at 8004scan.io/agents for ERC-8004 agentId
- Set `rewardWallet` in skill file
- Earn cbBTC after booking completes (post check-in)
- Without registration → default agent earns nothing

## Setup

```json
{
  "mcpServers": {
    "travala-mcp": {
      "type": "http",
      "url": "https://travel-mcp.travala.com/mcp"
    }
  }
}
```

Install Coinbase payments MCP for x402 payment completion:
```bash
npx @coinbase/payments-mcp
```

## Filters Available

`all_inclusive`, `free_breakfast`, `swimming_pool`, `ocean_view`

## GenTech Travels Integration

Travala = data + booking engine. GenTech Travels adds:
- Privacy layer (private bookings vs public on-chain)
- Social features (Trip Squad, shared bookings)
- Multi-platform (Telegram/Discord/X vs Claude Desktop only)
- Multi-chain payments (not just Base/USDC)
