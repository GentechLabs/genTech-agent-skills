# Credential Probe API Quirks

API-level details for each credential probe in the harness's `credential-health.sh`.
Use this as a reference when adding new probes or debugging failed ones.

## GitHub (`gh auth status`)

- **Command:** `gh auth status 2>&1`
- **Exit code:** 0 = logged in, 1 = not logged in
- **Edge case:** The `GITHUB_TOKEN` env var takes precedence over stored credentials
  in `~/.config/gh/hosts.yml`. If the env var is stale, `gh` reports "token is invalid"
  even though the stored token is valid. Fix: remove/update the env var in the profile-
  specific `.env` file. See "GITHUB_TOKEN Env Var Override" in SKILL.md.
- **Pitfall for probes:** The probe reads the **display output**, not the exit code
  alone. `gh auth status` can exit 1 with mixed results — one active token invalid
  (env) and one inactive but valid (stored). The probe currently checks the `Logged in`
  text and looks for error patterns like `invalid|401|expired`.

## Telegram (`getMe`)

- **Endpoint:** `GET https://api.telegram.org/bot${TOKEN}/getMe`
- **Auth:** Token in URL path (`bot${TOKEN}/getMe`)
- **HTTP 200:** Token valid
- **HTTP 401:** Token rejected
- **Cost:** Free, no rate limit concerns for periodic probing

## ElevenLabs (`v1/user`)

- **Endpoint:** `GET https://api.elevenlabs.io/v1/user`
- **Auth:** Header `xi-api-key: ${TOKEN}`
- **HTTP 200:** Key valid
- **HTTP 401:** Key rejected
- **Cost:** Free, no rate limit for periodic probing

## BlockRun

- **Status:** SKIP (no free authenticated endpoint)
- The `BLOCKRUN_API_KEY` is embedded in `config.yaml` as an MCP credential, not
  a standalone API key. BlockRun has no free `/auth/verify` endpoint — every API
  call costs USDC. The probe correctly reports `SKIP` with `key_format_valid`
  detail when the key syntax is present in config.
- **Do not attempt to probe BlockRun with a paid call** — the probe runs every
  4 hours and would burn USDC without user benefit.

## Pay Wallet (`pay account list`)

- **Command:** `pay account list 2>&1`
- **Exit code:** 0 even when "No accounts found" (the CLI tool prints the message
  to stdout and exits 0)
- **Key quirk:** The probe checks the output text, not the exit code
- **Keypair location:** `/root/.config/pay/keypair.json` (not `$HOME/.config/pay/`)
- **Root cause of NO_ACCOUNT:** gnome-keyring unavailable in headless Linux.
  `pay account new` requires a keyring backend. Without gnome-keyring, the
  keypair exists but no account is registerable.
- **Detection path:**
  1. Check `pay` CLI exists → SKIP if not
  2. Check `keypair.json` exists → NO_KEYPAIR if not
  3. Run `pay account list` → check for "No accounts found" text
  4. If "No accounts found", check `accounts.yml` for `pubkey:` entries
     → `need_gnome_keyring_backend` detail if pubkey exists but no account

## Q402 Payment Rail

- **Endpoint:** `POST https://q402.quackai.ai/api/keys/verify`
- **Auth:** API key goes in the **JSON body**, NOT an `Authorization` header!
  ```json
  {"apiKey": "q402_live_37..."}
  ```
- **HTTP 200:** Key valid — response includes plan, remaining credits, expiry
- **HTTP 400/401:** Key rejected or expired
- **HTTP 000 (curl timeout):** Relay unreachable
- **Cost:** Free — `verify` endpoint requires no payment
- **Key locations checked:**
  - `/root/.q402/mcp.env` (source of truth for probes)
  - Tries `Q402_TRIAL_API_KEY` first, falls back to `Q402_MULTICHAIN_API_KEY`
- **Status states produced:**
  - `PAY_OK` — healthy, includes plan + credits + expiry in detail
  - `LOW_CREDITS` — credits < 200 (10% of trial allotment)
  - `KEY_EXPIRED` — past expiry date or HTTP 400/401
  - `RELAY_DOWN` — curl returned 000 (connectivity issue)
  - `NO_KEY` — env file exists but no recognizable API key found
  - `SKIP` — no env file at all

## Adding a New Probe — Template

```bash
check_provider() {
    local key
    key=$(grep -oP 'PROVIDER_KEY=\K\S+' /path/to/.env 2>/dev/null || echo "")
    if [[ -z "$key" ]]; then
        _log_status "provider" "SKIP" "no_key_found"
        return 0
    fi

    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 \
        [AUTH_HEADER_OR_BODY] \
        "https://api.provider.com/v1/verify" 2>/dev/null || echo "000")

    if [[ "$http_code" == "200" ]]; then
        _log_status "provider" "200" "probe_ok"
    elif [[ "$http_code" == "401" ]]; then
        _log_status "provider" "401" "key_rejected"
    else
        _log_status "provider" "${http_code}" "unexpected"
    fi
}
```

**Key design rules for probes:**
1. **Zero side effects** — no payments, no state mutations, no rate-limit-sensitive calls
2. **Handle missing CLI** — `command -v` check, return SKIP
3. **Handle missing key** — return NO_KEY/SKIP, not a false 401
4. **Log the actual status** — don't fabricate 200s for format-only checks
5. **One curl call** when possible — avoid fetching the body and the http_code separately
