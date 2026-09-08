# GOAT Network AgentKit — Contribution Pattern

**GOAT AgentKit** is a TypeScript SDK for building AI agents on GOAT Network (Bitcoin L2). 15 plugins, 118 actions. x402 + ERC-8004 native.

## Assessment

- **Stars:** 4 ⭐ — very early, high signal
- **Forks:** 5
- **Contributors:** 4 (including Claude bot)
- **Open issues:** 2 (#2 extensionless imports, #4 ERC-8004 registry mismatch)
- **Forking:** API-forking blocked (403). Must create standalone repo + push manually
- **GitHub REST API:** Works for reading — `curl -s "https://api.github.com/repos/GOATNetwork/agentkit"`

## Contribution Strategy

### Quick Wins (low effort, high signal)

1. **Fix #4** — ERC-8004 testnet3 identity registry address mismatch. The `addresses.ts` file has `0x5560...` but the reputation registry is linked to `0x54b8...`. Fix: update the identity registry address in `plugins/erc8004/addresses.ts`.

2. **Build a compliance plugin** — GOAT has 15 plugins but no compliance/security. Port our scanner patterns:
   - `compliance.validate_x402_payment` — pre-flight checks on payment requests
   - `compliance.validate_x402_response` — validate HTTP 402 responses against spec
   - `compliance.check_agent_identity` — ERC-8004 agent registration + reputation check

### Plugin Pattern (for building new plugins)

Each plugin follows this structure:
```
plugins/{name}/
  index.ts           # Re-exports all actions
  actions/
    {action-name}.ts # Each action as ActionDefinition
```

Action shape:
```typescript
export function myAction(wallet: WalletProvider): ActionDefinition<Input, Output> {
  return {
    name: 'plugin.action_name',
    description: '...',
    riskLevel: 'read' | 'low' | 'medium' | 'high',
    requiresConfirmation: boolean,
    networks: ['goat-mainnet', 'goat-testnet'],
    zodInputSchema: inputSchema,
    async execute(ctx, input) { ... },
  };
}
```

### Submission Workflow

1. Clone repo
2. Create branch: `git checkout -b feat/my-feature`
3. Make changes, commit
4. Push to a standalone repo (since API forking is blocked):
   - Create new repo via GitHub API: `POST /user/repos`
   - Add remote: `git remote add fork https://{USER}:{TOKEN}@github.com/{USER}/{REPO}.git`
   - Push branch: `git push -f fork feat/my-feature`
5. Submit PR via GitHub API: `POST /repos/GOATNetwork/agentkit/pulls`
   - Set `head: "ProtoJay4789:feat/my-feature"` (using the standalone repo name)
   - Set `base: "main"`
   - Note: May fail with "invalid" head error if the repo isn't a fork. Fallback: manual web UI.

### Manual PR Submission (when API fails)

1. Go to https://github.com/ProtoJay4789/{standalone-repo}
2. Click "Contribute" → "Open Pull Request"
3. Verify: `GOATNetwork/agentkit` ← `ProtoJay4789:feat/branch-name`
4. Paste the PR description
5. Click "Create Pull Request"

### PR Body Template

Use markdown with sections: Summary, New Features, Bug Fix, Why This Matters, Verification.