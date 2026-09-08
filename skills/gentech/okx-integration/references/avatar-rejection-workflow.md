# OKX.AI Avatar Rejection Resolution Workflow

**Session**: July 1, 2026  
**Agent**: #2849 "Gentech DeFi"  
**Issue**: Avatar doesn't match description  
**Rejection Message**: "当前 Agent 使用的头像与 Agent 描述不符，请调整后重新上传"  
**Translation**: "The avatar used by the current Agent does not match the Agent description, please adjust and resubmit"

---

## Problem

OKX.AI manual review rejects agents when the avatar doesn't visually match the agent description. Generic finance graphics or abstract DeFi imagery will be rejected if the agent's service is specific (e.g., "LP Strategy Analysis & Automated Rebalancing").

---

## Resolution Workflow

### Step 1: Identify the Core Service Capability
Extract the primary action from the agent description:
- "LP Strategy Analysis & Automated Rebalancing" → **Visual focus**: Balance, token movement, automation

### Step 2: Create Avatar with Explicit Visuals
Use Python PIL to generate avatar that shows the capability:
- **LP Strategy**: Two curves or token stacks
- **Rebalancing**: Arrows showing token transfer, balance scale
- **Automation**: Gear icon, loop arrows, or mechanical elements

```python
from PIL import Image, ImageDraw, ImageFont

width, height = 500, 500
img = Image.new('RGB', (width, height), '#0a1628')
draw = ImageDraw.Draw(img)

# Draw balance scale with LP tokens
# Draw green arrow showing rebalancing action
# Draw gear icon for automation

img.save('/path/to/avatar.png', 'PNG', optimize=True)
```

### Step 3: Upload to OKX.AI
```bash
onchainos agent upload --file /path/to/avatar.png
# Returns: {"ok": true, "data": {"url": "https://static.okx.com/cdn/.../<uuid>.png"}}
```

### Step 4: Update Agent with New Avatar URL
```bash
onchainos agent update --agent-id 2849 \
  --picture "https://static.okx.com/cdn/web3/wallet/marketplace/headimages/agent/avatar/<uuid>.png"
```

### Step 5: Verify Update
```bash
onchainos agent get-agents --agent-ids 2849 | python3 -m json.tool | grep "profilePicture"
```

### Step 6: Log to Audit Trail
Document all attempts with file paths, URLs, txHash, timestamps:

```markdown
**Attempt 1: Generic DeFi Avatar**
- File: /path/to/defi-agent-avatar.png
- URL: https://static.okx.com/.../2f54f54e-ae0a-4c56-81bc-53c5b472da91.png
- Tx Hash: 0x983f1e2faddeeb5ccfc3e24604a7ca489ed8b7973ea3874772db2ed64ec871e7
- Status: ❌ Rejected (not specific enough)

**Attempt 2: LP Strategy Avatar**
- File: /path/to/lp-strategy-avatar.png
- URL: https://static.okx.com/.../093e1ed1-2758-419d-8315-8f92cb0293d0.png
- Tx Hash: 0x573cf8996e34904c2776f05b5a35685553ffed2dd29a4f88129e10457e01e93d
- Status: ❌ Rejected (missing "automated rebalancing" action)

**Attempt 3: LP Rebalancing Avatar (CURRENT)**
- File: /path/to/lp-rebalancing-avatar.png
- Features: Balance scale + rebalancing arrows + automation gear
- URL: https://static.okx.com/.../5fd633b9-f095-49a8-8de9-75663fb3b9a2.png
- Tx Hash: 0xa60cd07132c502c7eff063d1d5229b61a6c181c5a6fe94d9ca0f570fb371d884
- Status: ⏳ Pending manual review
```

---

## Avatar Design Principles

| Agent Service | Visual Elements to Include | Avoid |
|---------------|---------------------------|-------|
| LP Rebalancing | Balance scale, token stacks, directional arrows, gears | Generic dollar signs, abstract charts |
| Yield Scanning | Rate tables, yield comparison bars, protocol logos | Single currency symbol, wallet icon |
| Arbitrage | Two chains connected, profit arrows, speed indicators | Abstract network graph, trading chart |
| Portfolio Management | Pie chart with allocation, progress bars, rebalance icon | Single coin logo, wallet UI mockup |

---

## Expected Timeline

- Avatar upload: Immediate (CLI returns URL)
- On-chain update: ~1-2 minutes (tx confirmation)
- Manual review: 24-48 hours (OKX.AI team)

---

## Verification Checklist

- [ ] Avatar explicitly shows the core service capability
- [ ] Visual elements match key terms in description (e.g., "automated" → gears)
- [ ] File size under 50KB (recommended for fast loading)
- [ ] PNG/JPEG/WebP format only
- [ ] Resolution 500x500 or square aspect ratio
- [ ] txHash recorded in audit trail
- [ ] Avatar URL verified via `get-agents` command

---

## Related Issues

- **Name Length Rejection**: Keep English names under 25 characters
- **Similarity Rejection**: Differentiate from existing agents (e.g., Otto AI)
- **Missing Service Fields**: Include complete service JSON with all required fields