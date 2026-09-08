# Kimi K3 — Free via OpenCode Go (verified Aug 15, 2026)

## Verdict
Kimi K3 is reachable at **$0 cost** through our existing **OpenCode Go** provider — no new key, no signup, no Ollama credit burn. This is the best free route when Ollama Cloud's weekly cap is being conserved.

## Live verification (Aug 15, 2026)
Direct API call succeeded and reported `"cost":"0"`:

```bash
KEY=$(grep -oE 'OPENCODE_GO_API_KEY=.*' ~/.hermes/profiles/gentech/.env | cut -d= -f2)
curl -s -X POST "https://opencode.ai/zen/go/v1/chat/completions" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"kimi-k3","messages":[{"role":"user","content":"Reply with exactly: KIMI_K3_OK"}],"max_tokens":100}'
```
Result: `content: 'KIMI_K3_OK'`, `model: kimi-k3`, `cost: "0"` (or `None` in some response shapes).

## Why this works
`kimi-k3` is already in the opencode-go provider's models array in `config.yaml` (line ~16):
```
models: ["deepseek-v4-flash","deepseek-v4-pro","kimi-k2.7-code","kimi-k3","glm-5.2","glm-5","qwen3.7-plus"]
```
And `OPENCODE_GO_API_KEY` is already set in `~/.hermes/profiles/gentech/.env`. Nothing new to install or configure.

## Provider status matrix (all three setups checked Aug 15, 2026)
| Setup | Kimi K3 | Use? |
|-------|---------|------|
| **OpenCode Go** | ✅ AVAILABLE + FREE (cost 0) | **Best route** for coding + web-design work |
| **Ollama Cloud** | ⚠️ `kimi-k3:cloud` but NOT in any sub tier (even Max) — PAYG extra credits | Avoid while conserving the weekly reset |
| **Nous Portal** | ✅ Listed in Hermes catalog (`moonshotai/kimi-k3`) | Native sub path; second choice |

## Known caveat
`opencode run --model opencode-go/kimi-k3` (the CLI) returned `UnknownError: Unexpected server error` on first attempt. The **direct API call is the reliable path**. The CLI model-name format for K3 is still unpinned — retest after an OpenCode CLI update or with a bare `kimi-k3` name.

## Two-birds-one-stone
This route both (a) gives access to K3's premium web-design capability (the viral "13-min website" trick) AND (b) routes coding work through a free provider instead of burning Ollama Cloud's weekly cap. Aligns with conserving usage until the next reset.

*Recorded 09-Green Room/kimi-k3-access.md in the vault as well.*
