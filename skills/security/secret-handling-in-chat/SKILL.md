---
name: secret-handling-in-chat
description: "Protocol for when a user pastes a sensitive credential into chat — API keys, client keys, wallet private keys. Covers store/verify/never-echo, the private-key-in-chat compromise rule, key-privilege triage (client key vs private key), domain-restricting client keys, and coaching the user to stop pasting secrets. Use when a credential arrives as a raw value in a message and must be secured."
category: security
---

# Secret Handling in Chat

When a user pastes a raw credential value (API key, PAT, client key, or wallet private key) into a chat message, the agent must secure it AND calibrate urgency by what type of secret it is. This skill complements the (manually-authored, read-only) `credential-security-behavior` and `agent-security-hardening` skills, which cover the underlying Hermes redaction/scanner mechanics and key-material protection at rest.

## Core protocol — store / verify / never echo

1. **Receive** — key value arrives in a chat message.
2. **Store** — write to a locked-down path with explicit `umask 077` (so it can never be world-readable), `chmod 600`.
3. **Verify** — confirm write via `wc -c` (byte count) and `sha256sum` (record hash for later comparison). **Never `cat` or `read_file` it back** — those always redact or expose.
4. **Never echo the value** back into the conversation. Reference it by name / path only.

Example for a wallet secret:
```bash
install -d -m 700 /root/.blockrun
umask 077 && printf '%s' '<key>' > /root/.blockrun/<wallet-name>-secret
chmod 600 /root/.blockrun/<wallet-name>-secret
wc -c < /root/.blockrun/<wallet-name>-secret   # verify byte count, never cat
sha256sum /root/.blockrun/<wallet-name>-secret # record hash for later comparison
```

## The private-key-in-chat rule (higher stakes than API tokens)

A wallet **private key** pasted into chat is a **compromise event by itself** — chat history is frequently cloud-synced, so the value is exposed regardless of what the agent does afterward. Two obligations:
- Tell the user to **rotate the key / move funds** after the integration is swapped over. Never imply the local copy makes it safe.
- Do not treat it as "handled" just because it was stored to disk.

Proven Aug 4, 2026: Coinbase wallet secret pasted in chat; stored but flagged for rotation.

## Key-privilege triage — don't assume urgency

Not all keys are equal. Before acting, identify the privilege class so the user knows what's actually at risk:

| Key type | Risk | Response |
|---|---|---|
| **Client API key** (e.g. CDP client key — "cannot access portfolios or funds", for RPC/OnchainKit) | Low | Low urgency. **Domain-restrict it** if it'll be used in an app. Rotation can wait. |
| **Server/secret API key** (can touch account data / write) | Medium | Store securely; recommend rotation. |
| **Wallet private key** (moves funds) | High | Compromise event; advise rotation/move funds immediately. |

**Ask what the key is FOR before treating it as an action item.** A CDP client key vs a wallet private key vs a Base wallet pending funding are different actions. Don't assume the most recent key is the one a pending transaction needs.

## Domain-restricting a client key

For client keys that will be used in an app: restrict to exact full domains **before** the app goes live. Enter the full domain without `https://`; **wildcards are not supported**; the key is inert outside allowed domains if it leaks.

## Agent-side echo — the OTHER leak path (not just user pastes)

The user isn't the only source of raw secrets in chat: **the agent's own tool calls leak them too.** Proven Aug 31, 2026: `execute_code` (or `terminal`) ran a command that embedded an API key fetched from a secrets file — and the full command line with the literal key value was echoed back into the conversation transcript via the tool result. Same exposure as a user paste, self-inflicted.

**Rules when handling secrets programmatically:**
- Read secrets **inside** the script's memory (Python reads the file) — never interpolate values into shell command strings, `bash -c "...$KEY..."`, or the code text itself.
- Never print, echo, or `repr()` a credential, even "to confirm it loaded" — print a boolean (`key_found: True`) instead.
- Before running any command that will surface in the transcript, ask: *does this command line contain the secret value?* If yes, restructure until it doesn't.
- If an echo happens anyway, log the incident, flag the key for rotation in the reply, and do not re-print it.

## Coach the user on future pastes (durable preference)

Gently ask the user to **reference secrets by name** ("the CDP client key") instead of pasting raw values into chat. This is a durable workflow preference that prevents repeated exposure. Do not scold — a single calm, clear request.

## Pitfalls

- Do NOT read the secret back (`cat`, `read_file`) even to confirm — always verify indirectly (byte count, hash).
- Do NOT assume a private key is safe because it was stored to a `600` file — chat exposure still requires rotation.
- Do NOT confuse a low-privilege client key with a fund-moving private key when advising the user on urgency.
- Do NOT echo the raw value anywhere in the reply; use the path/name reference only.
- Do NOT build shell commands by interpolating secret values fetched from env/secrets files — the command string lands in tool output and the transcript. Keep secrets inside the script's process memory.
