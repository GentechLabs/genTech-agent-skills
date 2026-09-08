# OpenTrader Architecture Reference

## Project Overview
OpenTrader is an open-source crypto trading bot platform. Monorepo with pnpm workspaces + moon tooling.

## Monorepo Structure
- `app/` - CLI application and daemon (Commander.js)
- `packages/trpc/` - tRPC API layer
- `packages/prisma/` - Prisma schema and client
- `packages/db/` - Database abstraction with extended Prisma client
- `packages/bot/` - Bot processing engine and Fastify server
- `packages/bot-templates/` - Trading strategy templates (DCA, Grid, RSI)
- `packages/bot-processor/` - Strategy execution engine
- `packages/exchanges/` - Exchange integrations via CCXT
- `packages/event-bus/` - Event system for bot lifecycle
- `packages/types/` - Shared TypeScript types
- `packages/logger/` - Logging (pino)
- `packages/indicators/` - Technical indicators
- `packages/backtesting/` - Backtesting engine

## Prisma Schema (SQLite)

### Core Models
- **User** - Single admin user (id, email, displayName, role)
- **ExchangeAccount** - Exchange API credentials (exchangeCode, apiKey, secretKey, password, isDemoAccount, isPaperAccount)
- **Bot** - Trading bots (type, name, label, symbol, enabled, template, timeframe, processing, settings JSON, state JSON)
- **SmartTrade** - Trading operations (type: Trade/DCA, entryType, takeProfitType, symbol, ref)
- **Order** - Individual orders (status, type, entityType, side, price, filledPrice, quantity)
- **BotLog** - Strategy execution logs (action, triggerEventType, context JSON, error JSON)
- **Markets** - Cached market data per exchange
- **PaperAsset** - Paper trading balances
- **PaperOrder** - Paper trading orders

### Key Relationships
- User → ExchangeAccount (1:many)
- User → Bot (1:many)
- ExchangeAccount → Bot (1:many, primary + additional)
- Bot → SmartTrade (1:many)
- SmartTrade → Order (1:many)
- Bot → BotLog (1:many)

### JSON Fields (stored as strings, parsed by xprisma)
- Bot.settings - Bot configuration (validated with ZBotSettings)
- Bot.state - Bot runtime state (JSON)
- BotLog.context - Market data snapshot
- BotLog.error - Error details
- Markets.markets - Cached market data

## tRPC API Layer

### Authentication
- Password-based via `Authorization` header
- Single admin user (id=1)
- `isLoggedIn` middleware checks `ctx.user` exists

### App Router Structure
```
appRouter
├── exchangeAccount (CRUD + check)
├── symbol (list, getOne, price)
├── candles (list)
├── bot (CRUD + start/stop/backtest + smartTrades/logs)
├── dcaBot (CRUD + getTrades + formOptions)
├── gridBot (CRUD + formOptions)
├── smartTrade (list, infiniteList, getOne)
├── order (openOrders, closedOrders, infiniteOrders)
├── exchange (getAssets, getTicker)
└── public (healthcheck)
```

### Key Endpoints
- `bot.start` / `bot.stop` - Bot lifecycle
- `bot.backtest` - Strategy backtesting
- `exchangeAccount.check` - Validate exchange credentials
- `symbol.price` - Current market price
- `exchange.getAssets` - Account balances

## Server Architecture

### Fastify Server
- Serves static frontend from `app/frontend/`
- tRPC adapter at `/api/trpc`
- CORS enabled
- Configurable host/port (default: localhost:8000)

### Bot Processing Engine
- **Platform** class manages bot lifecycle
- **BotProcessing** executes strategies via `createStrategyRunner`
- **BotManager** handles start/stop operations
- **TradeManager** manages trade execution
- **OrdersStream** / **MarketsStream** - Real-time exchange data

### Event System
Events: `startBot`, `stopBot`, `onBotStarted`, `onBotStopped`, `onExchangeAccountCreated`, `onExchangeAccountDeleted`, `onTradeCreated`, `onTradeCompleted`

### Strategy Execution Flow
1. API call triggers bot start/stop
2. EventBus emits event
3. BotManager processes event
4. BotProcessing creates strategy runner
5. Strategy executes with exchange connection
6. State persisted to DB
7. Logs recorded in BotLog

## Built-in Strategies
- `grid-bot` - Grid trading
- `grid` - Grid variant
- `dca` - Dollar-cost averaging
- `rsi` - RSI indicator-based
- `test/*` - Test strategies

## Extended Prisma Client (xprisma)
- Auto-parses JSON `settings` and `state` fields
- Custom model methods: `setProcessing()`, `updateState()`, `log()`
- Computed `credentials` field on ExchangeAccount
- Type-safe bot queries with `NarrowBotType`

## Key Files
- `/root/opentrader/packages/prisma/src/schema.prisma` - Database schema
- `/root/opentrader/packages/trpc/src/routers/appRouter.ts` - API router definition
- `/root/opentrader/packages/bot/src/server.ts` - Fastify server setup
- `/root/opentrader/packages/bot/src/platform.ts` - Bot orchestration
- `/root/opentrader/packages/bot/src/processing/bot/bot.processing.ts` - Strategy execution
- `/root/opentrader/packages/db/src/xprisma.ts` - Extended Prisma client
- `/root/opentrader/packages/trpc/src/procedures.ts` - Auth middleware
- `/root/opentrader/packages/trpc/src/utils/context.ts` - Request context
