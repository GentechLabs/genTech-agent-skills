# Unity CLI — Agent-Native Game Dev Pipeline (Jul 22, 2026)

Unity released a standalone CLI (`unity` binary) on Jul 20, 2026 — terminal-native path for connecting coding agents, CI pipelines, and custom tooling to Unity.

## Key Features
- **Standalone binary** — install editors, modules, projects, auth from terminal. No UI needed.
- **com.unity.pipeline** package — drives a *running* Editor over a local API. Add `[CliCommand]` attribute to any static method.
- **`unity command eval`** — executes live C# inside a running Editor or Player. No recompile, no domain reload. Returns in milliseconds.
- **MCP Mode** — compatible with existing MCP-based agents.
- **Free, no concurrency limits** on the MCP server.

## Why It Matters for Agents
- Structured JSON output — agents parse results cleanly
- Self-describing Editor — agents discover available commands at runtime
- Eval reaches Unity's *entire* API — rendering, physics, animation, asset database
- Runtime mode — point CLI at a development build Player

## Integration Points for GenTech
1. **Hermes skill** — automate game builds and testing via Unity CLI
2. **x402 endpoints** — wrap Unity build services as pay-per-call APIs
3. **Gaming Hub** — integrate with automated deployment pipeline
4. **Agent Arcade** — automate game testing loop if pivoting to trading games

## The Bigger Picture
Unity just built agent-native interfaces (CLI + structured output + self-describing commands + live eval). This is the pattern every major platform is adopting. Game devs are the perfect entry point for the agent economy — they already understand microtransactions, asset marketplaces, and automation.

## Build Queue
- #66 — Unity CLI Integration (Hermes skill, assigned to Forge)
- #67 — Game Studio Agent Economy Watch (weekly research, assigned to Gentech)
