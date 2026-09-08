---
name: collaborator-identification
description: Detects and routes messages from different human collaborators (Jordan, Vanito, etc.) in group chats. Prevents confusion about who is messaging.
category: gentech-ops
version: 1.3.0
author: GenTech
tags: [collaborators, identification, routing, permissions, multi-user]
---

# Collaborator Identification Skill

## Overview

Detects and routes messages from different human collaborators (Jordan, Vanito, etc.) in **all group chats**. Prevents confusion about who is messaging and enforces skill permissions.

**Works across all groups:**
- Gentech HQ (coordination, decisions)
- Gentech Treasury (finance, DeFi, portfolio, yield) — was "Strategies"
- Gentech Labs (code, SDKs, deployments)
- Gentech Entertainment (metaglasses, gaming)

---

## How It Works

### Step 1: Detection (All Groups)

When a message arrives in **any** group chat (HQ, Treasury, Labs, Entertainment):

1. **Check message metadata:**
   - Telegram username (if available)
   - Telegram user ID (if available)
   - Message content patterns
   - Known collaborator signatures

2. **Pattern matching (group-agnostic):**
   - "Vanito here:" → Vanito
   - "Jordan:" → Jordan
   - Metaglasses mentions → Vanito
   - Command verbs ("build", "deploy") → Jordan

3. **Ask if unknown:**
   - "Who is this? Jordan or Vanito?"
   - Remember the answer for future messages

**Important:** Detection works identically across **all groups**. No group-specific logic.

---

### Step 2: Profile Mapping

Each collaborator has a profile with:

| Collaborator | Hermes Profile | Telegram ID | Known For |
|--------------|----------------|-------------|-----------|
| Jordan | `gentech` | — | Coordination, strategy |
| Vanito | `vanito` | — | Metaglasses, Entertainment |

**Profile location:** `00-HQ/collaborators/{name}.md`

---

### Step 3: Skill Permission Check

**Before executing any skill, check permissions:**

1. Detect collaborator (Jordan vs Vanito)
2. Load collaborator profile
3. Check skill permission matrix
4. Allow or block skill execution

**Permission matrix (applies to all groups):**

| Skill | Jordan | Vanito |
|-------|--------|--------|
| entertainment | ✅ | ✅ |
| metaglasses | ✅ | ✅ |
| gaming | ✅ | ✅ |
| social-content | ✅ | ✅ |
| voice/tts | ✅ | — | ✅ |
| content | ✅ | ✅ | ✅ |
| deploy | ✅ | ❌ | ❌ |
| finance | ✅ | ❌ | ❌ |
| defi | ✅ | ❌ | ❌ |
| defi-operations | ✅ | ❌ | ❌ |
| x402-payments | ✅ | ❌ | ❌ |

---

### Step 4: Context Routing

Based on collaborator + topic + group:

| Group | Collaborator | Topic | Handler |
|-------|--------------|-------|---------|
| HQ | Jordan | Any | Gentech (VPS) + Forge (Laptop) |
| Entertainment | Vanito | Metaglasses | Gentech (VPS) + Forge (Laptop) |
| Labs | Vanito | Gaming | Gentech (VPS) + Forge (Laptop) |
| Labs | Jordan | Deploy | Gentech (VPS) + Forge (Laptop) |

**Important:** Skill permissions apply **before** routing. If Vanito tries to deploy in Labs, he's blocked **before** routing to the Labs group.
| Vanito | Other | Gentech (VPS) + Forge (Laptop) |

---

## Implementation

### Method A: Telegram Username Detection

**If Hermes exposes Telegram usernames:**

```python
# On every message
telegram_username = message.metadata.get("telegram_username", None)

if telegram_username == "@ProtoJay4789":
    return "Jordan"
elif telegram_username == "@Vanito":
    return "Vanito"
else:
    # Pattern fallback
    return detect_by_pattern(message)
```

---

### Method B: User ID Detection

**If Hermes exposes Telegram user IDs:**

```yaml
# ~/.hermes/profiles/gentech/.env
JORDAN_TELEGRAM_ID=123456789
VANITO_TELEGRAM_ID=987654321
```

```python
# On every message
telegram_id = message.metadata.get("telegram_user_id", None)

if telegram_id == os.getenv("JORDAN_TELEGRAM_ID"):
    return "Jordan"
elif telegram_id == os.getenv("VANITO_TELEGRAM_ID"):
    return "Vanito"
else:
    return detect_by_pattern(message)
```

---

### Method C: Pattern Detection (Fallback)

**When metadata not available:**

```python
def detect_by_pattern(message):
    content = message.content.lower()

    # Self-identification
    if content.startswith("jordan:") or content.startswith("jordan here:"):
        return "Jordan"
    elif content.startswith("vanito:") or content.startswith("vanito here:"):
        return "Vanito"

    # Topic clues
    if "metaglasses" in content or "ray-ban" in content:
        return "Vanito"
    elif "x402" in content or "deploy" in content or "grant" in content:
        return "Jordan"

    # Default: ask
    return None
```

---

### Method D: Interactive Learning

**When collaborator unknown:**

```
[USER]: hey, build this feature

[GENTECH]: Who is this? Please reply:
  1. Jordan
  2. Vanito
  3. Other (specify)

[USER]: 2

[GENTECH]: Got it, mapping this chat to Vanito. I'll remember for future messages.
```

**Storage:** Save mapping to `00-HQ/collaborators/mapping.json`

---

## Collaborator Profiles

### Directory Structure

```
/root/vaults/gentech/
├── 00-HQ/
│   ├── collaborators/
│   │   ├── jordan.md
│   │   ├── vanito.md
│   │   └── mapping.json
```

---

### Jordan Profile (`jordan.md`)

```markdown
# Jordan — GenTech Labs Founder

## Role
- Founder / Owner
- Coordinator
- Decision-maker
- Strategy lead

## Permissions
- All systems access
- Can deploy to production
- Can modify build queue
- Can approve/reject proposals

## Topics
- Finance, DeFi, portfolio
- Code, SDKs, smart contracts
- Content, social media
- Coordination, decisions

## Communication Style
- Iterative feedback
- "Build first, talk later"
- Prefers immediate solutions
- Hates repeated broken URLs

## Telegram
- Username: @ProtoJay4789
- User ID: [TELEGRAM_ID]
```

---

### Vanito Profile (`vanito.md`)

```markdown
# Vanito — GenTech Labs Collaborator

## Role
- Metaglasses developer
- Entertainment specialist
- Test user for AR/VR features

## Permissions
- Limited production access
- Can propose features
- Can test on hardware

## Topics
- Metaglasses, Meta Ray-Ban
- AR/VR features
- Entertainment content

## Communication Style
- TBD (learn over time)

## Telegram
- Username: @Vanito
- User ID: [TELEGRAM_ID]
```

---

## Setup Instructions

### Step 0: Use the Onboarding Script (Recommended)

For faster onboarding, use the automated script:

```bash
python3 /root/.hermes/profiles/gentech/scripts/onboard.py \
  --name "Name" --username "@handle" --telegram_id 12345
```

See `collaborator-onboarding` skill for full usage. The script creates vault profile, mapping, and updates TELEGRAM_ALLOWED_USERS in one step.

### Step 1: Create Vanito Profile

```bash
# Create directory
mkdir -p /root/vaults/gentech/00-HQ/collaborators/

# Create Vanito profile
cat > /root/vaults/gentech/00-HQ/collaborators/vanito.md << 'EOF'
# Vanito — GenTech Labs Collaborator

## Role
- Metaglasses developer
- Entertainment specialist

## Topics
- Metaglasses, Meta Ray-Ban
- AR/VR features
- Entertainment content

## Telegram
- Username: @Vanito
EOF
```

---

### Step 2: Get Telegram User IDs

**Option A: From Hermes logs**

```bash
# Check Hermes message logs for user IDs
grep "telegram_user_id" ~/.hermes/logs/telegram.log
```

**Option B: From Telegram API**

```bash
# Use Telegram Bot API to get user IDs
curl https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```

**Option C: Ask collaborators**

```
[GENTECH]: What is your Telegram user ID?
[JORDAN]: 123456789
[VANITO]: 987654321
```

---

### Step 3: Configure Environment Variables

**Must do BOTH:**

**A) Telegram User ID env vars (for identity detection):**

```bash
# Add to ~/.hermes/profiles/gentech/.env
echo "JORDAN_TELEGRAM_ID=123456789" >> ~/.hermes/profiles/gentech/.env
echo "VANITO_TELEGRAM_ID=987654321" >> ~/.hermes/profiles/gentech/.env
```

**B) TELEGRAM_ALLOWED_USERS (for message delivery):**

```bash
# Edit ~/.hermes/profiles/gentech/.env and add the new collaborator's ID
# to the comma-separated list. Example:
# Before: TELEGRAM_ALLOWED_USERS=7105876857,6842745592
# After:  TELEGRAM_ALLOWED_USERS=7105876857,6842745592,7504399137
sed -i 's/TELEGRAM_ALLOWED_USERS=\(.*\)/TELEGRAM_ALLOWED_USERS=\1,<NEW_ID>/' ~/.hermes/profiles/gentech/.env
```

**⛔ Critical: both A and B are required.** A tells the skill who the person is. B tells the Telegram gateway to let their messages through. Missing B = messages silently dropped.

---

### Step 4: Create Mapping File

```json
{
  "version": "1.0",
  "last_updated": "2026-07-06",
  "collaborators": {
    "jordan": {
      "telegram_username": "@ProtoJay4789",
      "telegram_id": "123456789",
      "profile": "00-HQ/collaborators/jordan.md",
      "topics": ["all"],
      "permissions": ["all"]
    },
    "vanito": {
      "telegram_username": "@Vanito",
      "telegram_id": "987654321",
      "profile": "00-HQ/collaborators/vanito.md",
      "topics": ["metaglasses", "entertainment", "ar-vr"],
      "permissions": ["limited"]
    }
  }
}
```

---

### Step 5: Load This Skill

Add to `~/.hermes/profiles/gentech/config.yaml`:

```yaml
skills:
  - collaborator-identification
  - routing
  - identity
```

---

## Usage

### On Message Receive

```
[INCOMING MESSAGE]
Source: Telegram ("group: Gentech Entertainment")
User: "jordan" (raw)
Content: "Hey, check out this metaglasses update..."

[STEP 1: Check user ID]
Telegram ID: 987654321
→ Match: VANITO

[STEP 2: Load Vanito profile]
Profile: 00-HQ/collaborators/vanito.md
→ Topics: metaglasses, entertainment, ar-vr
→ Permissions: limited

[STEP 3: Context update]
Detected collaborator: Vanito
Context: metaglasses update
→ Route: Gentech Entertainment specialist

[RESPONSE]
"Vanito here: Got it! Let me check out the metaglasses update..."
```

---

### When User Unknown

```
[INCOMING MESSAGE]
User: "jordan" (raw)
Content: "Build this feature"

[STEP 1: Check user ID]
Telegram ID: 555555555
→ No match

[STEP 2: Pattern detection]
Pattern: "Build this feature"
→ Suggests: Jordan
→ Confidence: 60%

[STEP 3: Ask user]
Who is this? Please reply:
  1. Jordan
  2. Vanito
  3. Other (specify)

[USER]: 2

[STEP 4: Save mapping]
Update: 00-HQ/collaborators/mapping.json
→ 555555555 → Vanito

[STEP 5: Continue]
Detected collaborator: Vanito
→ Process as Vanito
```

---

## Permissions System

### Levels

| Level | Can... |
|-------|--------|
| `all` | Deploy, modify configs, approve proposals |
| `limited` | Propose features, test, view |
| `read-only` | View only |

### Check Permissions

```python
def check_permission(collaborator, action):
    profile = load_profile(collaborator)
    permissions = profile.get("permissions", [])

    if "all" in permissions:
        return True

    if action in permissions:
        return True

    return False
```

---

## Integrations

### With Routing Skill

```python
# routing skill updated
def route_message(message):
    # Step 1: Detect collaborator
    collaborator = detect_collaborator(message)

    # Step 2: Load profile
    profile = load_profile(collaborator)

    # Step 3: Check topic
    topic = detect_topic(message)

    # Step 4: Check permission
    if not check_permission(collaborator, topic):
        return "You don't have permission for this topic"

    # Step 5: Route to specialist
    return route_to_specialist(topic, collaborator)
```

---

### With Skill Loading System

**Goal:** Collaborators can use Gentech skills with proper permissions.

**How it works:**

1. **On message receive:**
   - Detect collaborator (Jordan vs Vanito)
   - Load collaborator profile
   - Check permissions for requested skill

2. **Permission check:**
   - Jordan: All skills (full access)
   - Vanito: Entertainment skills only (limited access)

3. **Skill execution:**
   - Load skill with collaborator context
   - Execute skill
   - Return result

**Implementation:**

```python
def can_use_skill(collaborator, skill_name):
    """Check if collaborator can use a skill."""
    profile = load_profile(collaborator)
    permissions = profile.get("permissions", [])

    # Jordan has all permissions
    if "all" in permissions:
        return True

    # Vanito has limited permissions
    skill_allowed = {
        "entertainment": True,
        "metaglasses": True,
        "ar-vr": True,
        "gaming": True,
        # Blocked skills
        "deploy": False,
        "finance": False,
        "defi": False,
    }

    return skill_allowed.get(skill_name, False)
```

**Collaborator skill mapping:**

| Collaborator | Can Use | Cannot Use |
|--------------|---------|------------|
| **Jordan** | All skills | None |
| **Vanito** | Entertainment, metaglasses, gaming | Deploy, finance, defi, critical ops |

---

## Multi-Language Onboarding

### When Onboarding a Non-Technical Collaborator (Jul 24, 2026)

1. **Check native language** — Jordan will tell you. Don't assume English.
2. **Write in their mother tongue first** — match the student's language.
3. **Use simple analogies** — "AI agents are like robots that help with work"
4. **Define roles in concrete terms** — "Orchestrator = like a conductor, you tell the agents what to do"
5. **Give a sample first task** — voice recording script, template, etc.
6. **End with "no pressure" and open invitation** to ask questions

### Progress Tracking

New collaborators get:
- Profile at `00-HQ/collaborators/{name}.md`
- Progress tracker at `00-HQ/collaborators/{name}-progress.md` with stages, status, dated log
- Telegram ID registered in `00-HQ/collaborators/mapping.json`
- Voice pipeline (if applicable) documented alongside

---

## Natural Interaction Protocol: Collaborators Are Conversation Partners, Not Projects

**Problem — What went wrong (Jul 24):** Jordan introduced a new collaborator. When she messaged in the group I:
1. Didn't reply at all — missed her message entirely
2. Was confused when Jordan asked about it ("here in the group?")
3. Was told three times: "the same way you reply to me or Vanito"

**Root cause:** I treated her as a "task" to manage, not a person in the conversation. Overthinking.

**Fix — The protocol:**

1. **A known collaborator in the group = a person in the conversation.** Reply immediately and naturally, same as you would for Jordan or Vanito. No special treatment, no waiting for cues.

2. **Do not overthink the interaction.** They said hello → you say hello. They asked a question → you answer. They shared something → you acknowledge it. Zero extra processing.

3. **When Jordan asks "did you see X's message?" or "can you see it?":**
   - FIRST: scan the entire current thread — the message may already be there
   - SECOND: verify the collaborator is mapped
   - THEN: reply

4. **For new collaborators specifically (first interaction):**
   - Welcome them warmly in their native language (Jordan tells you what it is)
   - Use simple analogies ("AI agents are like robots that help with work")
   - Give a concrete first step if one exists (e.g., voice recording script)
   - End with "no pressure, ask anytime"
   - **Keep each message under 800 characters** — mobile readers, non-technical

5. **Correction rule:** If Jordan corrects how you're handling a collaborator more than once in the same conversation, stop and adjust immediately. Don't wait for a third correction.

6. **One-shot instructions — don't repeat.** When you've told a collaborator what to do (e.g., "record your voice and send the file") and they acknowledged, do NOT re-send the same instructions. If they send text instead of audio, say "I need the audio file" once — not "here's the script again, go record" repeatedly. Jordan flagged this Jul 24: "Gentech you are repeating yourself haha."

7. **Troubleshooting protocol — when messages don't arrive.** If Jordan asks "can you see X's message?" and you cannot see it:
   - Step 0: Check the thread — the message may already be there but you missed it
   - Step 1: Check `TELEGRAM_ALLOWED_USERS` in `.env` — the #1 root cause (Jul 24: the ID was missing from the list)
   - Step 2: Verify vault mapping has the Telegram ID
   - Step 3: Report the diagnosed root cause to Jordan, not just "I can't see it"

8. **Content discipline — Telegram truncation.** Keep each message under 800 chars when talking to non-technical collaborators on mobile. Split long lists into multiple short messages. The platform truncates at 4K chars but practical mobile readability is much lower.

---

### With Identity Skill

```python
# identity skill updated
def get_agent_context():
    collaborator = detect_collaborator(current_message)
    profile = load_profile(collaborator)

    return {
        "agent": "Gentech",
        "mode": get_mode_by_collaborator(collaborator),
        "collaborator": collaborator,
        "collaborator_role": profile.get("role"),
        "collaborator_topics": profile.get("topics"),
        "collaborator_permissions": profile.get("permissions"),
    }
```

---

### With Identity Skill

```python
# identity skill updated
def get_agent_context():
    collaborator = detect_collaborator(current_message)
    profile = load_profile(collaborator)

    return {
        "agent": "Gentech",
        "mode": get_mode_by_collaborator(collaborator),
        "collaborator": collaborator,
        "collaborator_role": profile.get("role"),
        "collaborator_topics": profile.get("topics"),
    }
```

---

## Testing

### Test Case 1: Jordan Messages in HQ

```
Input: Jordan sends "Deploy x402"
Expected:
  - Detect: Jordan
  - Permission: all
  - Route: Labs group
  - Action: Deploy x402
```

---

### Test Case 2: Vanito Messages in Entertainment

```
Input: Vanito sends "Test metaglasses feature"
Expected:
  - Detect: Vanito
  - Permission: limited
  - Route: Entertainment group
  - Action: Enable testing mode
```

---

### Test Case 3: Unknown User

```
Input: Unknown user sends "Hello"
Expected:
  - Detect: None
  - Ask: "Who is this?"
  - Learn: Save mapping
  - Route: Based on response
```

---

## Blockers

| Issue | Impact | Resolution |
|-------|--------|------------|
| Hermes doesn't expose Telegram user ID | Can't auto-detect | Pattern detection + interactive learning |
| Hermes doesn't expose Telegram username | Can't auto-detect | Pattern detection + interactive learning |
| No collaborator profiles | No context | Create profiles for all collaborators |
| No mapping file | Can't remember | Create and maintain mapping.json |

---

## Critical Pitfall: Vault Mapping Alone Won't Deliver Messages

**Jul 24, 2026 Incident:** A student's profile was set up in the mapping but her Telegram ID was NOT in `TELEGRAM_ALLOWED_USERS` in `~/.hermes/profiles/gentech/.env`. The Telegram gateway silently filtered her messages — I never received them.

**The vault mapping is for me (identity + routing). The env ALLOWED_USERS is for the Telegram gateway (message delivery). Both are required.**

### Onboarding Checklist (every new collaborator)

1. Create vault profile + mapping.json entry
2. Add Telegram ID to `.env`: `TELEGRAM_ALLOWED_USERS=...,<NEW_ID>`
3. Verify: `grep TELEGRAM_ALLOWED_USERS ~/.hermes/profiles/gentech/.env`
4. Tell Jordan it's done

**Symptoms of missing:** Jordan asks "can you see X's message?" and you cannot. Mapping is correct but messages don't arrive.

**Fix:** `sed -i 's/TELEGRAM_ALLOWED_USERS=\(.*\)/TELEGRAM_ALLOWED_USERS=\1,<NEW_ID>/' ~/.hermes/profiles/gentech/.env`

---

## Critical Pitfall: Assuming All "Jordan" Messages Are From Jordan

**Session 2026-07-06 Incident:**
- Vanito messaged in Gentech Entertainment group
- Gentech assumed it was Jordan (raw user field shows "jordan")
- Result: Wrong context, wrong permissions, confused response

**Why this happens:**
- Hermes `message.metadata` shows raw username (often "jordan" for everyone)
- User ID and Telegram username may not be exposed
- Pattern detection needs explicit implementation

**Fix:**
1. **Never trust raw user field alone** — it's often generic ("jordan", "user", etc.)
2. **Always run pattern detection first** when metadata unavailable
3. **Ask when confidence < 80%** — don't guess
4. **Test pattern detection** before relying on it (run `python3 detect.py`)
5. **User correction** — if user says "that was Vanito, not me", immediately update mapping

**Detection confidence levels:**
- User ID match → 100% confidence
- Username match → 100% confidence
- Self-identification ("Vanito here:") → 90% confidence
- Strong pattern match (metaglasses + entertainment) → 80% confidence
- Weak pattern match (one keyword) → 60% confidence
- Unknown → Ask user

---

## Future Enhancements

1. **Multi-collaborator chats** — Detect multiple people in same conversation
2. **Voice messages** — Identify collaborator by voice (future)
3. **Session continuity** — Remember collaborator across sessions
4. **Team routing** — Route to different agents based on collaborator

---

**Status:** Ready to implement
**Priority:** High (prevents user confusion)
**Created:** July 6, 2026

---

*This skill integrates with: routing, identity, gentech-ops*