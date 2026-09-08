# Build Queue JSON Schema (canonical)

Source of truth: `/root/vaults/gentech/scripts/build_queue.json`
Human-readable mirror: `/root/vaults/gentech/10-Labs/build-queue.md` (renumber rows there separately!)

## Item shape

```python
{
  "id": 32,                        # next sequential: max(existing ids) + 1
  "name": "Model Strength Score — score trained models 0-850 for marketplace",
  "difficulty": "easy|medium|hard",
  "priority": "urgent|high|medium|low|none",
  "status": "pending",             # pending|in_progress|shipped|cancelled
  "assigned_to": "gentech|jordan",
  "platform": "any|cloud",
  "needs_jordan": true,            # true when human action required
  "human_gated": true,             # usually mirrors needs_jordan
  "gate_type": "greenlight|decision",
  "detail": "Full description: what, why, revenue model, spec path, what Jordan must do.",
  "recommended_tier": "k3"         # model routing hint, optional
}
```

Top-level keys: `version`, `summary` (total/shipped/in_progress/pending/
blocked/cancelled/needs_jordan), `items`, `consolidation_notes`, `agents`,
`note`, `updated`, `gate_summary` (human_gated/decision_gated/autonomous),
`model_strategy`.

## Add-item recipe (verified Aug 2026)

```python
import json
path = '/root/vaults/gentech/scripts/build_queue.json'
with open(path) as f:
    data = json.load(f)
existing_ids = [it.get('id') for it in data['items']]
# ... append item with id = max(existing_ids) + 1 ...
data['version'] += 1
data['updated'] = 'YYYY-MM-DD'
data['summary']['total'] = len(data['items'])
data['summary']['pending'] = sum(1 for it in data['items'] if it.get('status') == 'pending')
data['summary']['needs_jordan'] = sum(1 for it in data['items'] if it.get('needs_jordan'))
with open(path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

## Verification

```bash
python3 -c "
import json
data = json.load(open('/root/vaults/gentech/scripts/build_queue.json'))
ids = [it['id'] for it in data['items']]
assert ids == list(range(1, len(ids) + 1)), f'IDs not sequential: {ids}'
print('OK — sequential', len(ids), 'items')
"
```

## Pitfall: mirror drift

`10-Labs/build-queue.md` is a plain markdown table. Inserting a row requires
renumbering ALL following rows in that file — the mirror numbering does NOT
track the JSON automatically. (Aug 2026: JSON got #32 while mirror already had
its own #32 → duplicate row until fixed to #33.)
