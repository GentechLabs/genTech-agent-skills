# Tunnel Troubleshooting Guide

**Context:** When deploying services on VPS with external access needs (webhooks, mobile apps, smart glasses), tunnel services often fail silently. This guide captures proven diagnostic patterns and fixes.

## Common Tunnel Services

| Service | Setup | Pros | Cons | Use Case |
|---------|-------|------|------|----------|
| **Cloudflare Tunnel** | `cloudflared tunnel --url http://localhost:PORT` | Free, no signup, HTTPS | Returns 404 even when service works, routing issues | First attempt |
| **Localtunnel** | `npm install -g localtunnel && lt --port PORT` | Simple, HTTPS | "Bad Gateway" errors, 10-15 min timeouts | Quick testing |
| **Ngrok** | `ngrok http PORT` | Reliable, persistent | Requires signup/auth token | Production, persistent access |
| **Serveo** | `ssh -R 80:localhost:PORT serveo.net` | No signup | Host key verification failures, unstable | Avoid |
| **Proper Domain** | Buy domain + point A record + Let's Encrypt SSL | Permanent, reliable | Costs money (~$10/year), setup time | Production, Japan trip critical |

## Diagnostic Pattern (When Tunnel Returns 404/Bad Gateway)

**Step 1: Verify Server Is Actually Running**
```bash
# Check process
ps aux | grep "node server" | grep -v grep

# Check port binding
netstat -tlnp | grep PORT
# tcp6  0  0  :::PORT  → listening on IPv6 localhost only
# tcp   0  0  0.0.0.0:PORT → listening on all interfaces

# Test locally
curl http://localhost:PORT/api/pois | jq '.[0].name'
curl http://localhost:PORT/ | head -10
```

**Expected:** Local curls return HTTP 200 + actual content. If this fails, issue is server, not tunnel.

**Step 2: Diagnose Tunnel vs Server Issue**
```bash
# Test tunnel directly with verbose output
curl -v https://tunnel-url/ 2>&1 | grep -E "(HTTP/|Content-Type|Connected)"

# Check if server needs 0.0.0.0 binding
grep "app.listen" /root/project/server.js
```

**If local works but tunnel returns 404:** Server is listening on localhost-only. Tunnel services need 0.0.0.0 binding.

**If local returns 200 but tunnel returns "Bad Gateway":** Tunnel service issue (Localtunnel maintenance, Cloudflare routing problems). Wait 1-2 minutes or try different service.

**Step 3: Fix Server Binding (if needed)**
```bash
# Kill existing server
pkill -f "node server" || fuser -k PORT/tcp

# Patch server.js to listen on 0.0.0.0
sed -i 's/app\.listen(PORT,/app.listen(PORT, '"'"'0.0.0.0'"'"',/' server.js

# Restart server
PORT=PORT node server.js > /tmp/server.log 2>&1 &

# Verify binding
netstat -tlnp | grep PORT  # Should show "tcp   0  0  0.0.0.0:PORT"
```

**Step 4: Test Tunnel Again**
```bash
# Wait 30 seconds for server startup
sleep 30

# Test tunnel
curl -s https://tunnel-url/api/pois | jq '.[0].name'
curl -s https://tunnel-url/ | head -10

# If still failing, try different tunnel service
```

## Proven Failures and Workarounds

### HUD Travel Deployment Session (2026-07-07)

**Issue:** Cloudflare tunnel returning 404 while local server responded correctly.

**Root Cause:** HUD server (`leestar/meta-rayban-display-travel-hud`) hardcoded `app.listen(PORT, () => {...})` which defaults to localhost. Server showed `tcp6 :::3001` in netstat - IPv6 localhost binding only.

**Fix Applied:**
```bash
# Patch /root/reference-hud/server.js line 718
# From: app.listen(PORT, () => {...})
# To: app.listen(PORT, '0.0.0.0', () => {...})
```

**Verification:** After patch and restart, netstat showed `tcp   0  0  0.0.0.0:3001` - binding on all interfaces.

**Result:** Tunnel still returned 404. Further investigation revealed Localtunnel "Bad Gateway" service issues, not the HUD server.

**Lesson Learned:** Server binding is necessary but not sufficient. Tunnel service health matters more than tunnel configuration.

### Localtunnel Watchdog Pattern

**Issue:** Localtunnel URLs timeout after ~10-15 minutes. Single command returns, but tunnel dies.

**Solution:** Watchdog script that auto-restarts tunnel when it fails.

```bash
#!/bin/bash
# /root/localtunnel-watchdog.sh
while true; do
    if ! ps aux | grep "lt --port 3001" | grep -v grep > /dev/null; then
        lt --port 3001 > /tmp/localtunnel-current.log 2>&1 &
        echo "Tunnel restarted at $(date)" >> /tmp/watchdog-main.log
    fi
    sleep 10
done
```

**Usage:**
```bash
chmod +x /root/localtunnel-watchdog.sh
nohup /root/localtunnel-watchdog.sh > /tmp/watchdog-main.log 2>&1 &
tail -f /tmp/watchdog-main.log
cat /tmp/localtunnel-current.log  # Get current URL
```

**Pitfall:** Localtunnel "Bad Gateway" errors are service-side. Watchdog can restart, but won't fix service issues. Wait 1-2 minutes or switch to ngrok/proper domain.

### User Preference: Don't Give Untested URLs

**User Feedback:** "what is showing me that the URL you sent me is just showing me a black screen?" "Well, it's just like I want you to try to make it work."

**Lesson:** Never provide tunnel URLs to the user without first testing them yourself.

**Workflow Change:**
```bash
# AFTER starting tunnel, wait 30 seconds then test
sleep 30
curl -s https://tunnel-url/ | head -5

# If returns HTML content (not 404/Bad Gateway), give URL to user
# If fails, keep troubleshooting before giving URL
```

**Why:** User needs working URLs, not "hope this works" promises. Every URL provided must be verified to return actual content.

## Production Deployment Guidance

**For critical access (Japan trip, smart glasses, mobile apps):**

1. **Use proper domain with SSL** - ~$10/year, permanent, reliable
   ```bash
   # 1. Buy domain (Namecheap, GoDaddy)
   # 2. Point A record to VPS IP
   # 3. Set up Let's Encrypt SSL
   # 4. Permanent HTTPS access
   ```

2. **Ngrok with auth token** - Free account, reliable, persistent
   ```bash
   ngrok config add-authtoken YOUR_TOKEN
   ngrok http PORT  # Tunnel runs until stopped
   ```

3. **Avoid free tunnel services for critical access** - Cloudflare, Localtunnel are experimental, not production-ready

**For development/testing:**

1. **Cloudflare Tunnel first** - Quick setup, no signup
2. **Localtunnel with watchdog** - If Cloudflare fails, try Localtunnel
3. **SSH port forwarding** - For local testing only:
   ```bash
   ssh -L 3001:localhost:3001 your-vps-ip
   # Then open http://localhost:3001 locally
   ```

## Common Error Transcripts

### Cloudflare Tunnel 404
```
curl https://tunnel-url/
{"detail":"Not Found"}

netstat -tlnp | grep 3001
tcp6       0      0  :::3001                 :::*                    LISTEN      PID/node

# Diagnose: Server listening on localhost-only
# Fix: Patch server to listen on 0.0.0.0
```

### Localtunnel Bad Gateway
```
curl https://tunnel-url.loca.lt/
Bad Gateway

curl http://localhost:3001/
# Returns actual HTML content

# Diagnose: Localtunnel service issue (not your server)
# Action: Wait 1-2 minutes, restart watchdog, or switch service
```

### Ngrok Auth Failed
```
ngrok http 3001
ERROR: authentication failed: This ngrok session is not authenticated.
ERROR: Sign up for an account: https://dashboard.ngrok.com/signup

# Diagnose: Ngrok requires account and auth token
# Action: Sign up, get token, run: ngrok config add-authtoken YOUR_TOKEN
```

### Serveo Host Key Verification
```
ssh -R 80:localhost:3001 serveo.net
Host key verification failed.

# Diagnose: Serveo requires known_hosts entry or has server-side issues
# Action: Avoid Serveo, use alternative service
```

## Summary Checklist

When setting up external access:

- [ ] Verify server runs locally: `curl http://localhost:PORT`
- [ ] Check port binding: `netstat -tlnp | grep PORT`
- [ ] If localhost-only binding, patch server to 0.0.0.0
- [ ] Start tunnel service
- [ ] Wait 30 seconds for tunnel initialization
- [ ] Test tunnel URL: `curl https://tunnel-url/`
- [ ] Only provide URL to user after verifying it returns content
- [ ] For critical access: use proper domain or ngrok, not free tunnels