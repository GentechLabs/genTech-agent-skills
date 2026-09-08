# Hermes Dashboard Remote Access

**Created**: July 1, 2026  
**Purpose**: Direct web UI access for VPS agent from desktop without API overhead

---

## Discovery

**User Preference (Jordan, July 1, 2026):**
> \"I think I just found a better way to do it. Do we have a dashboard?\"
> \"I think option A might be better because they want a remote URL. It says path prefixes are supported, for example, slash hermes.\"

**Key Insight**: Hermes Dashboard provides built-in web UI with embedded chat - no custom API needed. Remote access via Cloudflare Tunnel with path prefix is cleaner than building task APIs.

---

## Dashboard Status

**Current Configuration:**
- ✅ Running: `http://127.0.0.1:9119/?profile=gentech`
- 🔑 Session token: `AU79rrs4HYs-5TFSkunA3FzvcXeK9eBs2TEeYvmZobU`
- 🔌 Embedded chat: enabled
- 📊 Profile: `gentech`

**Start/Stop:**
```bash
hermes dashboard              # Start web UI dashboard (port 9119)
hermes dashboard --stop       # Stop running dashboard processes
hermes dashboard --status     # List running dashboard processes
```

---

## Remote Access Options

### Option A: Hermes Dashboard + Cloudflare Tunnel (Recommended)

**Architecture:**
```
Desktop Browser ──► Cloudflare Tunnel ──► VPS Dashboard
                      │                         │
                   HTTPS                   127.0.0.1:9119
                      │                         │
                  https://gentechlabs.net/hermes
```

**Cloudflare Tunnel Options:**

**A1: Quick Tunnel (Temporary, No Setup)**
```bash
cloudflared tunnel --url http://127.0.0.1:9119
```

**Benefits:**
- Works instantly, no setup
- Generates random URL: `https://<random>.trycloudflare.com`

**Drawbacks:**
- Random URL changes each run
- **Rate-limited**: Returns `429 Too Many Requests` after repeated attempts
- No uptime guarantee (Cloudflare Online Services Terms apply)

**Error Pattern:**
```
Error code: 429 Too Many Requests
failed to unmarshal QuickTunnel: invalid character 'e' looking for beginning of value
```

**Use When:** Quick test, temporary access

---

**A2: Named Tunnel (Production, Path Prefix)**
```bash
# 1. Create named tunnel in Cloudflare Dashboard
#    Zero Trust > Networks > Tunnels > Create
#    Name: gentech-hermes-dashboard

# 2. Run install command (creates credentials)
#    This generates: ~/.cloudflared/<tunnel-id>.json

# 3. Configure with path prefix
cat > ~/.cloudflared/config.yml << EOF
tunnel: <tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  # Hermes Dashboard with path prefix
  - hostname: gentechlabs.net
    path: /hermes/*
    service: http://127.0.0.1:9119
  
  # Default dashboard access (subdomain)
  - hostname: dashboard.gentechlabs.net
    service: http://127.0.0.1:9119
  
  # Catch-all
  - service: http_status:404
EOF

# 4. Run tunnel
cloudflared tunnel --config ~/.cloudflared/config.yml run gentech-hermes-dashboard
```

**Access Points:**
- Path prefix: `https://gentechlabs.net/hermes`
- Subdomain: `https://dashboard.gentechlabs.net`

**Benefits:**
- Stable URL (same every time)
- Path prefix supported
- HTTPS by default
- Uptime guarantee (paid Cloudflare)

**Drawbacks:**
- Requires Cloudflare account
- One-time setup (5-10 minutes)

**Use When:** Production access, regular desktop use

---

### Option B: SSH Reverse Tunnel (No Cloudflare)

**Setup:**
```bash
# On Desktop (Forge), run reverse tunnel
ssh -N -R 9119:127.0.0.1:9119 root@2.24.195.196
```

**Desktop Access:**
```bash
# Access via localhost (tunnel forwards to VPS)
http://localhost:9119
```

**Benefits:**
- Zero external dependencies
- No Cloudflare account needed
- Simple SSH command

**Drawbacks:**
- Requires SSH access from desktop to VPS
- Desktop must run tunnel command
- Tunnel breaks on desktop sleep/restart
- Less secure than HTTPS tunnel

**Use When:** SSH access exists, quick prototype

---

## Cloudflare Tunnel Troubleshooting

### Rate Limiting (Quick Tunnel)

**Symptom:**
```
Error code: 429 Too Many Requests
failed to unmarshal QuickTunnel: invalid character 'e' looking for beginning of value
```

**Cause:** Quick tunnels have rate limits. Too many quick attempts trigger 429.

**Fix:**
1. Wait 5-10 minutes before retrying
2. Use named tunnel instead (no rate limits)
3. Don't use quick tunnel for production

### Credentials Missing (Named Tunnel)

**Symptom:**
```
open /root/.cloudflared/config.yml: no such file or directory
Error decoding origin cert: missing token in the certificate
```

**Cause:** Credentials file not created or tunnel not authenticated.

**Fix:**
1. Visit Cloudflare Dashboard → Zero Trust > Networks > Tunnels
2. Create named tunnel: `gentech-hermes-dashboard`
3. Run install command provided (creates credentials)
4. Verify credentials exist: `ls -la ~/.cloudflared/`

---

## Recommended Setup (July 2026)

**For Gentech VPS → Desktop Access:**

1. **Use Option A2: Named Tunnel with Path Prefix**
   - Setup: One-time (5-10 minutes)
   - URL: `https://gentechlabs.net/hermes` (stable)
   - Benefits: HTTPS, path prefix, uptime guarantee

2. **Backup: Quick Tunnel Script**
   - File: `tunnel-dashboard.sh`
   - Use when: Testing, temporary access

---

**Next Steps:**
1. Set up named tunnel with Cloudflare Dashboard
2. Configure DNS: CNAME `dashboard.gentechlabs.net`
3. Test desktop access: `https://gentechlabs.net/hermes`
4. Add tunnel monitoring cron job
5. Document in vault for future reference