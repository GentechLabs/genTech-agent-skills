# Travala Travel MCP Integration

## MCP Server
- URL: `https://travel-mcp.travala.com/mcp`
- No API key required for search endpoints
- 2.2M+ hotel properties (Marriott, Hilton, IHG)

## Tools (6)
1. `travala_search_hotel` — location, dates, price range, filters
2. `travala_search_package` — room types, rates, meal plans
3. `travala_book` — book + x402 payment (USDC, ~$0.01/tx)
4. `travala_book_status` — recovery for failed bookings
5. `travala_manage_bookings` — lookup existing bookings
6. `travala_cancel_booking` — cancel with refund

## Agent Registration
- Register at 8004scan.io/agents for ERC-8004 agentId
- Set rewardWallet (any EVM address on Base)
- Payout in cbBTC after booking completes

## Payment Flow
1. `travala_book` returns HTTP 402 with x402 payment details
2. Need `@coinbase/payments-mcp` for payment completion
3. USDC on Base, gasless, ~$0.01 per transaction

## GenTech Travels Integration
- Travala MCP = data + booking engine
- Our x402/Q402 = payment layer
- Privacy wrapper = our moat (Travala is public on-chain)
- Telegram/Discord/X = distribution

## Source
- GitHub: https://github.com/travala/travel-mcp
- Spec: /root/vaults/gentech/Strategies/travala-mcp-integration-spec.md
