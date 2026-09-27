---
name: self-hosted-oss-deployment
description: "Deploy open-source projects on VPS — prerequisites, env config, S3/MinIO setup, multi-service orchestration, and local dev patches. Covers the full lifecycle from clone to running stack."
version: 1.1.0
author: Gentech
tags: [devops, self-hosted, oss, minio, s3, vps, deployment]
---

# Self-Hosted OSS Deployment

**Purpose:** When we need to run an open-source project on our VPS (for testing, integration, or hackathon prep), follow this structured workflow. Covers the full lifecycle from clone to running stack.

**Trigger:** User says "spin it up", "self-host it", "let's try it", or shares an OSS repo with intent to run locally.

---

## Deployment Workflow

### Phase 1: Prerequisites Check

Before cloning, verify the VPS has what the project needs:

```bash
# Check all common prerequisites at once
echo "=== Node ===" && node --version
echo "=== pnpm ===" && pnpm --version 2>/dev/null || echo "MISSING"
echo "=== Rust ===" && rustc --version 2>/dev/null || echo "MISSING"
echo "=== Cargo ===" && cargo --version 2>/dev/null || echo "MISSING"
echo "=== FFmpeg ===" && ffmpeg -version 2>/dev/null | head -1 || echo "MISSING"
echo "=== Docker ===" && docker --version 2>/dev/null || echo "MISSING"
echo "=== Disk ===" && df -h / | tail -1
```

**Common prerequisites by project type:**
- **Node.js projects:** Node LTS + pnpm 10.x (not npm)
- **Rust projects:** rustc + cargo + cargo-watch (`cargo install cargo-watch`)
- **Python projects:** Python 3.11+ + pip/poetry
- **Go projects:** golang-go (`apt-get install -y golang-go`). Build with `go build -o binary-name .` from repo root. Check `go.mod` for module path.
- **Media projects:** FFmpeg (usually pre-installed)
- **Storage projects:** Docker (for MinIO)

### Capacity Gate (before committing to deploy)

Check RAM and co-tenants BEFORE cloning a heavy stack — the VPS also runs revenue-critical services:

```bash
free -h                                       # total vs available
docker ps --format '{{.Names}}\t{{.Image}}'   # what already lives here
ss -lntp | grep -E ':8000|:3000|:5175'        # candidate ports from the project's compose file
```

- Read the project's `docker-compose.yml` for its port bindings and check each against `ss -lntp` — project defaults (8000, 3000, 5175) collide often; remap to free ports instead of stopping existing services.
- ML-heavy stacks (torch, transformers, whisper, ultralytics, mediapipe) typically state an 8GB+ RAM floor. If available RAM is within a couple GB of that floor, do NOT deploy beside live paid services — memory pressure on the revenue path costs more than the tool earns.
- Pick the home in this order: hosted free tier (zero infra, proves the workflow) → desktop GPU box → separate VPS. Reserve the shared production VPS for lightweight services.
- If deployment is deferred pending a user decision, record the capacity numbers (RAM floor vs available, port conflicts) in the queue item so the next session doesn't re-derive them.

### Phase 2: Clone and Install

```bash
cd /root/repos
git clone https://github.com/{owner}/{repo}.git
cd {repo}
pnpm install  # or npm install, cargo build, pip install -r requirements.txt
```

**Pitfall:** `pnpm install` may warn about ignored build scripts. For native modules (sharp, esbuild, @nestjs/core), you need to approve builds:
```bash
# Non-interactive way (if available)
pnpm approve-builds --all
# Or rebuild specific ones
pnpm rebuild esbuild sharp
```

**Pitfall — LICENSE exceptions carve directories out of the open license.** When GitHub's API reports `license.spdx_id: NOASSERTION`, the LICENSE file carries custom terms — fetch and read its head before calling the repo MIT/Apache. Exception clauses ("everything under `X/` is licensed under the commercial license in `X/LICENSE`") exclude whole directories, commonly the multi-tenant auth/billing layer. Self-host and build on only the MIT-covered parts; never lift the excepted directory into a product or a deployment.

### Phase 3: Environment Configuration

**Rule: Never hardcode API keys.** Use `.env` files from `.env.example` templates.

```bash
# Find env examples
ls apps/*/.env.example 2>/dev/null || ls .env.example 2>/dev/null

# Copy and customize
cp .env.example .env
# Edit with real keys from vault
```

**Key environment variables to look for:**
| Variable | Source | Notes |
|----------|--------|-------|
| `OPENAI_API_KEY` | Hermes profile `.env` | Or use Google/Groq as OpenAI-compatible |
| `ELEVENLABS_API_KEY` | Hermes profile `.env` | For transcription/TTS |
| `AWS_*` / `REMOTION_AWS_*` | See MinIO setup below | Use MinIO for local dev |
| `PORT` | Set manually | Avoid conflicts with other services |

**Pitfall:** Don't put all keys in one `.env` file if the project has per-app env files (monorepo pattern). Each app reads its own `.env`.

### Phase 4: S3 Storage (MinIO)

Most media/video projects require S3 for file uploads. **Don't use AWS for dev — use MinIO.**

```bash
# Start MinIO
docker run -d \
  --name minio \
  --restart unless-stopped \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin123 \
  -v /root/minio/data:/data \
  minio/minio server /data --console-address ":9001"

# Install mc client
curl -sL https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc
chmod +x /usr/local/bin/mc

# Configure and create bucket
mc alias set local http://localhost:9000 minioadmin minioadmin123
mc mb local/{project-name}
mc anonymous set download local/{project-name}
```

**Environment variables for MinIO:**
```bash
AWS_ENDPOINT=http://localhost:9000
AWS_FORCE_PATH_STYLE=true
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin123
AWS_BUCKET_NAME={project-name}
```

### Phase 5: Patch for Local Dev

Most OSS projects assume AWS. You'll need to patch the S3 client to support MinIO.

**Pattern (proven with Framedeck):**
1. Find the S3 client initialization (usually `new S3Client({...})`)
2. Add endpoint override:
```typescript
const s3Config: any = { region, credentials, ... };
const customEndpoint = configService.get('AWS_ENDPOINT');
if (customEndpoint) {
  s3Config.endpoint = customEndpoint;
  s3Config.forcePathStyle = true;
}
this.s3Client = new S3Client(s3Config);
```
3. Also patch any hardcoded S3 URL construction (e.g., `getEndpoint()`) to use the custom endpoint.

**Why `forcePathStyle: true`:** MinIO uses path-style URLs (`localhost:9000/bucket/key`) not virtual-hosted (`bucket.localhost:9000/key`).

### Phase 6: Start Services

**For monorepos with multiple services:**

```bash
# Option 1: Start everything (if dev script supports it)
PORTLESS=0 pnpm dev:direct  # PORTLESS=0 skips localhost URL injection

# Option 2: Start individually (more control)
PORTLESS=0 pnpm --filter server dev &
PORTLESS=0 pnpm --filter frontend dev &
cargo run --release --manifest-path apps/media-processor/Cargo.toml &
```

**Port assignment strategy:**
| Service | Port | Check |
|---------|------|-------|
| Frontend | 3000 | `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000` |
| Backend API | 4000 | `curl http://localhost:4000/hello` |
| Media Processor | 4005 | `curl http://localhost:4005/health` |
| MinIO API | 9000 | `mc ls local/` |
| MinIO Console | 9001 | Browser: `http://localhost:9001` |

**Pitfall:** `pnpm dev` scripts often use `portless` which requires sudo for HTTPS proxy. Set `PORTLESS=0` to skip this on VPS.

**Pitfall:** First Rust build takes 2-5 minutes. Use `cargo build --release` in background, then `cargo run --release` after build completes.

### Phase 6b: Docker Compose Deployment

For projects with a `docker-compose.yml`, use Docker instead of running from source:

```bash
cd /root/{project}
# Create .env from example or manually
cp .env.example .env 2>/dev/null || nano .env

# Pull and start
docker compose pull
docker compose up -d

# Verify
docker ps --filter name={container}
curl -s -o /dev/null -w "%{http_code}" http://localhost:{port}/api/health
docker logs {container} --tail 20
```

**Port assignment pattern:**
| Service | Port | Notes |
|---------|------|-------|
| RSSHub | 1200 | Content monitoring |
| CloakBrowser | 8080 | Browser automation |
| Framedeck | 3000 | Video editor (when active) |
| TREK | 3002 | Travel planner |
| Hermes Dashboard | 3071 | Agent dashboard |

**Pitfall:** Check existing ports BEFORE assigning: `ss -tlnp | grep -E "3000|3002|4000"`. Don't rely on project defaults — they often conflict.

**Pitfall:** `docker compose up -d` in foreground mode triggers the long-lived process guard. Use `terminal(background=true, notify_on_complete=true)` for the pull/start, then verify in a separate call.

**Pitfall — Host port conflicts (nginx on 80/443):** If nginx or another service already occupies ports 80 and/or 443, `docker compose up -d` fails with:
```
Error response from daemon: failed to bind host port 0.0.0.0:80/tcp: address already in use
```
**Fix:** Identify the conflicting service with `ss -tlnp | grep ':80 '`, then either:
- Stop conflicting service temporarily: `systemctl stop nginx` or `docker stop <container>`
- Use alternate ports: Change the compose project's ports in `.env`:
  ```
  HTTP_PORT=8080
  HTTPS_PORT=8443
  docker compose down && docker compose up -d
  ```
- Avoid HTTPS_PORT entirely for local dev — set `SITE_ADDRESS=http://localhost:8080` (with `http://` prefix to disable Caddy auto-TLS). Without the prefix, Caddy auto-redirects to HTTPS on port 443 even when listening on a different port.

**Pitfall — Caddy auto-TLS without domain:** When using Caddy as reverse proxy, `SITE_ADDRESS=:8080` causes Caddy to attempt auto-HTTPS and redirect to port 443. Fix: use `SITE_ADDRESS=http://localhost:8080` (`http://` prefix disables TLS for local dev), or ensure the Caddy container's port maps to the correct internal port.

**Pitfall:** Read-only containers (`read_only: true`) need `tmpfs` for temp files. Check the compose file and add `tmpfs: /tmp:noexec,nosuid,size=64m` if the container fails to start.

### Phase 6d: Docker Compose — Buzz Relay Deployment

Buzz (Block's open-source agent workspace, 15.3K⭐) uses a Rust relay + Postgres + Redis stack. Deployment revealed several non-obvious pitfalls:

**1. Env var name mismatch — `DATABASE_URL` vs `BUZZ_DATABASE_URL`**

The Buzz relay binary reads `DATABASE_URL` (not `BUZZ_DATABASE_URL`). The `.env.example` and documentation may use `BUZZ_DATABASE_URL`, but the Rust config code reads the unprefixed name:

```rust
// crates/buzz-relay/src/config.rs
let database_url = std::env::var("DATABASE_URL")
    .unwrap_or_else(|_| "postgres://buzz:buzz_dev@localhost:5432/buzz".to_string());
```

**Fix:** Use `DATABASE_URL` in docker-compose environment, not `BUZZ_DATABASE_URL`. The relay will silently retry and timeout on the wrong env var, producing `error: database error: pool timed out while waiting for an open connection` with no indication of the real cause.

**2. Migrations require a separate command**

The relay binary does NOT auto-migrate on startup. You must run migrations explicitly before starting the relay:

```bash
docker run --rm --network buzz_buzz-net \
  -e DATABASE_URL="postgres://buzz:buzz_dev@postgres:5432/buzz?sslmode=disable" \
  --entrypoint buzz-admin ghcr.io/block/buzz:latest migrate
```

The `buzz-admin` binary is bundled in the same image. Check available commands with `--help`:
- `buzz-admin migrate` — Run pending database migrations
- `buzz-admin generate-key` — Generate a new Nostr keypair
- `buzz-admin add-member` — Add a pubkey to relay membership

**3. iptables DOCKER chain blocks inter-container traffic**

The VPS had a default DROP policy on the DOCKER chain that blocked the buzz relay from reaching Postgres even when both were on the same Docker network. The relay container had no IP on the network (it was created but iptables dropped the traffic before the connection could establish).

**Diagnose:**
```bash
# Check if containers can reach each other
docker run --rm --network buzz_buzz-net alpine:3.19 sh -c "ping -c1 -W2 postgres 2>&1 | head -3"

# Check iptables DOCKER chain
iptables -L DOCKER
```

**Fix:** Add ACCEPT rules for the buzz network subnet:
```bash
iptables -I DOCKER 1 -s 172.16.4.0/24 -j ACCEPT
iptables -I DOCKER 1 -d 172.16.4.0/24 -j ACCEPT
```

The subnet may vary — check with `docker network inspect buzz_buzz-net`.

**4. Dev keypair warning on first start**

The relay starts with a hardcoded dev keypair by default. This is expected for development:
```
WARN: Using hardcoded dev relay keypair (BUZZ_REQUIRE_AUTH_TOKEN=false).
Set BUZZ_RELAY_PRIVATE_KEY for production.
```

**5. Buzz compose file structure**

Minimal working docker-compose.yml for Buzz:
```yaml
name: buzz

services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: buzz
      POSTGRES_PASSWORD: buzz_dev
      POSTGRES_DB: buzz
    volumes:
      - buzz-postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U buzz"]
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
    restart: unless-stopped

  relay:
    image: ghcr.io/block/buzz:latest
    ports:
      - '127.0.0.1:3003:3000'
    environment:
      DATABASE_URL: postgres://buzz:buzz_dev@postgres:5432/buzz
      REDIS_URL: redis://redis:6379
      RUST_LOG: info
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

volumes:
  buzz-postgres:

networks:
  buzz-net:
    driver: bridge
```

**6. S3/MinIO dependency — relay crashes without it**

The Buzz relay binary runs a **git conformance probe** on startup that requires an S3-compatible object store at `http://localhost:9000`. If no S3 service is available, the probe fails and the relay exits with:

```
Error: git conformance probe failed: s3 backend error: reqwest: error sending request for url (http://localhost:9000/buzz-media/packs/...)
```

The relay's compose file does NOT include a MinIO service by default. Postgres and Redis will be healthy, but the relay will loop in `Restarting (1)` forever.

**Fix — Add MinIO to the compose stack:**

```yaml
services:
  # ... postgres, redis, relay as above ...
  
  minio:
    image: minio/minio:latest
    container_name: buzz-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin123
    volumes:
      - buzz-minio:/data
    ports:
      - '127.0.0.1:9000:9000'
      - '127.0.0.1:9001:9001'
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  buzz-minio:
```

Then add `minio` to the relay's `depends_on` and set S3 env vars on the relay:

```yaml
services:
  relay:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_started
    environment:
      # ... existing vars ...
      AWS_ENDPOINT: http://minio:9000
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin123
      AWS_REGION: us-east-1
      AWS_FORCE_PATH_STYLE: "true"
```

**7. Hermes native gateway integration**

As of July 29, 2026, Hermes integrates with Buzz natively via three methods:
1. Run locally inside Buzz Desktop
2. Join through an ACP relay bridge as a hosted agent
3. Add Buzz as a native Hermes gateway (recommended)

The native gateway preserves all Hermes capabilities (memory, skills, cron jobs, sessions) while adding channels, DMs, mentions, threaded replies, reactions, and images.

### Phase 6c: VPS Stack Audit

When cleaning up the VPS, follow this audit pattern:

1. **Survey running services:** `docker ps -a`, `systemctl list-units --type=service --state=running`
2. **Check each service:** Is it actively used? Does it have API keys? Is it consuming resources?
3. **Kill decision:** No active use + no API keys + consuming resources = KILL
4. **Kill sequence:**
   ```bash
   docker stop {container} && docker rm {container}
   docker rmi {image}
   docker volume rm {volume}
   systemctl stop {service} && systemctl disable {service}
   rm -rf /root/{data-dir}
   ```
5. **Clean /tmp:** `du -sh /tmp/* | sort -rh | head -10` then remove old tarballs, debug dirs
6. **Vault hygiene:** Remove nested `.git` dirs, stale browser data, demo videos
7. **Verify:** `df -h /` for disk, `free -h` for RAM, `docker ps` for containers

**Proven cleanup targets:** Framedeck (unused), MinIO (only if nothing uses it), Ollama (small models not worth the RAM), old `/tmp` cruft (Sui debug files, tarballs).

### Vite Dev Server Behind nginx — Allowed Hosts Gate

When proxying a Vite dev server through nginx (e.g., proxy_pass to port 5188), Vite blocks requests with unlisted host headers — returns HTTP 403 even when the server is up and nginx is working.

**Fix:** Set `allowedHosts` via env var:
```
VIEWER_ALLOWED_HOSTS=cad.gentechlabs.net npx vite dev --host 127.0.0.1
```
Multiple hosts: comma-separated. This is read from `process.env.VIEWER_ALLOWED_HOSTS` in the cad-viewer vite config. If the config hardcodes an empty array, patch `vite.config.*` instead.

**Diagnose:** Local curl to 127.0.0.1 works, but curl with `-H "Host: domain.com"` returns 403. That's Vite's gate, not nginx.

### npx Interactive Prompt in Background / tmux

`npx` prompts "Ok to proceed?" on first run — stalls forever in tmux/nohup (no TTY). Fix: use `npx --yes` to auto-accept. Only needed on first ever run per package version; cached runs skip the prompt.

### Phase 7: Public Access Setup (Tunneling)

**Problem:** Services running on VPS are only accessible via `localhost`. For external access (webhooks, mobile apps, smart glasses), you need HTTPS.

### Cloudflare DNS — A Records vs CNAMEs

When putting a service behind a custom domain (like `rugcheck.your-site.com`), you need a DNS record. Two options:

| Record | What It Does | Example |
|--------|-------------|---------|
| **A record** | Points a name directly to an IP address | `rugcheck` → `2.24.195.196` |
| **CNAME** | Points a name to another domain name | `rugcheck` → `your-site.com` |

**The Rule:**
- **A record** → your server's IP. Use for anything running on a VPS.
- **CNAME** → a Cloudflare Worker URL. Use for Workers.

**The Loop That Broke Our APIs:**
We had `rugcheck.gentechlabs.net` as a CNAME pointing to `gentechlabs.net`. The problem? `gentechlabs.net` itself is proxied through Cloudflare (orange cloud). So Cloudflare asked itself "where is gentechlabs.net?" and got back its own IP. It tried to connect to itself → **522 error**. The API was down for days.

**The Fix:**
Delete the CNAME, add an A record pointing to your server's real IP:

| Step | Action |
|------|--------|
| 1 | Delete the CNAME record |
| 2 | Add an A record: Name = subdomain, IPv4 = your server IP |
| 3 | Toggle the orange cloud (proxy) ON |
| 4 | Save |

**Quick Test:**
```bash
curl -s -o /dev/null -w "%{http_code}" https://rugcheck.your-site.com/v1/health
# Should return 200, not 522
```

**When to Use Each:**
```
A record  → VPS-hosted APIs (rugcheck, prices, gas, security)
CNAME    → Cloudflare Workers (api → your-worker.workers.dev)
CNAME    → DO NOT point to a proxied root domain (causes loop)
```

**Cloudflare Tunnel (first attempt):**
```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
dpkg -i cloudflared.deb

# Start tunnel (HTTPS)
cloudflared tunnel --url http://localhost:3000 > /tmp/cloudflared.log 2>&1 &
```

**Pitfall:** Cloudflare tunnels may return 404 errors even when local service responds. Pattern observed: `curl http://localhost:3000` → 200 OK, `curl https://tunnel-url` → 404. Root cause can be:
1. **Server listening on localhost-only vs 0.0.0.0:** Express apps default to `localhost`. Check with `netstat -tlnp | grep PORT`. If you see `tcp6 :::PORT`, the server is listening on IPv6 localhost only. Tunnel services (especially Cloudflare) need `0.0.0.0` binding.
2. **Port conflicts:** Another service occupying the target port. Use `fuser -k PORT/tcp` or `lsof -ti:PORT | xargs kill -9`.
3. **SPA routing mismatch:** Single-page apps with client-side routing may need server-side catch-all or proper base path.

**Diagnose tunnel vs server issues:**
```bash
# Verify server is actually running
ps aux | grep "node server" | grep -v grep
netstat -tlnp | grep 3001

# Test locally - if this works but tunnel fails, issue is tunnel routing
curl http://localhost:3001/api/pois | jq '.[0].name'
curl http://localhost:3001/ | head -10

# Test tunnel directly
curl -v https://tunnel-url/ 2>&1 | grep -E "(HTTP/|Content-Type)"

# Check if server needs 0.0.0.0 binding (read server.js listen() call)
grep "app.listen" /root/project/server.js
```

**Fix server binding if needed:**
```bash
# Patch server.js to listen on 0.0.0.0
sed -i 's/app\.listen(PORT,/app.listen(PORT, '"'"'0.0.0.0'"'"',/' server.js

# Restart server
pkill -f "node server"
PORT=3001 node server.js > /tmp/server.log 2>&1 &
```

**Localtunnel (fallback for simple HTTPS):**
```bash
# Install localtunnel
npm install -g localtunnel

# Start tunnel on specific port
lt --port 3001 > /tmp/localtunnel.log 2>&1 &
```

**Pitfall:** Localtunnel URLs timeout frequently (~10-15 min). Single command returns, but tunnel dies. Need watchdog for persistent access.

**Localtunnel Watchdog Pattern (proven for HUD deployment):**

The watchdog script is captured in `scripts/localtunnel-watchdog.sh`. Key commands:

```bash
# Start watchdog
chmod +x /root/localtunnel-watchdog.sh
terminal(background=true, notify_on_complete=true)  # Start watchdog

# Get current URL
cat /tmp/localtunnel-current.log

# Monitor watchdog
tail -f /tmp/watchdog-main.log
```

**Pitfall:** Localtunnel service issues ("Bad Gateway" errors) are transient. If URLs start returning 502/503, wait 1-2 minutes or restart the watchdog. These are service-side, not your deployment. Diagnose by checking local service works (`curl localhost:3001` → 200) while tunnel fails.

**Pitfall:** Localtunnel is not reliable for critical production access (e.g., smart glasses for travel). Expect occasional "Bad Gateway" errors. For production, use ngrok (requires signup), Cloudflare Tunnel (requires account), or proper domain with SSL (most reliable).

### Phase 8: Verify

```bash
# Check all ports
ss -tlnp | grep -E "3000|3001|4000|4005|9000|9001"

# Test local API endpoints
curl http://localhost:4000/hello  # Backend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000  # Frontend
curl http://localhost:4005/health  # Media processor

# Test tunnel accessibility
TUNNEL_URL=$(grep "your url is:" /tmp/localtunnel-current.log | tail -1 | awk '{print $4}')
curl -s -o /dev/null -w "%{http_code}" $TUNNEL_URL/api/pois  # API test
curl -s $TUNNEL_URL/ | head -5  # HTML load test

# Test upload flow (if S3-enabled)
FILE_SIZE=$(stat -c%s test-file.mp4)
curl -X POST http://localhost:4000/uploads/init \
  -H "Content-Type: application/json" \
  -d "{\"filename\":\"test.mp4\",\"contentType\":\"video/mp4\",\"fileSize\":$FILE_SIZE}"
```

---

## VPS Migration from GitHub Pages

When migrating a static site from GitHub Pages to a self-hosted VPS, the common failure mode is Cloudflare caching (or a Worker intercepting traffic), not nginx config.

### Migration Steps

1. **Copy files to VPS web root:**
   ```bash
   mkdir -p /var/www/portfolio/data
   cp -r /root/repos/owner/repo/* /var/www/portfolio/
   ```

2. **Add nginx server block:**
   Add to `/etc/nginx/sites-enabled/`:
   ```nginx
   server {
       listen 80;
       server_name subdomain.your-site.net;
       root /var/www/portfolio;
       index index.html;
       try_files $uri $uri/ =404;
   }
   ```
   Test and reload: `sudo nginx -t && sudo systemctl reload nginx`

3. **Update cron jobs** that previously pushed to GitHub Pages to instead copy to VPS. Change from `git push` to local `cp`. No GitHub API calls needed.

4. **Cloudflare:** After updating files, purge cache (Dashboard → Caching → Purge Everything) or set DNS to grey cloud for testing.

### Cloudflare Worker Interception Trap

**Most common reason file changes don't show up:** A Cloudflare Worker is intercepting root traffic and serving its own page, completely bypassing the VPS.

**Diagnose:**
```bash
# Compare what Cloudflare serves vs what VPS serves
curl -s https://your-site.net/ | wc -c
curl -s -H "Host: your-site.net" http://localhost/ | wc -c
# Different sizes = Worker intercepting
```

**Fix:** Cloudflare Dashboard → Workers & Pages → remove the root domain route (e.g., `your-site.net/*`). Keep only API-specific routes. The purge only clears cached origin responses — it doesn't affect Worker-served content.

## Related References

- `references/vps-migration-pattern.md` — Complete workflow for moving static sites from GitHub Pages to VPS
- `references/hermes-dashboard-setup.md` — Hermes dashboard systemd deployment, auth stubs, theme config
- `references/datahub-self-host-deployment.md` — DataHub 14-container stack: stale-tag bypass, port remapping off 8080/8081, schema-registry DNS race, and the token-signing-key fix
- `references/datahub-graphql-agent-build.md` — DataHub GraphQL agent-build pattern: working schema (searchResults/relationships fields), blast-radius lineage walker, severity verdict, and the read→reason→act→contribute-back shape for "Use of DataHub" hackathon tracks

## Pitfalls

1. **Port conflicts** — Check `ss -tlnp` before starting. Old processes may hold ports.
2. **Missing cargo-watch** — Rust dev mode needs it: `cargo install cargo-watch`
3. **Build scripts ignored** — pnpm may skip native module builds. Use `pnpm rebuild` or `pnpm approve-builds`.
4. **Hardcoded AWS URLs** — Most projects construct S3 URLs as `https://{bucket}.s3.{region}.amazonaws.com`. Patch these to use MinIO endpoint.
5. **Presigned URL mismatch** — If upload init works but actual upload fails, check that presigned URLs point to MinIO, not AWS. The `getEndpoint()` method needs the same patch as the S3 client.
6. **env var naming** — Projects use different names (`AWS_ENDPOINT` vs `S3_ENDPOINT` vs `MINIO_ENDPOINT`). Check the source code to find the right one.
7. **Background processes** — Use `terminal(background=true)` for long-running services. Don't use shell `&` — it doesn't track the process.
8. **Test tunnel URLs before sharing** — Never provide tunnel URLs to the user without testing them first. User feedback: "what is showing me that the URL you sent me is just showing me a black screen?" Always verify: `curl -s https://tunnel-url/` and confirm it returns actual content (not 404/Bad Gateway) before sharing URL.
9. **Init container failures on restart** — After `docker compose up -d`, some containers may exit with code 1 while others run fine. This is often a one-shot init container (`restart: "no"`) that already ran on a previous boot. Check `docker logs <init-container>` — if the error says "already exists" or "already configured", the failure is benign (the setup work was already done). The entrypoint script's grep fallback may not match the exact error message; fix by extending the grep pattern in `docker-compose.yaml`. Verify dependent services are healthy before investigating further.

---

## Related Skills

- `deploy-and-verify` — GitHub Pages deployment verification
- `docker-management` — Docker lifecycle and debugging
- `tool-evaluation-integration` — Evaluating whether to self-host in the first place
