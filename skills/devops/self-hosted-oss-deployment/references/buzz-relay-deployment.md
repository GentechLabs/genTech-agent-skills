# Buzz Relay Deployment — July 29, 2026

**Repo:** github.com/block/buzz (15.3K⭐, Apache 2.0, Rust)
**Image:** ghcr.io/block/buzz:latest
**VPS:** 2.24.195.196, port 3003 (internal)

## Status
- ✅ Docker Compose running (Postgres 17 + Redis 7 + relay)
- ✅ Migrations applied
- ✅ Relay started, listening on port 3003
- ⚠️ Needs nginx config + SSL cert for `buzz.gentechlabs.net`
- ⚠️ Needs Hermes native gateway integration

## Key Commands

```bash
# Start stack
cd /opt/buzz && docker compose up -d

# Run migrations (required before first start)
docker compose run --rm \
  -e DATABASE_URL="postgres://buzz:buzz_dev@postgres:5432/buzz?sslmode=disable" \
  --entrypoint buzz-admin relay migrate

# Check logs
docker logs buzz-relay --tail 20

# Generate keypair for production
docker run --rm --entrypoint buzz-admin ghcr.io/block/buzz:latest generate-key
```

## Critical Pitfalls (discovered during deployment)

1. **Env var name:** The binary reads `DATABASE_URL`, not `BUZZ_DATABASE_URL`. Using the wrong name produces a silent timeout with no error message indicating the real cause.
2. **Migrations are NOT automatic:** Must run `buzz-admin migrate` explicitly before starting the relay.
3. **iptables DOCKER chain:** Default DROP policy blocks inter-container traffic. Add ACCEPT rules for the buzz subnet.
4. **Dev keypair:** First start uses a hardcoded dev keypair. Set `BUZZ_RELAY_PRIVATE_KEY` for production.

## Hermes Integration

As of July 29, 2026, Hermes integrates with Buzz natively via three methods:
1. Run locally inside Buzz Desktop
2. Join through an ACP relay bridge as a hosted agent
3. Add Buzz as a native Hermes gateway (recommended — preserves memory, skills, cron jobs, sessions)
