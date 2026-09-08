# ClawWork / LiveBench Agent — Setup & Run (proven Aug 17, 2026)

ClawWork (HKUDS/ClawWork) runs an **economic survival simulation** (LiveBench) where an
agent must earn income by completing GDPVal professional tasks, pay its own token costs,
and stay solvent. It is a **benchmark**, NOT a real income source — see the honest-numbers
pitfall in the parent SKILL.md before presenting any "earnings" from it.

## What it proves
- The agent can do real professional work (research, document creation, analysis) end-to-end.
- A `gentech-qwen-ollama` (qwen3.5:397b) run survived 3 days, earned $337.78 *simulated*
  USDC, best single task $226.99 (glueball editorial, score 0.90). All fake money.

## Setup (venv, not conda — no conda on the VPS)
```bash
cd /root/ClawWork
/usr/bin/python3 -m venv .venv-livebench
. .venv-livebench/bin/activate
pip install -q -r requirements.txt
# GDPVal dataset (220 tasks) — required, not in the repo:
pip install -q huggingface_hub
python -c "from huggingface_hub import hf_hub_download; import shutil; \
  p=hf_hub_download('openai/gdpval','data/train-00000-of-00001.parquet',repo_type='dataset'); \
  shutil.copy(p,'gdpval/data/train-00000-of-00001.parquet')"
```

## Run
```bash
cd /root/ClawWork
. .venv-livebench/bin/activate
export PYTHONPATH="/root/ClawWork:$PYTHONPATH"
set -a && . ./.env && set +a
export EVALUATION_MODEL="deepseek-v4-flash:0731"   # CRITICAL — see fix 1
python livebench/main.py livebench/configs/test_gentech_qwen_ollama.json
```

## The three fixes that unlocked real work (all durable)
1. **EVALUATION_MODEL must be a proxy-available model.** The evaluator defaults to
   `gpt-4o`, which 404s on our local proxy (`127.0.0.1:8011`). Set it to a model the
   proxy actually serves (e.g. `deepseek-v4-flash:0731`). Without this, every submission
   fails with `model "gpt-4o" not found` and no work is ever evaluated/paid.
2. **PyPDF2 missing silently disables ALL productivity tools.** `livebench/tools/productivity/__init__.py`
   imports `PyPDF2` at module load; if it's absent, the whole `from livebench.tools.productivity import ...`
   in `direct_tools.py` raises ImportError → `PRODUCTIVITY_TOOLS_AVAILABLE=False` → the agent
   has NO `create_file`/`read_file`/`execute_code` and can only do text. `pip install PyPDF2`.
   Verify: `python -c "from livebench.tools.productivity import create_file, execute_code_sandbox, read_file, create_video, read_webpage, search_web; print('OK')"` → should print OK and `get_all_tools()` should return 10 tools.
3. **boxlite sandbox needs KVM; the pyo3 panic escapes `except Exception`.** On a VPS
   without `/dev/kvm`, `execute_code` raises a `pyo3_runtime.PanicException` (a
   `BaseException`, NOT an `Exception`) that crashes the whole run. Fix: change
   `except Exception` → `except BaseException` in BOTH
   `livebench/tools/productivity/code_execution_sandbox.py` (the `execute_code` wrapper)
   AND `livebench/agent/wrapup_workflow.py` (`_list_artifacts_node`). The agent then
   degrades gracefully — `execute_code` returns a clean error and the agent falls back to
   `create_file`/`read_file`/`search_web`, which don't need the sandbox. (For full
   code-execution capability you'd need an E2B_API_KEY or a KVM-enabled host.)

## Pitfalls
- **Reset agent state between runs.** The agent persists `livebench/data/agent_data/<sig>/`
  and skips already-completed dates. To re-run fresh: `rm -rf livebench/data/agent_data/gentech-qwen-ollama`
  (back it up first if you want the prior run's logs).
- **`framework` enum** — `hermes` is rejected; use `custom` (same as AgentLux).
- **The simulation is NOT a revenue stream.** Do not wire its "earnings" into the treasury
  or present them as real income. It is a capability proof for grants/listings only.
