# External Resources: Operator's Guide to Hermes Agent

## Tony Simons — "The Operator's Guide to Hermes Agent"
- **URL:** https://guide.tonysimons.dev/
- **Author:** @tonysimons_
- **Type:** Free ebook (email-gated)
- **Found:** Jul 25, 2026 (via X post about multi-agent setup)

### What It Covers
- Tools, Memory, Skills — the three pillars
- Cron jobs and Gateway setup
- Multi-agent Kanban workflows
- The "Operator Loop"
- Where people screw this up (Chapter 6)

### Why It Matters for Gentech
Tony's architecture emphasizes **clear ownership** over more agents — exactly what we do with topic routing (one brain, four channels). His "Operator Loop" pattern complements our session-hygiene/session-startup/wake-up-protocol lifecycle.

### Takeaways from His Multi-Agent Takedown
- Disposable subagents vs permanent profiles vs swarms
- Credentials stay at the top (don't inherit MCP keys)
- Not every agent needs every skill
- Most multi-agent setups fail because nobody owns anything
- More agents aren't the upgrade — clearer ownership is

### Our Counter-Architecture
Rather than N subagents with split context, we run:
- **1 agent (Gentech)** with topic-routed personalities per channel
- **1 shared brain (vault)** with session-hygiene auto-save
- **1 context bridge** that preserves state across restarts
- Characters like Echo are **personality layers** on delivery, not separate agent instances
