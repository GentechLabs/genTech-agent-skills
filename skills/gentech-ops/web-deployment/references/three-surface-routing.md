# Three-Surface Content Routing (Jordan-endorsed, Aug 2026)

There are THREE public surfaces that must stay cleanly separated. They are NOT
duplicates — each has a distinct job, and content must be routed to the right one
every time a change is made (same discipline as model routing / cron routing).

| Surface | URL | Job | What goes here |
|---------|-----|-----|----------------|
| **Main site** | `gentechlabs.net` | The story | Company narrative, problems we solve, roadmap, AAE stack, API services, case studies |
| **Portfolio** | `/var/www/portfolio/` | The person | Jordan's personal work history, career, skills, experience, connect |
| **Demo site** | `gentechlabs.net/demo.html` | The proof | Live, working, touchable artifacts — demos, videos, endpoints, walkthroughs |

**The rule in one line:** *Main site = the story. Portfolio = the person. Demo
site = the proof. Internal = never public.*

## Routing decisions

- A **live, working artifact** (demo video, endpoint, walkthrough) → **demo site**.
  The portfolio should only *reference* it (link to the demo site), never embed it.
- A **milestone / plan / roadmap item** → **main site** (or portfolio if it's
  personal career progress).
- **Internal ops** (Mess Hall, ideas board, considerations, vault health, cron
  status) → **vault only, NEVER any public surface.**
- **Token / support / ecosystem promotion** → not on any public surface unless
  it's a dedicated, intentional page.

## Audit finding (Aug 2026)

The portfolio had drifted into ~80% duplication of the main site (same title
"Jordan the ProtoJay", same Core Projects cards: Agent Arena, Agent Kit, Rugcheck,
Agent Credit Score, AgentEscrow, Speech Engine) AND carried internal ops content
(Mess Hall, Support Ecosystem, stale Hackathon status, One-Liner Deploy).

Fix: strip the portfolio to a clean personal/career page (About, Journey, Skills,
Experience, Connect), move live project cards to the demo site, delete internal
sections entirely.

## Standing discipline

Every time content is added or changed, ask "which of the three surfaces does
this belong on?" before deploying. Route it there, don't duplicate it across
surfaces. This is the same routing discipline Jordan applies to model routing and
cron routing — content routing is a first-class routing layer.
