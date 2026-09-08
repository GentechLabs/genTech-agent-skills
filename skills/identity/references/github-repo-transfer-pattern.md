# GitHub Repository Transfer Pattern

**Purpose:** Separating personal repositories from professional organization work.

## When to Use

- Launching a professional brand (e.g., GenTech Labs)
- Recruiters clicking your business link should NOT see personal projects
- Business site should link to org, not personal account

## Pattern

```
Personal Account (ProtoJay4789)
├── Portfolio (ProtoJay4789.github.io)
├── Personal projects
└── Private vaults

Organization Account (Gentech-Labs)
├── All professional repos
├── APIs and products
└── Hackathon submissions
```

## Transfer Workflow

### 1. Create or Verify Org

```bash
gh org list | grep -i <org-name>
```

### 2. List Repos to Transfer

```bash
gh repo list <personal-username> --limit 30
```

### 3. Transfer via API

```bash
# Get auth token
TOKEN=$(gh auth token | cut -d' ' -f1)

# Transfer each repo
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/<personal>/<repo>/transfer \
  -d '{"new_owner":"<org-name>","team_ids":[]}'
```

**Pitfall:** `gh repo transfer --yes` doesn't exist. Use curl API instead.

### 4. Verify Transfer

```bash
gh repo list <org-name> --limit 30
```

### 5. Update Links

- Business site CTA: `https://github.com/<org-name>`
- Business site docs: Reference org repos
- Personal portfolio: Keep separate

## Example: GenTech Labs Transfer

| Category | Moved To |
|----------|----------|
| gentech-agents | Gentech-Labs |
| gentech-hub | Gentech-Labs |
| genTech-agent-kit | Gentech-Labs |
| ... (11 more) | Gentech-Labs |
| ProtoJay4789.github.io | Stayed personal |
| gentech-vault | Stayed personal |

## Outcomes

- Recruiters see professional brand only
- Personal work stays personal
- Clear boundary between professional and personal