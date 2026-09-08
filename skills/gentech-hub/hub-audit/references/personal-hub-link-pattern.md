# Personal Hub Link Pattern for Non-Technical Users

## Problem

When sharing hub links with family members (Vanito, the student, others), raw GitHub markdown URLs (`github.com/.../blob/main/.../HUB.md`) are not user-friendly:
- Links work technically but don't render properly
- GitHub markdown interface is confusing
- No navigation back to main hub
- Poor mobile experience

## Solution

Always use **deployed GitHub Pages URLs** for personal hubs, not raw GitHub files.

## Link Pattern

### Main Hub Entry Point
```
https://protojay4789.github.io/hub.html
```

This is the single entry point for all users. From here, users navigate to their specific sections.

### Personal Dashboard Links
```\n# Student Hub (GenTech Academy — template ready)\nhttps://gentechlabs.net/student.html\n\n# Vanito's POE2 Dashboard (deployed)\nhttps://gentechlabs.net/vanito.html

# Jordan's Travel Dashboard (deployed)
https://protojay4789.github.io/Travels/travel-dashboard.html
```

### Internal Navigation Pattern

Each personal dashboard should have a "Back to Hub" link:

```html
<!-- At top of personal dashboard -->
<a href="https://protojay4789.github.io/hub.html" style="color: #888; font-size: 0.9em;">
  ← Back to GenTech Hub
</a>
```

For markdown files that link to deployed HTML:
```markdown
[← Back to GenTech Hub](https://protojay4789.github.io/hub.html)
```

## Telegram/Chat Platform Formatting

### ❌ Wrong (unclickable)
```
https://github.com/ProtoJay4789/gentech-vault/blob/main/12-Christel/HUB.md
```
Wrapped in code blocks → prevents clicking

### ✅ Right (clickable)
```
https://protojay4789.github.io/hub.html
```
Plain text → auto-converts to clickable link in Telegram

## Dashboard Registry Pattern

All personal dashboards should be registered in `/root/vaults/gentech/Dashboards/dashboard-registry.json`:

```json
{
  "hub": {
    "path": "Profiles/hub.html",
    "owner": "jordan",
    "description": "Central hub linking all dashboards. Settings gear for default tab preference."
  },
  "dashboards": [
    {
      "id": "student-academy",
      "name": "the student GenTech Academy",
      "owner": "student",
      "type": "academy",
      "status": "pending",
      "path": "examples/student-hub-template.html",
      "deployed_url": "https://gentechlabs.net/student.html",
      "created": "2026-07-25",
      "description": "GenTech Academy student hub — template ready for deployment"
    }
  ]
}
```

## Deployment Workflow

When adding a new personal dashboard:

1. **Create HTML file** in appropriate directory (`Cookbook/`, `Gaming/`, `Travels/`, etc.)
2. **Add "Back to Hub" link** at top of page
3. **Register in dashboard-registry.json** with `deployed_url` field
4. **Sync vault to GitHub**: `cd /root/vaults/gentech && ob sync`
5. **Sync GitHub Pages repo**: 
   ```bash
   cd /root/ProtoJay4789.github.io
   git add .
   git commit -m "feat: add [dashboard name]"
   git push origin main
   ```
6. **Verify deployed URL**: `curl -I https://protojay4789.github.io/path/to/dashboard.html`

## Common Pitfalls

### Pitfall: Confusing Git Repos

There are TWO repos:
- **Vault repo**: `gentech-vault` — source files, markdown, raw data
- **Pages repo**: `ProtoJay4789.github.io` — deployed HTML dashboards

Both need to be synced when updating dashboards.

### Pitfall: Relative Links in Deployed HTML

Don't use relative paths like `../hub.html` — they break when deployed.
Always use absolute URLs: `https://protojay4789.github.io/hub.html`

### Pitfall: Forgetting the "Back to Hub" Link

Users get lost without navigation back to main entry point. Always add the link pattern.

### Pitfall: Code Blocks in Chat Messages

When sharing links via Telegram/other platforms, don't wrap in code blocks:
- ✅ `https://protojay4789.github.io/hub.html`
- ❌ `https://protojay4789.github.io/hub.html` (in code block)

## Testing Checklist

Before sharing link with user:

- [ ] Link is deployed URL (not raw GitHub markdown)
- [ ] Link works in incognito browser (no cached auth issues)
- [ ] "Back to Hub" navigation works
- [ ] Mobile-responsive (test on phone viewport)
- [ ] Page loads within 3 seconds (check 4G connection)
- [ ] No 404 errors in browser console
- [ ] JSON data files are valid and accessible

## Reference Examples

**Student Hub (GenTech Academy — template):**
```markdown
# Student Hub 🎓

**[← Back to GenTech Labs](https://gentechlabs.net)**

Welcome to the GenTech Academy! This is your starter hub.

---

## 🚀 Your Journey

Coming soon — lessons, builds, and projects.
```

**Deployed URL to share:**
```
https://gentechlabs.net/student.html
```

## History

- **July 25, 2026** — Updated for GenTech Academy: Christel hubs replaced with the student student hub template.