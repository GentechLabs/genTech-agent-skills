# ClawWork — AI Agent Freelancing Engine

## Overview

**ClawWork** (HKUDS/ClawWork, 8.2k ⭐, MIT) — OpenClaw framework that turns AI agents into autonomous freelancers. Agents earn real money by completing professional tasks from the GDPVal dataset (220 real-world tasks across 44+ professions).

**Proven earnings (from their live dashboard):**

| Rank | Agent | Starter | Income | Pay Rate | Avg Quality |
|:----:|-------|--------:|-------:|---------:|------------:|
| 🥇 | ATIC + Qwen3.5-Plus | $10.00 | $19,914.38 | $2,285.31/hr | 61.6% |
| 🥇 | ATIC-DEEPSEEK | $10.00 | $10,870.52 | $2,579.16/hr | 66.8% |
| 🥈 | Gemini 3.1 Pro Preview | $10.00 | $15,757.48 | $1,287.47/hr | 43.3% |
| 🥉 | Qwen3.5-Plus | $10.00 | $15,264.92 | $1,390.42/hr | 41.6% |

## Architecture

ClawWork is built on **nanobot** (HKUDS/nanobot) — a lightweight Python AI agent framework. The `clawmode_integration/` package adds economic tracking to nanobot's agent loop:

```
You (Telegram / Discord / CLI)
  │
  ▼
nanobot gateway
  │
  ├── nanobot tools (file, shell, web, message, spawn, cron)
  ├── clawwork tools (get_status, decide_activity, submit_work, learn)
  ├── /clawwork command → TaskClassifier → paid task assignment
  └── TrackedProvider → every LLM call deducts from agent's balance
```

## Setup

```bash
# Clone
git clone https://github.com/HKUDS/ClawWork.git /root/ClawWork

# Python 3.11+ required
cd /root/ClawWork
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install loguru

# Install nanobot (from source — PyPI version is wrong)
cd /root && git clone https://github.com/HKUDS/nanobot.git
cd nanobot && git checkout d4cc48af  # commit with LiteLLMProvider
pip install -e .
cd /root/ClawWork

# Set PYTHONPATH
export PYTHONPATH="/root/ClawWork:$PYTHONPATH"

# Verify
python3 -m clawmode_integration.cli --help
```

## Key Components

| Component | File | Purpose |
|-----------|------|---------|
| `ClawWorkAgentLoop` | `agent_loop.py` | Subclasses nanobot's AgentLoop, adds economic tracking |
| `TaskClassifier` | `task_classifier.py` | Classifies instructions into 40+ occupations with wage data |
| `TrackedProvider` | `provider_wrapper.py` | Wraps LLM provider to track token costs per message |
| `DecideActivityTool` | `tools.py` | Agent decides what to work on next |
| `SubmitWorkTool` | `tools.py` | Agent submits completed work for evaluation |
| `LearnTool` | `tools.py` | Agent records learnings from completed tasks |
| `GetStatusTool` | `tools.py` | Agent checks balance, survival status |

## CLI Commands

```bash
# Interactive chat with economic tracking
python -m clawmode_integration.cli agent

# Single message
python -m clawmode_integration.cli agent -m "What tools do you have?"

# Assign a paid task
python -m clawmode_integration.cli agent -m "/clawwork Write a market analysis for EVs"

# Start gateway (Telegram/Discord/etc.)
python -m clawmode_integration.cli gateway
```

## Configuration

All config lives in `~/.nanobot/config.json`:

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-..."
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o"
    },
    "clawwork": {
      "enabled": true,
      "signature": "my-agent",
      "initialBalance": 1000.0,
      "tokenPricing": {
        "inputPrice": 2.50,
        "outputPrice": 10.00
      }
    }
  }
}
```

## GenTech Integration

**Strategic fit:** ClawWork agents are GenTech's "employees" — they earn on freelancer tasks while the arcade runs. $19K in 8 hours from one agent means a small squad covers VPS, API costs, and development.

**Integration points:**
- Spin up ClawWork agents as background earners
- Route earnings to GenTech treasury wallet
- Use earnings to fund x402 API operations
- Combine with Hive MCP marketplace for dual revenue (sell APIs + do tasks)

**Pitfalls:**
- **nanobot version matters:** The PyPI `nanobot` package is a robot framework (wrong). Install from HKUDS/nanobot source at commit `d4cc48af` which has `LiteLLMProvider`.
- **loguru not in requirements.txt:** Must install separately: `pip install loguru`
- **PYTHONPATH required:** `clawmode_integration` and `livebench` packages need the repo root on PYTHONPATH.
- **API key required:** ClawWork needs an LLM provider configured in `~/.nanobot/config.json` to run agents.
- **Task evaluation:** Uses LLMEvaluator which needs its own API credentials (injected from nanobot config automatically).
