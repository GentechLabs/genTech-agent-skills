# OpenAPI Parameters Injection Pattern — Pay-Skills Catalog

**When**: A pay-skills catalog PR's canonical `openapi.json` is missing `parameters` arrays on paid endpoints. Greptile flags this as "endpoints impossible to call correctly from the spec."

**Context**: The pay-skills `openapi.json` is typically a single-line (minified) file. Opening it in an editor, identifying the insertion point for each of 16 endpoints, and manually editing is error-prone. Use programmatic injection instead.

## Prerequisites

- The fork is cloned with the PR branch checked out
- Python 3 available (included in standard Hermes environment)

## Step-by-Step

### 1. Read the minified spec and identify all paths

```python
import json
with open('providers/gentech/x402-gateway/openapi.json') as f:
    spec = json.load(f)

# Print all paths to plan parameter schemas
for path in spec.get('paths', {}):
    print(path)
```

### 2. Design parameter schemas per endpoint category

Three common patterns for pay-skills endpoints:

| Pattern | Endpoints | Required Param | Optional Params |
|---------|-----------|----------------|-----------------|
| **Search** | `/search`, `/cheapest`, `/news`, `/details`, `/trailers` | `q` (string) | `category` (enum), `page` (int), `year` (int), `region` (enum) |
| **Blockchain** | `/wallet/analyze`, `/token/risk`, `/airdrops/check`, `/agentscan` | `wallet`/`mint`/`agent` (string) | `chain` (enum with default) |
| **Tracking** | `/shipping/track` | `tracking` (string) | `carrier` (enum) |

### 3. Build the parameter definitions dict

```python
param_defs = {
    "/api/games/search": [
        {"name": "q", "in": "query", "required": True,
         "schema": {"type": "string"},
         "description": "Game title search query"},
        {"name": "category", "in": "query", "required": False,
         "schema": {"type": "string", "enum": ["all", "pc", "playstation", "xbox", "nintendo"]},
         "description": "Platform category filter"},
    ],
    # ... repeat for each endpoint
}
```

**Rules**:
- Every paid endpoint that accepts user input MUST have at least a `q` (required string) parameter
- Optional parameters MUST have a `default` value so x402scan's `@agentcash/discovery` probe knows what to send
- Use `enum` constraints documented in the actual service (not invented values)
- Path parameters (`{id}`, `{mint}`) can be `required: true` — the scanner handles URL templating

### 4. Inject parameters and re-serialize compact

```python
for path, methods in spec['paths'].items():
    for method, op in methods.items():
        if not isinstance(op, dict) or method.startswith('x-'):
            continue
        if path in param_defs:
            op['parameters'] = param_defs[path]

# Write with minified format (no spaces — matches pay-skills convention)
output = json.dumps(spec, separators=(',', ':'))
with open('providers/gentech/x402-gateway/openapi.json', 'w') as f:
    f.write(output)
    f.write('\n')
```

### 5. Verify no duplicate keys were introduced

```python
import json
with open('openapi.json') as f:
    d = json.load(f)

duds = []
for path, methods in d.get('paths', {}).items():
    for method, spec_op in methods.items():
        if isinstance(spec_op, dict):
            count = sum(1 for k in spec_op if k == 'parameters')
            if count > 1:
                duds.append(f'{path} ({method}): {count} parameters blocks')

if duds:
    print('❌ DUPLICATE KEYS:', duds)
else:
    print('✅ No duplicate keys')
```

### 6. Verify all 16 endpoints have parameters

```python
all_ok = True
for path in param_defs:
    if path in spec['paths']:
        for m, op in spec['paths'][path].items():
            if isinstance(op, dict):
                params = op.get('parameters', [])
                if len(params) == 0:
                    print(f'❌ {m.upper()} {path}: 0 params')
                    all_ok = False
                else:
                    print(f'✅ {m.upper()} {path}: {len(params)} params')
if all_ok:
    print('All endpoints have parameters')
```

### 7. Commit and push

```bash
git add providers/gentech/x402-gateway/openapi.json
git commit -m "fix: add required parameters arrays to all N endpoints in canonical OpenAPI spec"
# For a feature branch on a personal fork where remote has diverged:
git push --force origin <branch-name>
```

## Pitfalls

- **Force push is OK on personal forks** — There's only one author on the branch. Force-pushing replaces the old commit with the fixed one. Greptile auto-re-scans on the new commit.
- **Minified JSON must stay minified** — Pay-skills convention is single-line `openapi.json` files. Don't indent the output. Use `json.dumps(spec, separators=(',', ':'))` (no spaces).
- **Greptile won't re-trigger on force-push** — the bot scans the new commit's OID. If the OID changes via force-push, the old Greptile review still points to the old OID. The bot re-scans on the new OID's first appearance. Give it a few minutes.
- **Verify the commit landed** — After push, run `gh pr view <number> --json commits --jq '.commits[-1].oid'` to confirm the new commit is visible on the PR branch. If it shows the old OID, the push didn't reach the PR's head ref.
