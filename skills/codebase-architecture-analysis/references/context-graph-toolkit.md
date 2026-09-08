# Repo-Context Graph Toolkit — Implementation Notes (shipped Aug 5 2026, queue #35)

Working pure-stdlib tools at `scripts/context-graph/`. These notes capture the
non-obvious details learned while building and verifying them, so future edits
don't reintroduce the bugs.

## The three tools

- `repo_map.py <repo>` — walks the repo (skips JUNK_DIRS), extracts per-file
  header (leading docstring/comment block) + crux lines + sibling imports,
  writes `.repo-map/{repo-map.md, graph.json, fingerprint.json}`.
- `repo_map_check.py <repo> [--rebuild]` — hashes current files vs
  `fingerprint.json`; exit 0 fresh / 1 drifted / 2 no map.
- `blast_radius.py <repo> <target> [--transitive]` — reads `graph.json`,
  prints direct dependents (and transitive closure).

## Import-resolution pitfalls (each cost a debug cycle)

1. **Python dotted imports collapse to a single name if you only take
   `split(".")[0]`.** `from injective_functions.bank import x` becomes
   `injective_functions` for EVERY file → useless noise in `depends_on`.
   Fix: walk the dotted path longest-first and return the longest prefix that
   resolves to a file/dir/`__init__.py` inside the repo
   (`_resolve_py_module`). Then `bank` resolves to `injective_functions.bank`.

2. **JS relative imports need the extension stripped AND existence-checked.**
   `from './rig.js'` → `spec.split('/')[0]` yields `'.'`, not `rig`. Fix:
   `norm = spec.lstrip('./')`, take the first segment, strip `.js/.ts`, then
   verify it resolves (`os.path.exists` on the file OR `<extless>.js` OR
   `<extless>.ts`) before recording the dependency. Same-dir, bare, and
   index-level (`./nav` → `nav.js`) all need to work.

3. **JS blast-radius needs the bare basename stem as a lookup key.** `used_by`
   is keyed by the module name JS imports by (`app`), but `_module_keys` only
   produced `web.app`/`web/app`. Add the bare `os.path.basename(base)` stem so
   `blast_radius web/app.js` still finds the `app` key. Symptom of the miss:
   exit 2 "no dependents found" on a file that IS depended on.

## Semantics worth knowing

- **True negatives are real.** A repo of standalone action scripts (e.g.
  gold-402, where each script reads `services.json` directly, no cross-imports)
  legitimately reports "no dependents". That's correct — don't chase it as a bug.
- **Drift includes uncommitted edits.** `repo_map_check` hashes the live
  filesystem, so `graft check`-style "fail loudly on drift" catches any change,
  not just committed ones. `--rebuild` restores freshness in one step.
- **Crux is regex-driven, not LLM.** `_CRUX_RE` catches top-level
  defs/classes/returns/throws/emits; `_SIGNAL_RE` catches high-value tokens
  (secrets/uuid/hashlib/verify/signature/payTo/402). Keeps it `$0` and offline.

## Verification recipe (reuse when touching the toolkit)

```bash
cd /root/vaults/gentech/scripts/context-graph
python3 test_context_graph.py          # 3/3 pass (build, staleness, blast-radius)
python3 repo_map.py /root/iagent-x402  # real-repo smoke; then
python3 repo_map_check.py /root/iagent-x402        # expect FRESH exit 0
python3 blast_radius.py /root/iagent-x402 injective_functions/utils/helpers.py --transitive  # 8 direct/12 transitive
```

Always re-run the test suite + one real-repo smoke after editing `repo_map.py`
or `blast_radius.py` — the import-resolution regexes are easy to break silently.
