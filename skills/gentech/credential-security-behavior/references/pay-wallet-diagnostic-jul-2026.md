# Pay Wallet Diagnostic — July 27, 2026

## Context
The Pay MCP server was configured in Hermes (`mcp_servers.pay` with `PAY_SECRET_KEY_PATH` set to `/root/.config/pay/keypair.json`), and both `keypair.json` and `accounts.yml` existed on disk. But `pay__get_balance` via MCP returned "No account configured for mainnet."

## Root Cause

The `accounts.yml` at `/root/.config/pay/accounts.yml` had a mainnet entry with a pubkey:
```yaml
mainnet:
  name: mainnet
  pubkey: pX1FTLyXAskfD4y8pRwx7Go58GpM9t2PtGZGj6Lq2hR
```

But `pay account list` returned "No accounts found" because:
- `pay account new` requires `--backend gnome-keyring` on Linux
- This headless server has no gnome-keyring daemon
- The account was never registered in a secure keyring backend

## Diagnostic Commands

```bash
pay account list 2>&1
# → "No accounts found. Run `pay account new` to create one."

pay account new mainnet --force 2>&1
# → "Configuration error: No --backend specified and no interactive terminal available."
# → "Pass --backend=<one of 'gnome-keyring'>."

pay setup --update 2>&1
# Re-installs MCP configs for Claude Code and Codex. Does NOT create an account.
# → "Update complete."
```

## Credential Health Probe

The credential-health.sh probe (added in Evolve cycle #4) detects this state:

```bash
check_pay() {
    # 1. Check CLI exists
    # 2. Check keypair.json exists (explicit /root/.config/pay/ path)
    # 3. Check `pay account list` for registered account
    # 4. If no account but keypair exists → NO_ACCOUNT with gnome-keyring detail
}
```

## Implications

- Pay MCP tools (`pay__get_balance`, `pay__curl`, `pay__search_catalog`) are available to the agent but all payment operations will fail until an account is registered
- The keypair is intact and could be used if gnome-keyring were available
- Q402 payments (`q402_pay` etc.) work independently and are unaffected
