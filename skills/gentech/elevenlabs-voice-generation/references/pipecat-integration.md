# Pipecat + ElevenLabs Integration

Researched 2026-07-03. Pipecat is an open-source Python framework (13.2k⭐) for building real-time voice and multimodal conversational agents.

## Architecture

```
Speech Engine SDK (outer layer — voice loop, STT/TTS, turn-taking)
  └─ on_transcript callback fires when user finishes speaking
       └─ Pipecat pipeline (runs for one turn, then cancelled)
            └─ Composable processors: LLM call, RAG, function calls, guardrails
                 └─ Stream text back → ElevenLabs TTS → user
```

Pipecat handles **text generation** through a composable pipeline. ElevenLabs Speech Engine handles the **voice loop** (STT, TTS, turn-taking, interruption).

## When to Use

- Brain needs more than a single LLM call (RAG, function calls, guardrails)
- Frame-based middleware for inspecting/transforming/blocking traffic
- Reusable pipeline fragments across multiple agents
- **Not needed** if brain is just "transcript in, LLM call out" — use Speech Engine quickstart instead

## Setup

```bash
pip install "pipecat-ai[openai]" "elevenlabs" "python-dotenv"
```

Replace `[openai]` with `[anthropic]`, `[google]`, etc. for other LLM providers.

## Key Files

- `brain.py` — TextSink processor (drains streamed text into async queue) + run_pipecat_brain coroutine
- Shared secret in Speech Engine config for auth

## Links

- **Pipecat GitHub**: https://github.com/pipecat-ai/pipecat
- **Integration Guide**: https://elevenlabs.io/docs/eleven-api/guides/how-to/speech-engine/pipecat-integration
- **Speech Engine Quickstart**: https://elevenlabs.io/docs/eleven-api/guides/cookbooks/speech-engine

## Dependencies

- Python 3.10+
- Public HTTPS tunnel for brain server (e.g. ngrok)
- ElevenLabs Speech Engine (pre-configured)
