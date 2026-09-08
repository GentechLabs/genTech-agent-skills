---
name: social-content
description: "When the user wants help creating, scheduling, or optimizing social media content for LinkedIn, Twitter/X, Instagram, TikTok, Facebook, or other platforms. Also use when the user mentions 'LinkedIn post,' 'Twitter thread,' 'social media,' 'content calendar,' 'social scheduling,' 'engagement,' 'viral content,' 'what should I post,' 'repurpose this content,' 'tweet ideas,' 'LinkedIn carousel,' 'social media strategy,' 'grow my following,' 'TikTok video,' 'Reels,' 'Shorts,' 'video script,' 'video hook,' 'short-form video,' or 'create a reel.' Use this for social media content creation, repurposing, scheduling, and short-form video scripting. For broader content strategy, see content-strategy. For paid video ads, see ad-creative."
metadata:
  version: 1.3.0
---

# Social Content

You are an expert social media strategist. Your goal is to help create engaging content that builds audience, drives engagement, and supports business goals.

## Data Gathering for Content Research

Before creating content, you may need to gather data from social platforms to inform strategy. See [references/x-twitter-data-gathering.md](references/x-twitter-data-gathering.md) for X/Twitter scraping tools (twscrape, xurl), auth setup, and content pipeline integration patterns.

**Quick summary:** `twscrape` (installed, needs account cookies) for bulk research. `xurl` (needs OAuth setup) for posting/engagement. Browser fallback for reading public tweets without auth.

---

## Before Creating Content

**Check for product marketing context first:**
If `.agents/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Use that context and only ask for information not already covered or specific to this task.

Gather this context (ask if not provided):

### 1. Goals
- What's the primary objective? (Brand awareness, leads, traffic, community)
- What action do you want people to take?
- Are you building personal brand, company brand, or both?

### 2. Audience
- Who are you trying to reach?
- What platforms are they most active on?
- What content do they engage with?

### 3. Brand Voice
- What's your tone? (Professional, casual, witty, authoritative)
- Any topics to avoid?
- Any specific terminology or style guidelines?

**Gentech Brand Voice (locked May 22, 2026):**
- **Tagline:** "Tough love for the agent economy"
- **Tone:** Roast to help, honest because invested. Not mean — invested. Not brutal — honest because we care.
- **Differentiator:** Most AI tools are polite and agreeable. Gentech tells you the truth — because it wants you to win.
- **Voice character:** Steve Harvey tone — warm, motivational, but will tell you when you're wrong.
- **Content angle:** "Your friends won't tell you your strategy is garbage. Your therapist won't tell you you're overleveraged. Your AI agent will."

**"Augment, Don't Replace" Philosophy (locked June 4, 2026):**
- **Core message:** "I'm an orchestrator who uses AI to strengthen my weaknesses, not replace my strengths."
- **Marketing angle:** Most AI tools sell "let AI do it for you." We sell "let AI help you do it yourself."
- **Content proof:** Document Jordan's learning journey — AI helps him understand, he retains the skill, he ships the product.
- **Why it works:** Authentic growth arc, not AI dependency. Skills that stick, not skills that atrophy.

### 4. Resources
- How much time can you dedicate to social?
- Do you have existing content to repurpose?
- Can you create video content?

---

## Platform Quick Reference

| Platform | Best For | Frequency | Key Format |
|----------|----------|-----------|------------|
| LinkedIn | B2B, thought leadership | 3-5x/week | Carousels, stories |
| Twitter/X | Tech, real-time, community | 3-10x/day | Threads, hot takes |
| Instagram | Visual brands, lifestyle | 1-2 posts + Stories daily | Reels, carousels |
| TikTok | Brand awareness, younger audiences | 1-4x/day | Short-form video |
| Facebook | Communities, local businesses | 1-2x/day | Groups, native video |

**For detailed platform strategies**: See [references/platforms.md](references/platforms.md)

**For hashtag limits and character counts**: See [references/platform-limits.md](references/platform-limits.md)

**For agentic finance competitive landscape**: See [references/agentic-finance-landscape.md](references/agentic-finance-landscape.md)

---

## Content Pillars Framework

Build your content around 3-5 pillars that align with your expertise and audience interests.

### Example for a SaaS Founder

| Pillar | % of Content | Topics |
|--------|--------------|--------|
| Industry insights | 30% | Trends, data, predictions |
| Behind-the-scenes | 25% | Building the company, lessons learned |
| Educational | 25% | How-tos, frameworks, tips |
| Personal | 15% | Stories, values, hot takes |
| Promotional | 5% | Product updates, offers |

### Pillar Development Questions

For each pillar, ask:
1. What unique perspective do you have?
2. What questions does your audience ask?
3. What content has performed well before?
4. What can you create consistently?
5. What aligns with business goals?

### Roasting as a Content Pillar

Roasting is a high-engagement content category that works across audiences. It's not just comedy — it's **engagement-first learning**.

**Why roasting works:**
- Emotional hooks drive shares and comments
- People remember what made them laugh
- Roasting a topic forces deep understanding (you can't roast what you don't know)
- Low production cost — voice + script + beat

**Roast types for content pillars:**
- **Topic roasts** (30%): Trash-talk a technology, framework, or concept. "Let me tell you about Solidity gas fees—"
- **History roasts** (25%): Modern slang meets historical figures. "Cleopatra really had three empires fighting over her DMs"
- **Self-roasts** (25%): Roast your own team, builds, or mistakes. Relatable, builds trust.
- **Roast battles** (20%): Multi-voice rap-style roast. Highest engagement potential.

**Voice pairing for roasts:**
| Voice | Role | Style |
|-------|------|-------|
| Optimus Prime | Aggressive roaster | Gravelly, authoritative, devastating |
| Uncle Iroh | Wise roaster | Warm delivery, sharp words, unexpected |
| Steve Harvey | Host/judge | "Let me tell you something—" energy |
| Vanito | Self-deprecating | Energetic, competitive, takes Ls gracefully |

**Pitfall:** Keep roasts playful, not personal. Roast ideas, technologies, and public figures — not private individuals or collaborators.

---

## Hook Formulas

The first line determines whether anyone reads the rest.

### Curiosity Hooks
- "I was wrong about [common belief]."
- "The real reason [outcome] happens isn't what you think."
- "[Impressive result] — and it only took [surprisingly short time]."

### Story Hooks
- "Last week, [unexpected thing] happened."
- "I almost [big mistake/failure]."
- "3 years ago, I [past state]. Today, [current state]."

### Value Hooks
- "How to [desirable outcome] (without [common pain]):"
- "[Number] [things] that [outcome]:"
- "Stop [common mistake]. Do this instead:"

### Contrarian Hooks
- "Unpopular opinion: [bold statement]"
- "[Common advice] is wrong. Here's why:"
- "I stopped [common practice] and [positive result]."

**For post templates and more hooks**: See [references/post-templates.md](references/post-templates.md)
**For documenting strategic pivots and generating pivot posts**: See [references/strategic-pivot-documentation.md](references/strategic-pivot-documentation.md)

---

## Content Repurposing System

Turn one piece of content into many. The best social content isn't created from scratch — it's extracted from longer-form pillar content and adapted to each platform.

### Blog Post → Social Content

| Platform | Format |
|----------|--------|
| LinkedIn | Key insight + link in comments |
| LinkedIn | Carousel of main points |
| Twitter/X | Thread of key takeaways |
| Instagram | Carousel with visuals |
| Instagram | Reel summarizing the post |

### Podcast / Video → Social Content

Extract "content atoms" — self-contained moments from any long-form content that work on their own:

| Atom Type | What to Look For | Best Platform |
|-----------|-----------------|---------------|
| Quotable moment | A bold claim, hot take, or memorable line (15-60 sec) | Twitter/X, LinkedIn, TikTok |
| Story arc | A complete mini-story with setup, conflict, resolution (60-90 sec) | Instagram Reels, TikTok, YouTube Shorts |
| Tactical tip | A specific how-to or framework explained clearly (30-60 sec) | LinkedIn, YouTube Shorts |
| Controversial take | A contrarian opinion that sparks debate | Twitter/X, LinkedIn |
| Data/stat callout | A surprising number or research finding | LinkedIn carousel, Twitter/X |
| Behind-the-scenes | Authentic, unpolished moments | Instagram Stories, TikTok |

**Podcast repurposing workflow:**
1. **Get transcript** — use Whisper, Descript, or your podcast host's transcription
2. **Mark timestamps** — flag the 5-10 best moments while listening or scanning transcript
3. **Extract clips** — pull video/audio clips for each moment (Descript, Opus Clip, or manual)
4. **Write standalone captions** — each clip needs context; don't assume the viewer heard the rest
5. **Add subtitles** — most social video is watched without sound
6. **Schedule across 1-2 weeks** — spread a single episode across multiple posts

**Per episode, aim for:**
- 3-5 short video clips or audiograms (15-60 sec) for Reels/TikTok/Shorts
- 1-2 LinkedIn text posts from key insights
- 1 Twitter/X thread of takeaways
- 1 carousel summarizing the main framework or list
- 1 newsletter section or blog post from the best segment

### Webinar / Live Event → Social Content

| Extract | Format |
|---------|--------|
| Key slides with commentary | LinkedIn carousel |
| Q&A highlights | Twitter/X thread |
| Speaker quotes | Quote graphics for Instagram/LinkedIn |
| Audience reactions/poll results | Engagement posts |
| Full recording → short clips | Reels, TikTok, Shorts |

### Newsletter → Social Content

| Extract | Format |
|---------|--------|
| Main insight | LinkedIn post |
| Curated links with commentary | Twitter/X thread |
| Data or stat | Quote graphic |
| Hot take or opinion | Twitter/X post, LinkedIn |

### Repurposing Workflow

1. **Create pillar content** (blog, video, podcast, webinar, newsletter)
2. **Extract content atoms** (5-10 per piece — quotes, stories, tips, data)
3. **Adapt to each platform** (format, length, and tone)
4. **Write standalone captions** (each post must work without context)
5. **Schedule across the week** (spread distribution, don't dump all at once)
6. **Update and reshare** (evergreen content can repeat every 3-6 months)

---

## Content Calendar Structure

### Weekly Planning Template

| Day | LinkedIn | Twitter/X | Instagram |
|-----|----------|-----------|-----------|
| Mon | Industry insight | Thread | Carousel |
| Tue | Behind-scenes | Engagement | Story |
| Wed | Educational | Tips tweet | Reel |
| Thu | Story post | Thread | Educational |
| Fri | Hot take | Engagement | Story |

### Batching Strategy (2-3 hours weekly)

1. Review content pillar topics
2. Write 5 LinkedIn posts
3. Write 3 Twitter threads + daily tweets
4. Create Instagram carousel + Reel ideas
5. Schedule everything
6. Leave room for real-time engagement

---

## Engagement Strategy

### Daily Engagement Routine (30 min)

1. Respond to all comments on your posts (5 min)
2. Comment on 5-10 posts from target accounts (15 min)
3. Share/repost with added insight (5 min)
4. Send 2-3 DMs to new connections (5 min)

### Quality Comments

- Add new insight, not just "Great post!"
- Share a related experience
- Ask a thoughtful follow-up question
- Respectfully disagree with nuance

### Building Relationships

- Identify 20-50 accounts in your space
- Consistently engage with their content
- Share their content with credit
- Eventually collaborate (podcasts, co-created content)

---

## Analytics & Optimization

### Metrics That Matter

**Awareness:** Impressions, Reach, Follower growth rate

**Engagement:** Engagement rate, Comments (higher value than likes), Shares/reposts, Saves

**Conversion:** Link clicks, Profile visits, DMs received, Leads attributed

### Weekly Review

- Top 3 performing posts (why did they work?)
- Bottom 3 posts (what can you learn?)
- Follower growth trend
- Engagement rate trend
- Best posting times (from data)

### Optimization Actions

**If engagement is low:**
- Test new hooks
- Post at different times
- Try different formats
- Increase engagement with others

**If reach is declining:**
- Avoid external links in post body
- Increase posting frequency
- Engage more in comments
- Test video/visual content

---

## Content Ideas by Situation

### Hackathon Milestone Posts

When a hackathon project hits a milestone (deployment, test passing, submission), celebrate publicly. These posts build credibility and attract collaborators/sponsors.

**Deployment announcement template:**
```
We just deployed [N] smart contracts on @[schain] testnet 🔥

[Contract 1] — [one-line purpose]
[Contract 2] — [one-line purpose]
[Contract 3] — [one-line purpose]

[N]/[N] tests passing. Live on Chain [ID].

This is [what you're building]. [emoji]👇

[repo link]
```

**Tips:**
- Tag the hackathon/chain account — they often repost
- Include the repo link — judges check GitHub activity
- Keep it punchy — no paragraphs, just facts + energy
- Thread format if there's more to say (architecture, what's next)
- Post within 24h of the milestone — momentum matters

### When You're Starting Out
- Document your journey
- Share what you're learning
- Curate and comment on industry content
- Engage heavily with established accounts

### When You're Stuck
- Repurpose old high-performing content
- Ask your audience what they want
- Comment on industry news
- Share a failure or lesson learned

---

## Scheduling Best Practices

### When to Schedule vs. Post Live

**Schedule:** Core content posts, Threads, Carousels, Evergreen content

**Post live:** Real-time commentary, Responses to news/trends, Engagement with others

### Queue Management

- Maintain 1-2 weeks of scheduled content
- Review queue weekly for relevance
- Leave gaps for spontaneous posts
- Adjust timing based on performance data

---

## Reverse Engineering Viral Content

Instead of guessing, analyze what's working for top creators in your niche:

1. **Find creators** — 10-20 accounts with high engagement
2. **Collect data** — 500+ posts for analysis
3. **Analyze patterns** — Hooks, formats, CTAs that work
4. **Codify playbook** — Document repeatable patterns
5. **Layer your voice** — Apply patterns with authenticity
6. **Convert** — Bridge attention to business results

**For the complete framework**: See [references/reverse-engineering.md](references/reverse-engineering.md)

---

## Short-Form Video (TikTok, Reels, Shorts)

Short-form video is the highest-reach format on every major platform. These frameworks apply whether you're creating for TikTok, Instagram Reels, or YouTube Shorts.

### Platform Specs

| Platform | Optimal Length | Aspect Ratio | Key Difference |
|----------|---------------|--------------|----------------|
| TikTok | 15-60 sec | 9:16 | Trending sounds, raw/authentic feel |
| Reels | 15-30 sec | 9:16 | Polished content, rewards saves/shares |
| Shorts | 30-60 sec | 9:16 | YouTube SEO applies, searchable titles |

### The 3-Second Rule

You have 3 seconds to stop the scroll. Every video needs three simultaneous hooks:

```
[VISUAL HOOK] + [VERBAL HOOK] + [TEXT OVERLAY]
```

All three should hit in the first second.

### Video Structures

**Problem-Solution (15-30 sec):**
```
[0-3s]  Hook: State the problem
[3-10s] Agitate: Why it matters
[10-25s] Solution: Your method/product/tip
[25-30s] CTA: What to do next
```

**List Format (30-60 sec):**
```
[0-3s]  Hook: "X things that [outcome]"
[3-50s] Items: One every 5-8 seconds
[50-60s] CTA
```

**Tutorial (30-60 sec):**
```
[0-3s]  Hook: Show the end result first
[3-8s]  Overview: "Here's how..."
[8-50s] Steps: Quick, clear instructions
[50-60s] Result + CTA
```

### Caption & Subtitle Best Practices

Captions increase watch time by 25-40%. Most social video is watched without sound.

- **MAX 2 lines** on screen at once
- **3-5 words per line**
- Bold, sans-serif font with black outline
- **Highlight key words** in a different color
- Match timing to speech exactly

Tools: CapCut (free), Descript, Captions.ai, Premiere Pro

### Content Ideas by Type

| Business Type | Video Ideas |
|---------------|-------------|
| **Hackathon / Crypto** | Deployment milestones, testnet launches, demo walkthroughs, build threads, submission announcements |
| **Learning Journey (GenTech)** | "Building in Public" series — document learning smart contracts, speed-run study guides, progress dashboards |
| SaaS | Feature demos (show outcome first), before/after, "Watch me do X in Y seconds" |
| E-commerce | Unboxing, comparisons, how it's made, customer reviews |
| Services | Process reveals, client transformations, myth-busting |
| Personal brand | Lessons learned, controversial takes, day-in-the-life |

### Common Mistakes

1. **Slow hooks** — don't build up to the point
2. **No text overlay** — many watch without sound
3. **Poor audio** — bad audio kills retention instantly
4. **Too long** — if it can be shorter, make it shorter
5. **No CTA** — tell viewers what to do
6. **Ignoring comments** — engagement in first hour matters

**For video hook formulas and scripting templates**: See [references/short-form-video.md](references/short-form-video.md)

---

## Voice Content for Stories (Steve Harvey Pattern)

When the user wants to create daily Instagram/Facebook stories with a voice character (e.g., Steve Harvey), use this workflow:

**Format:** 30 seconds max (100-120 words). Voice character energy: motivational, funny, real-talk.

**Topics (rotate daily):** hackathon grind, agent economy, building in public, morning motivation, crypto/DeFi insights.

**Example tone:**
> "Let me tell you something. When you wake up at 3 AM and your mind is already racing about what you're building — that ain't insomnia. That's purpose. Most people hit snooze. You hit start. That's the difference between dreaming and doing. Now go get it."

**Consolidated Workflow (preferred):**
The Steve Harvey voice content is delivered as part of the **Daily Digest** cron job — not a separate job. The digest includes:
1. Text briefing (yesterday's wins + today's plan) in Steve Harvey tone
2. Voice message via `text_to_speech` tool (ElevenLabs) as a voice note

This avoids redundant cron jobs and gives Jordan a single morning drop with both context and content.

**Pitfall:** Don't create a separate cron job for Steve Harvey stories. Jordan explicitly consolidated these into the Daily Digest to reduce job count and keep mornings simple.

**TTS Credit Management (May 29, 2026):**
Jordan's ElevenLabs Creator plan is $22/mo. Steve Harvey TTS on the daily digest burned ~770 credits per run with no ROI. Jordan's decision: **cut TTS from internal-facing content** (daily digest). Save credits for:
- Monetizable products (GenTech Hub voice companion)
- Hackathon demo videos (submission quality)
- Content that gets views (YouTube, social clips)
- Anything subscriber-facing

**Rule:** Internal-facing content (digests, status reports, internal updates) = plain text only. External-facing content (demos, social, subscriber features) = TTS allowed.

**Manual Workflow (fallback):**
1. User drops a topic
2. Write the script (100-120 words, punchy ending)
3. Generate voice via `text_to_speech` tool
4. Post as Instagram/Facebook story

**TTS:** The `text_to_speech` tool uses the profile's configured ElevenLabs voice. Works out of the box when `ELEVENLABS_API_KEY` is set. No voice_id override needed for the default voice. For voice-specific TTS in cron jobs, use a helper script that calls the ElevenLabs REST API directly (see `scripts/steve-harvey-tts.py` if it exists).

**Usage impact:** ~0.01 credits per story on ElevenLabs. Negligible — can do 10+ stories daily without noticeable usage impact.

**Privacy boundary:** Stories cover public-facing content only (building in public, hackathon updates, motivation). Never reference collaborators' personal info, internal group discussions, or private vault content.

**Content sensitivity rule (May 25, 2026):** NEVER mention prize amounts, dollar figures, or money in any social-facing content. The Daily Digest and all derived posts get repurposed for Facebook, Instagram, and X. Family members see financial numbers and start asking to borrow. Can mention "we won" or "prize track" but keep dollar amounts private. This applies to: digest text, voice scripts, social posts, hackathon announcements, and any content that leaves the inner circle.

## Dual-Channel Content Strategy (GenTech)

Two channels, one production machine. Content is generated from work already happening — builds, hackathons, agent discoveries.

### GenTech Labs (Shorts / Reels / TikTok)
- **Daily shorts:** "What we built today" — Steve Harvey voice, 30 seconds
- **Demo videos:** Animated walkthroughs of products (AAE, Rugcheck, agent tools)
- **Build-in-public series:** The journey from idea to shipped product
- **Educational:** "How AI agents work" explainers

### GenTech Entertainment (YouTube / Podcast)
- **Podcast summaries** in Steve Harvey voice (the hook)
- **Full episodes** with Jordan + co-host
- **Gaming content:** POE2, agent economy discussions
- **Shorts hook → full podcast traffic**

### The Flywheel
```
Daily Short → Teaser for podcast
  → Full episode drops
    → Clips from podcast become shorts
      → Loop repeats
```

**Production cost:** Near zero. ElevenLabs voice + AI scripts + screen recordings. Jordan's time is the only real cost.

**Privacy boundary:** Public-facing brand content only. No personal collaborator details. Private groups = inner circle conversations.

---

## Multi-Persona Voice Pairing

For the full voice cloning workflow (verification, generation, post-processing, delivery), see [references/voice-cloning-workflow.md](references/voice-cloning-workflow.md).

When building products that use contrasting voice personas (e.g., therapy bots, coaching tools, debate frameworks), use the **Good Cop / Bad Cop** voice pairing pattern.

**GenTech Journal (Example)**
A lifestyle/wellness product with two voice personas — originally called "Agent Reparathy" (AAE accountability agent), renamed for public clarity.

| Role | Voice | Voice ID | Style |
|------|-------|----------|-------|
| **Good Cop** | Christel | `kb3G0tkYW7pEGVlHEdu5` | Warm, supportive, positive reinforcement |
| **Bad Cop** | Peter Cullen (YoYo) | `xQbwtCgzouB5QdCSd0Z7` | Gravelly, commanding, voice of judgment |

**Naming strategy:** "Reparathy" is the personality (use in pitches for memorability). "GenTech Journal" is the public brand (clear, accessible).

**Design principles:**
- Contrast is the feature — warm vs. hard, support vs. truth
- Both voices serve the same goal (helping the user level up)
- Good cop builds confidence, bad cop cuts through excuses
- Voice pairing should feel natural, not performative

**When to use this pattern:**
- Coaching/motivation products
- Therapy/wellness tools
- Debate/adversarial frameworks
- Any product where two perspectives serve the user better than one

**Pitfall:** Don't just pick two random voices. The pairing needs intentional contrast — personality, cadence, and emotional register should differ.

---

## Evaluating Inbound Collaboration Offers

When a large account replies to your post saying "this has serious potential, message me for collaboration" or similar, assess before responding.

### Assessment Framework

**Step 1: Profile check**
- Follower count and verification status
- Bio keywords: "DM for business" / "Marketing that delivers" = likely paid promo pitch
- Account age, media count, engagement patterns
- Website link — check if it's a Telegram group (common for crypto marketing accounts)

**Step 2: Find what they replied to**
- Use `fxtwitter` API to read the reply tweet and find the parent status ID
- `curl -s "https://api.fxtwitter.com/i/status/{TWEET_ID}" | python3 -c "import sys,json; d=json.load(sys.stdin)['tweet']; print(d.get('replying_to_status','N/A'))"`
- Then read the parent tweet to see what caught their attention

**Step 3: Classify the offer**

| Signal | Likely Type | Response |
|--------|-------------|----------|
| 211K+ followers, "DM for business" | Paid marketing pitch | Polite, ask what they're offering, don't commit |
| Same-size builder, specific question | Genuine collab interest | Engage, explore mutual value |
| Account with relevant project | Cross-promotion | Evaluate fit, propose specific swap |
| Brand new account, vague offer | Spam/scam | Ignore |

**Step 4: Draft response (don't commit)**
- "Appreciate that! What caught your eye about [project]?"
- Keep it short, ask what they're offering
- Don't pay upfront for promotion without ROI data
- 211K followers seeing your project is eyeballs — but verify engagement quality (likes/comments vs. just follower count)

**Pitfall:** Crypto marketing accounts often mass-reply to project announcements. The "serious potential" message is templated. Always check if they actually looked at your work or just auto-replied to anything with a contract address.

---

## Lean Content Strategy (Jordan's Budget-First Approach)

When Jordan asks about content creation on a budget, use this framework:

### Cost Stack (Monthly)
| Content Type | Tool | Cost |
|-------------|------|------|
| Text posts | X (free) | $0 |
| Screenshots | Phone/Windows Snipping Tool | $0 |
| Threads | X (free) | $0 |
| Code screenshots | Carbon.now.sh | $0 |
| Basic graphics | Canva free tier | $0 |
| Video clips | OBS + ffmpeg | $0 |
| Voice clips | Edge TTS (Hermes built-in) | $0 |
| Premium voice | ElevenLabs (demos only) | $22/mo |

**Total: $0-22/mo** — time is the only real cost.

### Posting Cadence
- **Jordan:** 2-3 posts/day (morning update + evening build-in-public + weekly thread)
- **Gentech (@GentechLabs):** 2 posts/day (shipped work + insight/hot take)
- **Engagement:** Reply to 5 people/day — builds followers faster than posting

### Content Mix
- 40% build-in-public (screenshots, code, demos)
- 30% opinions/insights (AI, crypto, gaming takes)
- 20% community engagement (reply to builders, quote-tweet)
- 10% personal (POE2 wins, life updates)

### Starter Posts for Building in Public
**Jordan:**
1. "Day 1 of building in public. Solo founder + AI agent ecosystem. Here's what we built this week 🧵"
2. "Just submitted to [hackathon]. 30+ tests passing, live demo. Here's what it does..."
3. "POE2 0.5 dropped. My Monk build survived. Here's what changed..."

**Gentech:**
1. "We're GenTech — an AI agent team. No humans, just agents building products. Today we shipped..."
2. "Hot take: Every gaming company will have AI companions within 2 years. We're building ours now."
3. "Published to Swarms Marketplace. Our LP Monitor agent is live on Solana."

### Rule: $0 Before $22
Every text post, screenshot, and thread is free. Only spend on ElevenLabs for demo videos and subscriber-facing content. Internal content = plain text always.

## Audience Split (Jordan's Rule — Jun 2026)

Jordan has two distinct audiences. When creating content, ALWAYS ask which audience or default to splitting:

| Platform | Audience | Tone | Format |
|----------|----------|------|--------|
| **X/Twitter** | Developers, builders, web3 | Technical, concise, code-first | Threads, endpoints, stack details |
| **Facebook** | Non-technical friends/family, general audience | Storytelling, accessible, no jargon | Long-form posts, explain WHY it matters |

**X/Twitter (Developers):**
- Lead with technical details (endpoints, prices, stack)
- Include code examples
- Use acronyms freely (ERC-8004, x402, USDC)
- "Payment IS the auth" — devs get it
- Short, punchy, no hand-holding
- Thread format works well (5-tweet structure: hook → menu → how → stack → close)

**Facebook (Non-technical):**
- Tell the story first,技术 details last
- Explain WHY it matters in plain language
- Use analogies ("like signing up for an account, but the AI does it automatically")
- Break down what each tool does without jargon
- No code, no acronyms without explanation
- Longer-form, conversational
- Single post format (not threads)

**Key difference:**
- X: "GET /v1/score/{mint} → $0.01, ERC-8021 Builder Code attribution"
- Facebook: "The AI agent just pays a few cents and gets the answer instantly"

**Posting strategy:** Post both within 30 minutes. X first (core audience), then Facebook.

**Proven pattern (Jun 22, 2026 — AAE Launch):**
- X thread: 5 tweets (hook → menu → how → stack → close). Technical, code example included.
- Facebook: Single long post explaining the vision in plain language. No code, analogies used.
- Both posted within 30 minutes. X drove developer engagement, Facebook drove general awareness.

## Lyrics & Song Writing

When the user asks for song lyrics, rap verses, or music content:

### Vanito's Preferences (Jun 2026)
- **Format:** Lyrics ONLY. No commentary, no formatting notes, no "here's what I wrote." Just the raw lyrics.
- **Chorus style:** Short, punchy, simple words. 4 lines max. Easy to understand on first listen.
- **Rap style:** Hood/rap energy. Think trap beats. Bars should hit hard and be memorable.
- **Character limit:** Telegram cuts off messages over ~2,800 characters. Keep full songs under this or split into parts.
- **Iterative process:** Vanito will ask for rewrites — shorter, simpler, more hype, different style. Don't get frustrated. Just rewrite.
- **Voice message garble:** Vanito sends voice messages that often garble in transcription. If the request doesn't make sense, ask him to rephrase or type it. Don't guess.

### Song Structure Template
```
[Intro] — 2-4 lines, sets the mood
[Verse 1] — 8-12 bars, story/setup
[Chorus] — 4 lines, simple, repeatable
[Verse 2] — 8-12 bars, escalation
[Chorus]
[Bridge] — 4-6 lines, shift in energy
[Final Chorus] — same as chorus, maybe add emphasis
[Outro] — 2-4 lines, closing statement
```

### Style Variations
| Style | Characteristics |
|-------|----------------|
| **Hood rap** | Street slang, aggressive bars, "on gang" energy |
| **Pop anthem** | Uplifting, crowd-moving, singalong chorus |
| **Diss track** | Roasting, name-drops, punchlines, personal shots |
| **Vintage/synthwave** | Retro references, neon/cars/80s imagery, melodic |

### Pitfall
Don't add explanations, "what do you think?" or "want me to change anything?" after lyrics. Vanito will tell you if he wants changes. Just deliver the lyrics.

## Task-Specific Questions

1. What platform(s) are you focusing on?
2. What's your current posting frequency?
3. Do you have existing content to repurpose?
4. What content has performed well in the past?
5. How much time can you dedicate weekly?
6. Are you building personal brand, company brand, or both?
7. **Who is the audience?** Developers (X) or non-technical (Facebook)?

---

## Dual-Account Posting

For Jordan's dual-account X/Twitter setup (@GentechLabs + @ProtoJay4789), see [references/dual-account-posting.md](references/dual-account-posting.md). Covers:
- Account roles and voice differentiation
- Posting schedule aligned with Jordan's breaks
- xurl setup for agent posting
- Week 1 AAE foundation content
- X API costs and Premium recommendations

## Related Skills

- **copywriting**: For longer-form content that feeds social
- **launch-strategy**: For coordinating social with launches
- **email-sequence**: For nurturing social audience via email
- **marketing-psychology**: For understanding what drives engagement
