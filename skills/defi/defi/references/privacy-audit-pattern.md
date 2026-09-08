# Privacy Audit Pattern for Public Repos

## When to Run
- Before any repo goes public
- After adding wallet addresses, API keys, or personal info to code
- Periodically (monthly) for active public repos

## What to Search For

### High Priority (Rotate Immediately)
| Pattern | Grep | Risk |
|---------|------|------|
| Wallet addresses | `0x[0-9a-fA-F]{40}` | On-chain tracking |
| API keys | `sk_live\|sk_test\|api_key.*=\|AIzaSy` | Account takeover |
| GitHub tokens | `ghp_[A-Za-z0-9]{36}` | Repo access |
| Private keys | `PRIVATE_KEY\|MNEMONIC\|SEED_PHRASE` | Fund theft |

### Medium Priority (Review)
| Pattern | Grep | Risk |
|---------|------|------|
| Email addresses | `@gmail\|@yahoo\|@hotmail` | Spam/phishing |
| Phone numbers | `\+1[0-9]{10}` | Social engineering |

### Low Priority (Usually Intentional)
| Pattern | Notes |
|---------|-------|
| LinkedIn profiles | Usually intentional on portfolio sites |
| Public wallet addresses | Blockchain is public anyway |

## Search Commands

```bash
# Wallet addresses in code (excluding node_modules/.git)
grep -rl "0xYOUR_ADDRESS" /root/repos/ /root/projects/ \
  --include="*.md" --include="*.json" --include="*.js" \
  --include="*.py" --include="*.html" --include="*.env" \
  | grep -v node_modules | grep -v .git/

# API keys in .env files
grep -rn "API_KEY\|SECRET\|TOKEN" /root/repos/ \
  --include="*.env" | grep -v ".env.example"

# Check repo visibility
gh repo view OWNER/REPO --json visibility -q '.visibility'
```

## Remediation

### Wallet Addresses
Replace with environment variable reference:
```python
# ❌ Hardcoded
WALLET = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"
# ✅ Environment variable
WALLET = os.environ.get("WALLET_ADDRESS", "")
```

### API Keys
1. Revoke the exposed key immediately
2. Generate a new key
3. Update the .env file
4. Add .env to .gitignore if not already
5. Commit and push

### If Key Was in Public Repo
Assume the key is compromised. Rotate ALL keys created around the same time.

## Post-Audit Checklist
- [ ] All wallet addresses replaced with env vars
- [ ] All API keys rotated
- [ ] GitHub tokens revoked and regenerated
- [ ] .env files in .gitignore
- [ ] Changes committed and pushed
