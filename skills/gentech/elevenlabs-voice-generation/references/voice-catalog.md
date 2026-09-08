# Gentech Voice Catalog

All known voice IDs, settings, and source notes for ElevenLabs TTS.

## Character Voices

### Optimus Prime (Peter Cullen)
| Field | Value |
|-------|-------|
| **Voice ID** | `xQbwtCgzouB5QdCSd0Z7` |
| **Model** | `eleven_multilingual_v2` |
| **Stability** | 0.75 |
| **Similarity Boost** | 0.85 |
| **Speed** | 0.88 |
| **Source** | Voice clone of Peter Cullen's Optimus Prime (renamed from "YoYo" Aug 13, 2026) |
| **Use** | Roasts, feedback messages, fun supervisor comms, agent intros |

### Steve Harvey
| Field | Value |
|-------|-------|
| **Voice ID** | `Rxk9LQxvNFEplpjjsjuN` |
| **Model** | `eleven_multilingual_v2` |
| **Stability** | 0.45 |
| **Similarity Boost** | 0.75 |
| **Speed** | Default |
| **Voice Type** | Expressive/Preacher |
| **Pacing** | Steve Harvey Pattern — punch-and-pause, dramatic beats, one-thought-per-line |
| **Use** | Social media narration, comic announcements, non-technical audience <br>❌ NOT for: technical reads, fast content, informational narration |

### Uncle Iroh (Gentech-Iroh)
| Field | Value |
|-------|-------|
| **Voice ID** | `NqA7ncEPGGt1nDbCrDex` |
| **Source** | Uncle Iroh voice clone |

## Gentech Agent Voices

### Vanito
| Field | Value |
|-------|-------|
| **Voice ID** | `eMQtaKLvw87ksRqmQVpS` |
| **Use** | Gaming content |

### Christel
| Voice ID: `R8Nmfj7gteuYpqJBPrMD` |

### Christel - TrustGuard Good Cop
| Voice ID: `kb3G0tkYW7pEGVlHEdu5` |

### Jocelyn-English
| Voice ID: `dwPf6y3q42Kdh7xBSGKx` |

### IvanOnTech
| Voice ID: `ToA54GQ3jBRB2zt0fBXj` |

### D-Mob (Def Jam voice)
| Voice ID: `n2icbiwmCen7udwM65GS` |

### Alex (professional)
| Voice ID: `XaEUesE01wKIKaa0xI0h` |

### Alexei (professional)
| Voice ID: `NQJnREzQtnAHHZnia0tY` |

> **Removed:** Mako (`TkEJnN27nf5BsX1xwrLB`) deleted Aug 13, 2026 — not distinctive. YoYo renamed to Optimus Prime.

## Default Voices (Built-in ElevenLabs)

| Alias | Voice ID | Description |
|-------|----------|-------------|
| sarah | EXAVITQu4vr4xnSDxMaL | Mature, Reassuring, Confident |
| roger | CwhRBWXzGAHq8TQ4Fs17 | Laid-Back, Casual, Resonant |
| george | JBFqnCBsd6RMkjVDRZzb | Warm, Captivating Storyteller |
| laura | FGY2WhTYpPnrIDTdsKH5 | Enthusiast, Quirky Attitude |
| charlie | IKne3meq5aSn9XLyUdCD | Deep, Confident, Energetic |
| callum | N2lVS1w4EtoT3dr4eOWO | Husky Trickster |
| river | SAz9YHcvj6GT2YYXdXww | Relaxed, Neutral, Informative |
| harry | SOYHLrjzK2X1ezoPC6cr | Fierce Warrior |
| (adam) | pNInz6obpgDQGcFmaJgB | Dominant, Firm |
| (brian) | nPczCjzI2devNBz1zQrb | Deep, Resonant, Comforting |

## API Key Status Tracking

| Date | Source | Status | Action |
|------|--------|--------|--------|
| 2026-07-06 | Vault `HQ/Integrations/elevenlabs-api-key.md` | ⚠️ EXPIRED — `invalid_api_key` | Jordan must regenerate from ElevenLabs dashboard and update vault |

**PITFALL:** Keys in documentation files can go stale. Always validate with:
```bash
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user
```
If authentication fails, the key is expired — regenerate from dashboard, don't chase stale backups.

## Voice Settings Quick Reference

```
stability: 0.35-0.50    — Expressive voices, preacher cadence (Steve Harvey)
stability: 0.55-0.70    — Warm conversational, storyteller (Iroh, Vanito)
stability: 0.70-0.85    — Professional narration, authoritative (Optimus, Mako)

similarity_boost: 0.70-0.80 — Expressive clones — safer range, prevents artifacts
similarity_boost: 0.80-0.95 — Stable voices — higher = closer to original

Model rule: cloned voices → eleven_multilingual_v2. Non-clone short → turbo_v2_5.
```

**Match voice type to profile using `gentech/voice-agent-config` skill — one-size-fits-all defaults cause degradation.**
