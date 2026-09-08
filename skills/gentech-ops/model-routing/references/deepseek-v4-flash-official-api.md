# DeepSeek V4-Flash Official API — Live Public Beta (Jul 31, 2026)

**Source:** DeepSeek announcement tweet (2.46M views, 16K likes). Docs: https://api-docs.deepseek.com

## What Changed

- Official API live at `api.deepseek.com` — native **Responses API** support, fully adapted for **Codex CLI**
- Massive agent-capability upgrade over V4-Pro-Preview (Flash-0731 vs Pro-Preview):

| Benchmark | Flash-0731 | Pro-Preview | Δ |
|-----------|-----------|-------------|---|
| DeepSWE | 54.4 | 12.8 | 4.2x |
| Terminal Bench 2.1 | 82.7 | 72.1 | +10.6 |
| Cybergym | 76.7 | 52.7 | +24 |
| Toolathlon-Verified | 70.3 | 55.9 | +14.4 |
| Agents' Last Exam | 25.2 | 16.5 | +8.7 |
| AutomationBench | 25.1 | 12.8 | ~2x |
| DSBench-FullStack | 68.7 | 41.8 | +26.9 |
| DSBench-Hard | 59.6 | 31.1 | +28.5 |

- DeepSeek docs now list **Hermes Agent as an official agent integration** (install → setup → select DeepSeek provider → base URL `https://api.deepseek.com`, model `deepseek-v4-pro`)
- Codex integration: one-click setup script `bash <(curl -fsSL https://cdn.deepseek.com/api-docs/codex-deepseek-setup-en.sh)`; only `deepseek-v4-flash` supports Codex for now (pro expected early Aug)

## Relevance to Gentech

- T1 default tier IS DeepSeek V4 Flash — this is a capability jump for the same tier we use daily
- DEV tier in develop-and-verify pipeline benefits (stronger agentic coding = faster build queue)
- **Open decision (Mess Hall considerations, Jul 31):** switch from Nous provider to direct DeepSeek API (sk- key) for official support/lower cost? Evaluate Z.AI / Ollama Cloud in the same pass.
- Codex delegation path gets a free official upgrade.

## Verification Notes

- Benchmark image footnote: Flash tested with DeepSeek Harness (minimal mode), max tier, topp=0.95, temperature=1.0
- DSBench-FullStack = full-stack web/dev benchmark; DSBench-Hard = coding agent challenges
