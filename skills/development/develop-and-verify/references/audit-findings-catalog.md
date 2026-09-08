# Audit Findings Catalog

Real bugs caught by Kimi K2.7 / Claude Opus 4.8 review sessions.
Use as a reference checklist during Phase 3 (AUDIT).

## CWE-338: Weak Randomness for Identifiers

**Symptom:** `random.randint(0, 99999)` or `hash(str(ts)) % 10000` for scan IDs, request IDs, or any enumerable identifier.

**Risk:** Predictable + collision-prone. An attacker can enumerate scan reports, payment requests, or session tokens.

**Fix:** `secrets.token_hex(16)` or `uuid.uuid4()`.

**Caught in:** Agent Rug 2.0 Phase 5 — `full_scan.py` scan ID generation.

## CWE-1333: ReDoS via Unbounded Regex on User Input

**Symptom:** Regex patterns with unbounded quantifiers (`{20,}`, `{6,}`) run against user-controlled input without length truncation. Classic amplifiers: `[a-zA-Z0-9\s]{20,}` (whitespace class backtracking), `[^\s]{6,}` (greedy over large inputs).

**Risk:** Resource exhaustion. A crafted long description can cause catastrophic backtracking.

**Fix:**
1. Truncate input before scanning: `text[:MAX_LEN]` (e.g. 8192).
2. Add upper bounds to quantifiers: `{16,256}` instead of `{16,}`.
3. Pre-compile all patterns at module load so compilation cost is paid once.

**Caught in:** Agent Rug 2.0 Phase 5 — all `_check_asi*` functions scanning tool descriptions.

## CWE-117: Log Injection

**Symptom:** User-controlled input (agent IDs, URLs, headers) interpolated into log messages via f-strings or `%s` without sanitization. Newlines/CRLF in the input forge fake log lines.

**Fix:**
```python
safe = str(user_input).replace("\n", "\\n").replace("\r", "\\r")[:128]
logger.info("Event for %s", safe)  # parameterized, not f-string
```

**Caught in:** Agent Rug 2.0 Phase 5 — `agent_id` in `run_full_scan` log line.

## Missing Exception Isolation in Orchestrators

**Symptom:** A single `try/except` wrapping multiple independent sub-operations. If sub-scan A fails, sub-scans B and C never run.

**Fix:** Wrap each sub-operation in its own `try/except`. Log with `exc_info=True`, set the result to `None`, and let downstream checks handle `None` gracefully.

**Caught in:** Agent Rug 2.0 Phase 5 — `run_full_scan()` calling `verify_agent`, `scan_mcp_server`, and `audit_x402_endpoint`.

## Wrong Chain ID in Payment Configuration

**Symptom:** Hardcoded chain ID that doesn't match the target blockchain. E.g., `INJECTIVE_NETWORK = "eip155:888"` (Wanchain) when Injective mainnet is `eip155:2525`.

**Risk:** Payments target the wrong chain. Funds sent to the correct address but on the wrong network — unrecoverable.

**Fix:** Make chain ID configurable via env var with a verified default. Document the correct chain ID in comments and README. Add a test that asserts the expected value.

```python
INJECTIVE_NETWORK = os.getenv("X402_NETWORK", "eip155:2525")  # Injective mainnet
```

**Caught in:** Injective iAgent x402 Integration (Jul 22, 2026) — Kimi K2.7 audit.

## Missing Address Format Validation in Payment Config

**Symptom:** `pay_to` address accepted without format validation. A misconfigured value (whitespace, wrong address format like `inj1...` for an EVM scheme) passes the `if not addr` check and routes payments to a garbage address.

**Risk:** Payments sent to unrecoverable addresses. Silent failure — no error until funds are lost.

**Fix:** Pre-compile an EVM address regex at module load and validate before accepting the config:

```python
import re
_EVM_ADDR = re.compile(r"^0x[a-fA-F0-9]{40}$")

def _valid_evm_address(addr: str) -> bool:
    return bool(_EVM_ADDR.match(addr.strip()))
```

Validate in `load_x402_config()` and return `False` (fail closed) on mismatch.

**Caught in:** Injective iAgent x402 Integration (Jul 22, 2026) — Kimi K2.7 audit.

## Missing URL Scheme Validation in Payment Config

**Symptom:** Facilitator URL accepted without scheme validation. `file://`, `http://`, or arbitrary protocols passed directly into `HTTPFacilitatorClient`.

**Risk:** SSRF via malicious facilitator URL. Misconfiguration routes payments through an unintended facilitator.

**Fix:** Pre-compile an HTTPS URL regex and validate before accepting:

```python
_HTTPS_URL_RE = re.compile(r"^https://[a-zA-Z0-9][a-zA-Z0-9.-]+[a-zA-Z0-9](:\d+)?(/.*)?$")

def _valid_https_url(url: str) -> bool:
    return bool(_HTTPS_URL_RE.match(url.strip()))
```

**Caught in:** Injective iAgent x402 Integration (Jul 22, 2026) — Kimi K2.7 audit.

## Fail-Open Payment Config (Defaulting to Public Facilitator)

**Symptom:** `os.getenv("X402_FACILITATOR_URL", "https://public-facilitator.example.com")` silently defaults to a third-party facilitator when the operator forgets to set the env var.

**Risk:** An operator who forgot to configure their own facilitator unknowingly trusts an external facilitator to verify their payments. Payment verification is outsourced by accident.

**Fix:** Fail closed — require explicit configuration. No default value for security-sensitive URLs:

```python
raw_facilitator = os.getenv("X402_FACILITATOR_URL", "")
if not raw_facilitator or not raw_facilitator.strip():
    logger.error("X402_FACILITATOR_URL not set. Must be configured explicitly.")
    return False
```

**Caught in:** Injective iAgent x402 Integration (Jul 22, 2026) — Kimi K2.7 audit.
