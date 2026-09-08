# DeFi Model Training Pipeline

## Overview

Fine-tune an open-source LLM on proprietary DeFi data to create a specialized financial advisor model. Revenue via API key selling, x402 micropayments, EvoMap Capsules, and Agent Kit skills.

## Training Data Sources

1. **LP Position History** — AVAX/USDC positions, fee accrual, IL scenarios
2. **Market Reactions** — FOMC events, narrative rotations, macro impacts
3. **Yield Farming Decisions** — When to enter/exit, compound vs extract
4. **Dashboard Metrics** — Portfolio health, risk scores, optimization cues

## Model Selection

| Model | Params | Math Score | Cost to Fine-tune | Best For |
|-------|--------|------------|-------------------|----------|
| DeepSeek R1 Distill (Qwen 32B) | 32B | 85%+ MATH | $30-60 (QLoRA) | ✅ Our choice — reasoning-focused, lighter |
| Qwen3 (30B-A3B) | 30B MoE | - | $20-40 (QLoRA) | Budget option |
| DeepSeek V3.2 | 685B MoE | 90.2% MATH | $50-100 (QLoRA) | Best math, expensive |

## Training Pipeline

### 1. Data Extraction
```bash
python3 extract-training-data.py  # Extract from vault
python3 generate-synthetic-data.py  # Generate synthetic Q&A pairs
python3 combine-training-data.py  # Combine into final dataset
```

### 2. Fine-Tuning (QLoRA)
- **Method:** QLoRA (4-bit quantization + LoRA adapters)
- **Rank:** 16
- **Alpha:** 32
- **Target modules:** q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
- **Epochs:** 3
- **Batch size:** 2 (gradient accumulation: 8)
- **Learning rate:** 2e-4

### 3. Deployment
- **Platform:** BlockRun Modal (A10G GPU)
- **Cost:** ~$30-60 for 1 hour
- **Payment:** USDC on Base (already funded)

## Revenue Models

1. **API Key Selling** (validated by Tao) — sell access via API keys
2. **x402 Micropayments** — $0.01-0.05/query via USDC
3. **EvoMap Capsules** — publish as Capsule, earn credits
4. **Agent Kit Skill** — bundle into premium skill ($10-50)

## Files

- `02-Labs/defi-model/README.md` — Project overview
- `02-Labs/defi-model/extract-training-data.py` — Vault data extraction
- `02-Labs/defi-model/generate-synthetic-data.py` — Synthetic data generation
- `02-Labs/defi-model/combine-training-data.py` — Data combination
- `02-Labs/defi-model/finetune.py` — QLoRA training script
- `02-Labs/defi-model/run-modal.py` — Modal runner
- `02-Labs/defi-model/training-data/` — Training datasets
- `02-Labs/defi-model/model/` — Fine-tuned model output

## Timeline

- **Jun 18-19:** Prep training data ✅ (26 pairs ready)
- **Jun 22 (Sunday):** Run fine-tune (need funds)
- **Jun 23-24:** Test and deploy
- **Jun 25:** Publish to EvoMap + API endpoint

## Pitfalls

- **Training data quality > quantity** — 26 good pairs > 100 noisy pairs
- **QLoRA is cheaper than full fine-tuning** — use 4-bit quantization
- **BlockRun Modal charges per minute** — keep training efficient
- **Test with small sample first** — validate before full run
