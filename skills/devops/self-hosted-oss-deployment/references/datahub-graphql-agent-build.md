# DataHub GraphQL Agent-Build Pattern (Aug 3 2026)

How to build an agent that reads a DataHub metadata graph and does real work with it —
the "Agents That Do Real Work" + "Use of DataHub (contribute back)" hackathon tracks.
Companion to `datahub-self-host-deployment.md` (getting the stack running). Proven on the
DataHub Agent Hackathon ($20.5K, Aug 10): the **Lineage Guard** agent
(`/root/datahub-agent-build/lineage_guard.py`).

## The winning shape: read → reason → act → contribute back

The agent answers a real question ("what breaks if I drop/change this table?"), walks
lineage to compute blast radius, classifies assets by severity, issues a verdict
(BLOCK / REVIEW / SAFE), and persists the assessment back to the graph. The write-back is
what scores "Use of DataHub / contribute back" — read-only agents miss that criterion.

## DataHub GraphQL — the working schema (verify via introspection if a query 404s)

DataHub exposes a GraphQL API at `<GMS>/api/graphql`. Use `__type(name: "...") { fields }`
to introspect — field names are NOT what you'd guess.

Confirmed (v1.5.0.6, Aug 2026):
- **Search field is `searchResults`, NOT `results`** (and NOT `entities`):
  ```graphql
  { search(input: { type: DATASET, query: "*", start: 0, count: 5 })
      { total searchResults { entity { urn } } } }
  ```
- **Lineage field is `relationships`, NOT `relations`**; the arg is `input:{direction,start,count}`:
  ```graphql
  { dataset(urn: "...") {
      lineage(input: { direction: DOWNSTREAM, start: 0, count: 100 })
        { total relationships { type entity { urn } degree } } } }
  ```
- `LineageRelationship` fields: `type, entity, degree, createdOn, createdActor, updatedOn, updatedActor, isManual, paths`
- `EntityLineageResult` fields: `start, count, total, filtered, relationships`
- Dataset entity name via `... on Dataset { properties { name } }`; charts/dashboards via
  `... on Chart { properties { name } }` / `... on Dashboard { properties { name } }`.
  Best-effort resolve friendly names per-URN with an `entity(urn:"...") { ... }` call.

## Blast-radius walker (the core)

```python
def blast_radius(urn, direction="DOWNSTREAM", depth=0, max_depth=5, seen=None, results=None):
    if seen is None: seen, results = set(), {}
    if depth > max_depth or urn in seen: return results
    seen.add(urn)
    data = gql('{ dataset(urn: "%s") { lineage(input: { direction: %s, start: 0, count: 100 }) { total relationships { type entity { urn } degree } } } }' % (urn, direction))["data"]["dataset"]
    for rel in (data or {}).get("lineage", {}).get("relationships", []):
        ent = rel["entity"]["urn"]
        results[ent] = {"urn": ent, "type": entity_type(ent), "name": friendly_name(ent)}
        blast_radius(ent, direction, depth+1, max_depth, seen, results)
    return results
```

Severity model (map entity type → blast impact): DASHBOARD=critical, CHART/DATAFLOW/ML_MODEL=high,
DATASET/DATAPROCESS/NOTEBOOK=medium, TAG/GLOSSARY_TERM=low. Verdict: BLOCK if any high/critical
downstream, REVIEW if any downstream, else SAFE.

## Pitfalls

- **Per-URN GraphQL calls are SLOW on a cold graph.** A `--scan` mode that walks every
  dataset's full tree timed out (>180s). Prefer targeting known hub datasets (e.g. the
  PowerBI `Customer_Analytics_Measures` fed 5 charts+dashboard) or use `--search` to find
  a dataset by name, then walk it. Avoid naive full-graph scans.
- **URNs are ugly** — friendly names need the `entity(urn:...)` lookup, not the URN tail
  (which for charts/dashboards is a UUID). Always resolve display names before showing output.
- **Load sample data first:** `datahub datapack load showcase-ecommerce` → 1,049 entities,
  53 datasets with downstream lineage — rich enough for a compelling blast-radius demo.
- **24/7 VPS is an asset for judges** — a live local DataHub instance (isolated on a
  remapped port) means judges can hit the real graph, not a mock. Keep the rebuild recipe
  in the repo so the stack is one command to restart.

## Monetization angle (differentiator)

Wrap the agent behind our x402 gateway as a pay-per-query endpoint — no other submission
to a data-platform hackathon will have a *paid* lineage-agent. See `api-monetization`.
