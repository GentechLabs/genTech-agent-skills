# Voice Roster — Full Details

## Custom Cloned Voices

### Optimus Prime (Peter Cullen)
- **Voice ID:** `xQbwtCgzouB5QdCSd0Z7`
- **Source:** Cloned from YoYo voice config (Peter Cullen / Optimus Prime inspired)
- **Style:** Gravelly, resonant, noble authority
- **Best for:** Bad cop persona, dramatic narration, rap verses, authoritative announcements
- **Settings:** stability 0.75, similarity 0.90, speed 0.85
- **Rap settings:** stability 0.60, similarity 0.85, speed 0.92

### Uncle Iroh (Mako)
- **Voice ID:** `TkEJnN27nf5BsX1xwrLB`
- **Source:** Cloned from Mako (Avatar: The Last Airbender)
- **Style:** Warm, wise, philosophical
- **Best for:** Good cop persona, comedy, wisdom drops, tea metaphors
- **Settings:** stability 0.70, similarity 0.85, speed 0.88
- **Rap settings:** stability 0.55, similarity 0.80, speed 0.90

### Steve Harvey
- **Voice ID:** `Rxk9LQxvNFEplpjjsjuN`
- **Source:** Cloned from Steve Harvey
- **Style:** Punchy, confident, motivational
- **Best for:** Social storytelling, daily content, motivational speech
- **Settings:** stability 0.70, similarity 0.85, speed 0.90

### Vanito
- **Voice ID:** `eMQtaKLvw87ksRqmQVpS`
- **Source:** Cloned from Vanito (collaborator)
- **Style:** Energetic, competitive, playful
- **Best for:** Roasts, reactions, self-deprecation, gaming content
- **Settings:** stability 0.60, similarity 0.90, speed 0.95

### Christel
- **Voice ID:** `kb3G0tkYW7pEGVlHEdu5`
- **Source:** Cloned from Christel (collaborator)
- **Style:** Warm, supportive, encouraging
- **Best for:** Good cop persona, positive reinforcement, therapy sessions
- **Settings:** stability 0.65, similarity 0.85, speed 0.90

## Pre-Made Voices (Backup)

| Voice | ID | Style |
|-------|-----|-------|
| Charlie (DMOB) | `IKne3meq5aSn9XLyUdCD` | Deep, confident, energetic |
| George (Gentech) | `JBFqnCBsd6RMkjVDRZzb` | Warm, captivating storyteller |
| Brian | `nPczCjzI2devNBz1zQrb` | Deep, resonant (JEJ alternative) |
| Adam | `pNInz6obpgDQGcFmaJgB` | Dominant, firm |

## API Key Location
- Env var: `ELEVENLABS_API_KEY`
- Vault: `/root/vaults/gentech/.env` and `secrets.env`
- **Loading:** `export $(grep ELEVENLABS_API_KEY /root/.hermes/profiles/gentech/.env | xargs)`
