# BlockRun Wallet Recovery — Sakura Session (Jul 30, 2026)

## The Problem

Jordan sent $14.63 USDC to fund the Sakura Muffin petting scene. BlockRun wallet showed $0.00.

## Root Cause

The BlockRun MCP server had been restarted, which created a **new wallet** with a new private key. The old wallet address (`0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8`) was where Jordan had been sending funds historically. The new wallet (`0x8B1a1B98376B5e4A057a69847C26d738BefBf99f`) was empty.

## Wallet Comparison

| Property | OLD Wallet | NEW Wallet |
|----------|-----------|------------|
| Address | `0xebc8c...5972f8` | `0x8B1a1...Bf99f` |
| Private key (first 20 chars) | `0x1fc8b2ed40607e977bb4` | `0x42214892d19c6e54f90d` |
| .session file | `~/.blockrun/.session` (Jun 16) | `~/.hermes/profiles/gentech/home/.blockrun/.session` (Jul 30) |
| Created | Jun 16, 2026 | Jul 30, 2026 |

## Key Discovery

There were **two different `.session` files**:
- `/root/.blockrun/.session` — the OLD key (Jun 16), address `0xebc8c...`
- `/root/.hermes/profiles/gentech/home/.blockrun/.session` — the NEW key (Jul 30), address `0x8B1a1...`

The MCP server was reading the profile-specific copy, not the root copy.

## Resolution Path

Restore the old private key from `/root/.blockrun/.session` into the active `.session` file that the MCP server reads.

## Lesson

Always check the wallet address before asking Jordan to send funds. If the address changed, restore the old key first.
