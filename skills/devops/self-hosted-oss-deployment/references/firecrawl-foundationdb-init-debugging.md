# Firecrawl FoundationDB Init — Worked Debugging Example

**Date:** July 8, 2026
**Stack:** Firecrawl via Docker Compose at `/root/firecrawl/`

---

## Symptom

After `docker compose up -d`, one container shows `Exited (1)`:

```
firecrawl-foundationdb-init-1    Exited (1) 2 hours ago
```

All other containers (api, redis, rabbitmq, postgres, playwright, foundationdb) show `Up`.

## Diagnosis

**Step 1 — Check logs:**

```bash
docker logs firecrawl-foundationdb-init-1
```

Output:
```
Database created
ERROR: Database already exists! To change configuration, don't say `new'
```

**Step 2 — Check entrypoint in docker-compose.yaml:**

The init container runs a one-shot `fdbcli` command to create the FoundationDB database:

```yaml
foundationdb-init:
  image: foundationdb/foundationdb:7.3.63
  restart: "no"
  entrypoint:
    - /bin/bash
    - -c
    - >
      sleep 5 && out=$(fdbcli -C /var/fdb/fdb.cluster --exec 'configure new single ssd' 2>&1);
      status=$?; printf '%s\n' "$out";
      if [ "$status" -eq 0 ]; then exit 0; fi;
      printf '%s\n' "$out" | grep -Eiq 'already.*configured|database.*configured'
```

The logic:
1. Run `configure new single ssd` — creates FDB database
2. If exit code 0 → success, exit 0
3. If exit code ≠ 0 → grep output for "already configured" or "database configured"
4. If grep matches → exit 0 (benign re-run)
5. If grep fails → exit with original error code → container shows Exited (1)

**Step 3 — Identify the mismatch:**

On second boot, `fdbcli` outputs:
```
Database created
ERROR: Database already exists! To change configuration, don't say `new'
```

The grep pattern `already.*configured|database.*configured` does **not** match the actual output `"Database already exists!"` — there's no "configured" in the error message. So grep returns non-zero and the container exits with code 1.

## Fix

Append `|already.exists` to the grep pattern in `docker-compose.yaml` (line ~202):

```yaml
# Before (broken):
grep -Eiq 'already.*configured|database.*configured'

# After (fixed):
grep -Eiq 'already.*configured|database.*configured|already.exists'
```

Then re-run the init container:
```bash
docker compose -f /root/firecrawl/docker-compose.yaml up -d foundationdb-init
```

## Verification

```bash
docker logs firecrawl-foundationdb-init-1
# Should show no output (exit 0 on success)

docker inspect firecrawl-foundationdb-init-1 --format '{{.State.ExitCode}}'
# Should show 0
```

## Why This Is Benign

- The `NUQ_BACKEND` env var defaults to PostgreSQL (not FoundationDB)
- The FDB database was already created on first boot — the init container's work was done
- All dependent services (api, workers, etc.) use PostgreSQL + RabbitMQ for queue operations
- The FDB infrastructure is there for when someone switches to `NUQ_BACKEND=fdb`

## Key Takeaway

One-shot init containers (`restart: "no"`) that run setup commands will fail on subsequent `docker compose up -d` because their setup work is already done. If the entrypoint has a fallback grep, check that the grep pattern matches the actual error message. If not, extend the pattern. Always verify that dependent services are healthy before treating the failure as urgent.

---

## Container Status Reference

| Container | Status | Purpose | Init-Dependent? |
|-----------|--------|---------|-----------------|
| `firecrawl-foundationdb-init-1` | ❌ Exited (1) | One-shot FDB setup | No (ran once) |
| `firecrawl-foundationdb-1` | ✅ Up | FoundationDB server | No (PostgreSQL active) |
| `firecrawl-api-1` | ✅ Up | Main API + workers | No |
| `firecrawl-redis-1` | ✅ Up | Rate limiting + cache | No |
| `firecrawl-rabbitmq-1` | ✅ Up (healthy) | Job queue broker | No |
| `firecrawl-nuq-postgres-1` | ✅ Up | Queue backend | No |
| `firecrawl-playwright-service-1` | ✅ Up | JS rendering | No |

**API accessible at:** `http://localhost:3005` (root returns `{"message":"Firecrawl API"}`)
**Scrape endpoint:** `POST /v1/scrape` — verified working with `https://example.com`
