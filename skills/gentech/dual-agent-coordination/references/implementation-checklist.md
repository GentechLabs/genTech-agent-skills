# Dual-Agent Implementation Checklist

## Quick Start Commands

### Desktop Setup (Forge)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl start ollama

# Pull model with 128K+ context
ollama pull llama3.1:8b

# Verify installation
curl http://localhost:11434/api/tags
```

### DeepSeek Configuration
```bash
# Monitor token usage (weekly check)
curl -s "https://api.deepseek.com/v1/usage" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"

# Check remaining tokens
jq '.data.total_tokens_used' deepseek-usage.json
```

### Hermes Config Updates
```bash
# Add to ~/.hermes/profiles/<profile>/config.yaml
providers:
  deepseek:
    base_url: "https://api.deepseek.com/v1"
    default_model: "deepseek-v4-flash"
    name: DeepSeek
    transport: openai_chat
    
  ollama:
    base_url: "http://localhost:11434/v1"
    default_model: "llama3.1:8b"
    name: Ollama Local
    transport: openai_chat
```

---

## Daily Sync Commands

### Vault Sync
```bash
# Check git status
cd /root/vaults/gentech
git status

# Sync if clean
git pull --rebase
git add .
git commit -m "dual-agent sync"
git push

# Obsidian sync (if configured)
ob sync
```

### Cross-Agent Coordination
```bash
# Check implementation status
grep -r "forge-implementation-plan.md" /root/vaults/gentech/
grep -A5 "Dual-Agent Coordination" /root/vaults/gentech/00-HQ/current-status.md
```

---

## Monitoring Commands

### Token Usage Tracking
```bash
# DeepSeek weekly usage
echo "Checking DeepSeek usage..."
curl -s "https://api.deepseek.com/v1/usage" | jq '.data.total_tokens_used'

# Alert if >80% of 5M used
if [ $(curl -s "https://api.deepseek.com/v1/usage" | jq '.data.total_tokens_used') -gt 4000000 ]; then
    echo "WARNING: DeepSeek tokens >80% used"
fi
```

### System Health
```bash
# Check cron jobs
hermes cron list

# Check Ollama service
systemctl is-active ollama

# Check model availability
curl http://localhost:11434/api/generate -d '{"model":"llama3.1:8b","prompt":"test","stream":false}'
```

---

## Troubleshooting Commands

### Common Issues
```bash
# Ollama not running
sudo systemctl start ollama
sudo systemctl enable ollama

# Context window error
# Ensure llama3.1:8b (128K) not qwen2.5-coder:7b (32K)

# DeepSeek auth error
export DEEPSEEK_API_KEY="your_key_here"
```

### Performance Issues
```bash
# Check RAM usage (llama3.1:8b needs ~4.9GB)
free -h

# Check GPU usage (if available)
nvidia-smi
```