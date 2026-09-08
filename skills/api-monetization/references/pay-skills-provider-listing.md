# Pay Skills (PAY.md) Provider Listing Guide

How to maintain provider listing files in the `solana-foundation/pay-skills` repository. These are the canonical listings agents discover when searching the Solana Pay catalog for paid APIs.

## File Structure

Each provider gets a directory under `providers/<operator>/<name>/` with a `PAY.md` frontmatter file:

```
providers/gentech/
├── agent-discover/PAY.md
├── airdrop-checker/PAY.md
├── games-intel/PAY.md
├── market-intel/PAY.md
├── movie-intel/PAY.md
├── nft-search/PAY.md
├── shipping-tracker/PAY.md
├── token-security/PAY.md
└── wallet-analyzer/PAY.md
```

## PAY.md Frontmatter Format

```yaml
---
name: agent-discover                    # Must match parent directory name
title: "Agent Discovery & Reconnaissance"
description: "Short description (64-255 chars)"
use_case: "When-to-use guidance (64-255 chars)"
category: ai_ml                        # Must be from CONTRIBUTING.md allowed set
service_url: https://...                # Live endpoint URL
openapi:
  content: |                            # Inline OpenAPI 3.1.0 spec as JSON
    { "openapi": "3.1.0", ... }
network: solana                         # Required by registry
accepts:
  - eip155:8453                         # Base
  - solana:mainnet                      # Solana (required by CI gate)
pricing:
  per_request: 0.001                    # USD per call
---
```

## CI Validation Rules (from CONTRIBUTING.md)

### Category Allowed Set (P1 — blocking)
Only these category values pass CI:

`ai_ml` `cloud` `compute` `data` `devtools` `finance` `identity` `maps` `media` `messaging` `other` `productivity` `search` `security` `shopping` `storage` `translation`

**Common invalid values Greptile catches:**
- `entertainment` → use `media` (for game/movie content)
- `nft` → use `other` or `finance`
- `logistics` → use `other`
- `travel` → use `maps`
- `ai-agents` → use `ai_ml`
- `wallets` → use `finance`

### OpenAPI Spec Requirements (P1 — blocking)
- Each PAY.md must include either `openapi:` with inline spec or an `openapi.json` file committed alongside
- Inline specs must have **real path entries** — empty `"paths": {}` causes the build to generate no-op listings
- Each path entry needs at minimum: method, parameters, response schema, and a 402 response description
- The `x-payment-info` price `amount` must be a valid numeric string (`"0.001"`), NOT `"NaN"` — NaN silently bypasses x402 middleware
- The `x-payment` network must include Solana mainnet (`solana:mainnet` or `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp`) for the Solana-compat CI gate

### Network Requirement (P1 — blocking)
- Every paid endpoint must accept payment on **Solana mainnet**
- The CI runs a `--strict` Solana-compat gate that upgrades non-Solana warnings to blocking errors
- Dual-chain (Solana + Base) is accepted; Solana-only is fine; Base-only is blocked

### Naming Requirements
- `name:` in frontmatter must match the parent directory name exactly
- `name:` is used as the listing slug — mismatch breaks registry links

## Common Greptile CI Failures

### 1. `"amount": "NaN"` in x-payment-info (P1)
**Symptom:** Every x-payment-info price block has `"amount": "NaN"`
**Cause:** Generation artifact — price was not mapped from frontmatter to inline OpenAPI spec
**Fix:** Replace literal `"NaN"` with the actual price string matching `pricing.per_request`:
```json
"x-payment-info": {
  "price": {
    "mode": "fixed",
    "currency": "USD",
    "amount": "0.001"
  }
}
```
**Check after fix:** `grep -c '"NaN"' providers/gentech/*/PAY.md` → should be 0

### 2. Invalid category values (P1)
**Symptom:** CI shape validation rejects files using non-allowed category strings
**Fix:** Map to the valid category from the allowed set above
**Check after fix:** `grep 'category:' providers/gentech/*/PAY.md` — every value must be in the allowed set

### 3. Literal `\n` in markdown tables (P1)
**Symptom:** Endpoint tables render as broken single-line rows with visible `\n` characters
**Cause:** Generation artifact — `\n` escape sequences end up as literal bytes in the output
**Fix:** Strip trailing `\n` bytes from the end of files and replace any `\n` in table rows with actual newlines:

With Python:
```python
content = content.replace(b'\\n', b'')
```
Or with grep/sed over binary-safe mode.

### 4. Empty OpenAPI `paths: {}` (P1)
**Symptom:** "Empty OpenAPI paths makes every listing a no-op in the registry"
**Fix:** Each path entry needs at minimum method, parameters, responses (including a 402 response)

### 5. GET used for state-creating operations (P2)
**Symptom:** Greptile flags GET endpoints that create state (e.g. `GET /v1/wallet/deploy`)
**Fix:** Use POST for all operations that accept body input or create state

### 6. Zero-price endpoint (P2)
**Symptom:** An endpoint is priced at `$0.0` — won't trigger x402 payment challenge
**Fix:** Use a concrete non-zero price or mark the endpoint as genuinely free (remove x-payment-info)

## Workflow for Updating Provider Listings

1. **Clone the forked repo** — `git clone https://github.com/ProtoJay4789/pay-skills.git`
2. **Make changes in `providers/gentech/*/PAY.md`**
3. **Run the static check** — `cd pay-skills && npx pay catalog check` (or verify with `npx pay catalog check --strict`)
4. **Commit with descriptive message** covering which files changed and why
5. **Push to fork** — `git push origin main`
6. **Wait for Greptile re-review** — the bot re-reviews every push to the PR branch

### Quick Verification After Making Changes
```bash
# Check for NaN amounts
grep -c '"NaN"' providers/gentech/*/PAY.md
# Expected: 0 for all files

# Check categories
grep 'category:' providers/gentech/*/PAY.md
# Every value must be in the allowed set

# Check literal \n
grep -c '\\\\n' providers/gentech/*/PAY.md
# Expected: 0 for all files

# Check network includes Solana
grep -A1 'network:' providers/gentech/*/PAY.md
# Expected: "network: solana"

# Check file count
ls -d providers/gentech/*/
# Should match expected provider count
```

## Handling Maintainer Feedback

When a maintainer (e.g. @lgalabru) comments:
1. Address each issue individually with commits
2. Rebase on upstream/main before pushing
3. Respond on the PR thread summarizing what was fixed
4. Wait for Greptile auto-re-review on the new commit
5. Check the CI status badge before asking for re-review

## Reference
- `CONTRIBUTING.md` in the pay-skills repo for the full allowed category list and CI rules
- Greptile bot auto-reviews every push — fix all P1s before requesting re-review

## Editing Inline JSON Inside YAML Literal Blocks

The OpenAPI spec in each PAY.md is stored as a YAML **literal block scalar** (`|`): JSON-as-text that preserves newlines and indentation. Editing this inline JSON programmatically is tricky because YAML literal blocks terminate on under-indented lines.

### The Problem

A literal block scalar's indentation is set by the **first content line**. Any line with less indentation terminates the block — the YAML parser resumes reading frontmatter keys and a `]` or `}` at column 0 breaks the parse.

### Working Approach

1. **Extract the JSON** via regex — find the block after `openapi:\n  content: |\n`
2. **Parse with `json.loads()`** — the JSON is valid, just embedded in a string
3. **Modify the Python dict** (add parameters, fix amounts, netorks, categories)
4. **Re-serialize with `json.dumps(indent=4)`** — use 4-space nested indent
5. **Re-indent all lines** to match the YAML block baseline (typically 4 spaces)
6. **Replace in the file**

```python
import re, json

def edit_openapi_in_pay_md(filepath, modifier_fn):
    with open(filepath) as f:
        content = f.read()
    m = re.search(r'openapi:\s*\n\s+content:\s*\|\s*\n', content)
    start = m.end()
    lines = content[start:].split('\n')
    indent = len(lines[0]) - len(lines[0].lstrip())
    json_lines = []
    for line in lines:
        if line.strip() == '':
            json_lines.append(line); continue
        li = len(line) - len(line.lstrip())
        if li < indent and line.strip(): break
        json_lines.append(line)
    spec = json.loads('\n'.join(json_lines))
    spec = modifier_fn(spec)
    new = json.dumps(spec, indent=4)
    indented = '\n'.join(' ' * indent + line for line in new.split('\n'))
    content = content[:start] + indented + content[start + len(json_text):]
    with open(filepath, 'w') as f: f.write(content)
```

### Failed Approaches

| Approach | Failure | Symptom |
|----------|---------|---------|
| String insert between x-payment-info and responses | Brace-tracking off-by-one | `},,\n"responses"` — double comma, invalid JSON |
| `json.dumps(indent=N)` without re-indent | Closing brackets at column 0 | YAML error: "expected block end, but found ']'" |
| `ruamel.yaml` round-trip | Second `---` delimiter starts new YAML document | ComposerError: "found another document" |
| `yaml.safe_load()` on whole file | Multi-document stream with second `---` | YAML error on second document start |

### Script

`scripts/pay-skills-fix-openapi-params.py` in this skill directory can add parameter definitions to any GET endpoint in a PAY.md. Adapt the `modifier_fn` for other edits (amounts, categories, networks).
