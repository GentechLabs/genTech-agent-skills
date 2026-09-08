# Monid × Context.dev — Jul 29, 2026

## Overview

**Monid** (monid.ai) is "OpenRouter for agent tools" — one integration gives agents access to 1,300+ tools across 13+ providers. Pay-per-call, no subscriptions, one balance.

**Context.dev** is their web scraping/crawling partner — turns any URL into clean structured data (markdown, HTML, JSON, brand kits, screenshots, etc.).

## Key Details

- **Supports:** Claude, Codex, Cursor, **Hermes** (we're listed in their "works with" section), and others.
- **Three connection methods:** Skill (one line into agent chat), MCP (remote MCP server), CLI (terminal install).
- **x402 support:** Their docs have a dedicated page at `/guide/pay-with-x402`. They already speak our protocol.
- **$1 free credit** to start — low risk to try.

## Tool Provider Program

- "Become a tool provider" at bottom of homepage
- Google Form to apply: `https://forms.gle/NLPchCCwnTP6zQhV8`
- They route agent traffic, meter calls, share revenue
- Already lists **Blockrun** — they're in our ecosystem

## What We'd List

| Service | Endpoint | Price |
|---------|----------|-------|
| Yield Rainbow Data | `api.gentechlabs.net/yield-rainbow` | ~$0.01/call |
| Narrative Rotation | `api.gentechlabs.net/narrative` | ~$0.01/call |
| GTA Arb Scan | `api.gentechlabs.net/arb` | ~$0.01/call |
| Agent Treasury Report | `api.gentechlabs.net/treasury` | ~$0.02/call |

## Why This Matters

1. **Firecrawl replacement** — Context.dev does what Firecrawl did (scrape web pages into clean data). No credits to exhaust, pay-per-call.
2. **We could list on Monid as a tool provider** — Our x402 gateway services could be listed in their 1,300+ tool catalog. Agents using Monid could discover and pay for GenTech's DeFi intelligence.
3. **They already list Blockrun** — so they're in our ecosystem. Listing our services alongside Blockrun makes sense.

## Decision

**Apply as tool provider** — Fill out the Google Form to list our x402 gateway services. This puts us in front of every agent using Monid's platform.
