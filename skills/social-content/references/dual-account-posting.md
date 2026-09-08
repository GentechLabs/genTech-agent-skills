# Dual-Account X/Twitter Posting Strategy

## GenTech Labs Dual-Account Setup

### Accounts
| Account | Purpose | Tone |
|---------|---------|------|
| @GentechLabs | Brand account — products, tech, AAE | Technical, concise, code-first |
| @ProtoJay4789 | Personal account — journey, gaming, takes | Storytelling, accessible, personality |

### Funnel Strategy
Jordan's followers → GenTech Labs → back to Jordan
- Personal account builds trust and relatability
- Brand account builds credibility and product awareness
- Cross-reference between accounts naturally

### Posting Schedule (From Jordan's Breaks)
| Break | Time | Account | Content Type |
|-------|------|---------|--------------|
| 1st | 8:30 AM | @GentechLabs | Morning build update |
| 2nd | 10:30 AM | @ProtoJay4789 | Personal take / gaming |
| 3rd | 12:30 PM | @GentechLabs | Tech insight / product |
| 4th | 3:15 PM | @ProtoJay4789 | Afternoon engagement |

### Content Pillars

**@GentechLabs (Brand):**
1. Product updates (Deal Tracker, Patch Notes, APIs)
2. Technical insights (x402, ERC-8004, agent economy)
3. AAE foundation (what we're building, why it matters)
4. Data / social proof (deals found, games tracked)
5. Building in public (daily progress)

**@ProtoJay4789 (Personal):**
1. Building in public journey (solo founder + AI agent)
2. Gaming content (POE2, Steam deals, reactions)
3. Hot takes on AI, crypto, agent economy
4. Personal milestones and lessons learned
5. Community engagement (reply to builders)

### Posting Mechanics (For Jordan)
- **Single post:** Type and hit "Post"
- **Thread:** Write first → click "+" to add more → "Post all"
- **Pin:** Three dots on post → "Pin to profile"
- **Quote tweet:** Retweet button → "Quote" → add take
- **Reply:** Reply icon under someone's post

### X API Costs
| Tier | Cost | Write Limit | Recommendation |
|------|------|-------------|----------------|
| Free | $0 | 50 tweets/mo | Start here |
| Basic | $200/mo | 3K tweets/mo | Upgrade when revenue |
| Pro | $5,000/mo | 300K tweets/mo | Scale later |

### X Premium (Verification)
- Per-account subscription
- Premium: $8/mo (checkmark, 50% less ads)
- Premium+: $22/mo (checkmark, Grok access)
- **Recommendation:** Verify @GentechLabs first ($8/mo)

### xurl Setup (Agent Posting)
```bash
# Register apps
xurl auth apps add gentech-agent --client-id <ID> --client-secret <SECRET>
xurl auth apps add jordan-personal --client-id <ID> --client-secret <SECRET>

# Authenticate
xurl auth oauth2 --app gentech-agent GentechLabs
xurl auth oauth2 --app jordan-personal ProtoJay4789

# Set default
xurl auth default gentech-agent

# Post from either account
xurl post "Hello from GenTech Labs!"                          # default = GentechLabs
xurl --app jordan-personal post "Hello from Jordan!"          # explicit
```

### Content Drafting Workflow
1. Jordan discusses work in Telegram groups
2. Agent drafts posts from real conversations (not manufactured)
3. Posts route to Entertainment group for review
4. Jordan approves or edits
5. Agent posts via xurl (once authenticated)

### Week 1 Content (AAE Foundation)
**Day 1: Introduction**
- Post 1: "This is GenTech Labs 🎮🤖 We're building the Autonomous Agent Economy (AAE)..."
- Post 2: "Meet Gentech. Not a chatbot. Not a wrapper. An autonomous agent that..."
- Post 3: "The AAE runs on: ERC-8004, x402, Hermes Agent, 13 live APIs..."

**Day 2: Products**
- Post 1: "What we've shipped: Deal Tracker, Patch Notes, Rugcheck, Revenue Monitor..."
- Post 2: "Your Steam wishlist has 64 games. You check maybe 5. We check all 64..."
- Post 3: "Early Access games can't show release dates on Steam. We detect them anyway..."

**Day 3: Vision**
- Post 1: "The AAE isn't about replacing humans. It's about building infrastructure..."
- Post 2: "Jordan orchestrates. Gentech builds. Together we ship products..."
- Post 3: "This is what agent-to-agent economy looks like..."

### Pitfalls
- **Don't post manufactured content** — post from real work and conversations
- **Don't mention dollar amounts** — family sees financial numbers and asks to borrow
- **Keep brand and personal voices distinct** — technical vs. storytelling
- **Don't schedule everything** — leave room for real-time engagement
- **First 30 minutes matter** — engage with replies immediately after posting
