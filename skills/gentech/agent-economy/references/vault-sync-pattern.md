# Vault Sync Pattern

## The Problem

Crons read from vault files, but conversation updates don't always sync to the files. Result: morning digest shows stale data.

## The Solution

Every time something changes in conversation, update the vault files IMMEDIATELY. Crons pick it up automatically.

## Files That Must Stay Current

| File | What It Tracks | Who Reads It |
|------|---------------|-------------|
| `00-HQ/current-status.md` | What's done, what's next, blockers | Morning Digest, Build List, To-Do |
| `00-HQ/hackathon-tracker.md` | Hackathon/event status | Morning Digest, Opportunity Scanner |
| `10-Labs/build-queue.md` | Build priorities | Build Queue Review, Workshop |
| `11-Mess Hall/considerations.md` | Pending decisions | Morning Digest, Context Snapshot |

## The Rule

**Conversation → Vault → Crons**

1. Jordan says something in conversation (e.g., "I signed up for Solana Boot Camp")
2. Agent updates the relevant vault file IMMEDIATELY
3. Crons read from vault files and reflect the update

## When to Update

- Jordan confirms submission/signup/completion
- Jordan mentions a new idea or decision
- Build queue items move (pending → done)
- Wallet balances change
- Hackathon status changes

## Pitfalls

- Don't wait for end-of-day to sync — do it in real-time
- Don't assume the vault is current — always check before reporting
- Don't update conversation-only notes — they die with the session
- When in doubt, write it to the vault
