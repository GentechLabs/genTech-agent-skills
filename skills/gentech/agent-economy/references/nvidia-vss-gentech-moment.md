# NVIDIA VSS 3 + GenTech Moment — Video Intelligence Integration

## NVIDIA Metropolis VSS 3

**Repo:** github.com/NVIDIA-AI-Blueprints/video-search-and-summarization
**License:** Apache-2.0
**Version:** 3.2.0

### 16 Agent Skills (agentskills.io spec)

**Core video:**
- `vss-ask-video` — Visual Q&A on clips via VLM
- `vss-search-archive` — Natural-language search across video archives
- `vss-summarize-video` — Summarize long recordings
- `vss-generate-video-report` — Formatted analysis reports

**Deployment:**
- `vss-deploy-profile` — Stand up full workflows (base/search/lvs/alerts)
- `vss-deploy-detection-tracking-2d/3d` — Object detection
- `vss-deploy-dense-captioning` — VLM captions on streams
- `vss-deploy-video-embedding` — Semantic video embeddings

**Management:**
- `vss-manage-alerts` — Add/manage/monitor alerts
- `vss-query-analytics` — Read incidents, metrics, sensor data
- `vss-manage-video-io-storage` — Cameras, clips, storage

### Architecture

```
Video In → Real-Time Intelligence → Downstream Analytics → Agent Processing
            (detection, embedding,      (behavior, alerts)    (search, summarize,
             VLM captions)                                    Q&A, reports)
```

### Integration with GenTech

**For Jordan sending videos:**
- `vss-ask-video` — "What's in this video?" → VLM answers
- `vss-summarize-video` — summarize long recordings

**For API skill (x402):**
- Wrap VSS REST API as paid endpoint
- Video Q&A, summarization, search — pay per call

**For Unreal Engine:**
- 3D detection/tracking for game footage
- Anomaly detection on streams

**Requirement:** GPU-accelerated NIM microservices (cloud GPU ~$0.50-2/hr)

## GenTech Moment — Journal Feature

**Concept:** Send video → agent watches → reacts contextually → saves to journal
**Tagline:** "Your journal remembers everything. Now it watches too."
**Design doc:** `09-Green Room/ideas/gentech-moment.md`

### Tech Stack
- NVIDIA VSS 3 (video understanding)
- Hermes Memory (context)
- TTS (voice reactions)
- Journal (timeline + logging)

### Build Queue Items
1. Prototype Video Q&A
2. Memory integration
3. Voice reactions (TTS)
4. Journal logging
5. MVP Telegram bot
6. Premium tier
