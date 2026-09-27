# DataHub Self-Host Deployment Recipe (Aug 3 2026)

DataHub (open-source metadata platform / context platform for AI agents) runs as a
14-container Docker Compose stack. Used for the "Build with DataHub Agent Hackathon"
(deadline Aug 10, $20.5K). This recipe captures the 4 non-obvious fixes that took a
bare `datahub docker quickstart` from failing to fully running.

## The core gotcha: the CLI pins stale image tags

`datahub docker quickstart` (from the `acryl-datahub` CLI) uses `quickstart_version_mapping.yaml`
which pins `composefile_git_ref: v1.5.0.6` and `docker_tag: v1.5.0.6` by DEFAULT. The
`acryldata/datahub-kafka-setup` image was DISCONTINUED after `v1.1.0.1` — so the pinned
`v1.5.0.6` tag does NOT exist on Docker Hub → pull fails:

```
Error response from daemon: failed to resolve reference "docker.io/acryldata/datahub-kafka-setup:v1.5.0.6": not found
```

**Fix:** bypass the CLI entirely; fetch the compose file and run `docker compose` directly
with the kafka-setup image pinned to a tag that exists.

```bash
# Fetch the compose at a known release
curl -s "https://raw.githubusercontent.com/datahub-project/datahub/v1.5.0.6/docker/quickstart/docker-compose.quickstart.yml" -o /tmp/dh-compose.yml
# Patch kafka-setup to the 'head' tag (exists on Docker Hub)
sed -i 's|image: ${DATAHUB_KAFKA_SETUP_IMAGE:-acryldata/datahub-kafka-setup}:${DATAHUB_VERSION:-head}|image: acryldata/datahub-kafka-setup:head|' /tmp/dh-compose.yml
```

Check tag existence before pinning: `curl -s -o /dev/null -w "%{http_code}" "https://hub.docker.com/v2/repositories/acryldata/<image>/tags/<tag>"` (200 = exists).

## Port conflicts (CRITICAL on this VPS)

The stack maps GMS on **8080** and schema-registry on **8081**. On this VPS:
- **8080** = the live x402 gateway (untouchable)
- **8081** = hummingbot-broker (EMQX) maps its internal 8081 → host 8099

**Fix — remap via env overrides** (the compose reads these):
```bash
export DATAHUB_MAPPED_GMS_PORT=28080
export DATAHUB_MAPPED_SCHEMA_REGISTRY_PORT=28081
```
The compose file uses `${DATAHUB_MAPPED_GMS_PORT:-8080}:8080` and
`${DATAHUB_MAPPED_SCHEMA_REGISTRY_PORT:-8081}:8081`, so these env vars work cleanly.

ALWAYS check ports before starting: `ss -tlnp | grep -E "8080|8081|28080|28081"`.

## schema-registry DNS race

`schema-registry` fails on first boot with "Couldn't resolve server broker:29092" — the
broker takes ~60s to become healthy and the registry probes too early. **Fix:** after the
broker is healthy, restart schema-registry:
```bash
docker start datahub-schema-registry-1
```
The registry has `SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS=broker:29092` and
`SCHEMA_REGISTRY_HOST_NAME=schemaregistry`.

## datahub-upgrade fails: token signing key

`datahub-upgrade` (the 36-step graph initializer) exits 1 with:
```
IllegalArgumentException: authentication.tokenService.signingKey must be set and not be empty
```
The docs say the env var is `AUTHENTICATION_TOKEN_SERVICE_SIGNINGKEY` but Spring's relaxed
binding maps `TOKEN_SERVICE` → `token-service` (hyphenated), NOT `tokenService` (camelCase),
so that var never binds. **The correct env vars are `DATAHUB_TOKEN_SERVICE_SIGNING_KEY` and
`DATAHUB_TOKEN_SERVICE_SALT`.**

**Fix:** export these and add them (plus `-Dauth.tokenService.signingKey`/`.salt` in
JAVA_OPTS) to the compose env for both `datahub-upgrade` and `datahub-gms` services:
```bash
export DATAHUB_TOKEN_SERVICE_SIGNING_KEY="gentech-signing-key-2026"
export DATAHUB_TOKEN_SERVICE_SALT="gentech-salt-2026"
```

## Working start command (the whole recipe)

```bash
cd /tmp
export DATAHUB_MAPPED_GMS_PORT=28080
export DATAHUB_MAPPED_SCHEMA_REGISTRY_PORT=28081
export DATAHUB_VERSION=v1.5.0.6
export DATAHUB_TOKEN_SERVICE_SIGNING_KEY="gentech-signing-key-2026"
export DATAHUB_TOKEN_SERVICE_SALT="gentech-salt-2026"
docker compose -f /tmp/dh-compose.yml --profile quickstart -p datahub up -d
```

Startup order that works: broker/mysql/zookeeper/elasticsearch/neo4j → schema-registry
(restart after broker healthy) → kafka-setup → datahub-upgrade (36 steps, SUCCEEDED) →
datahub-gms → frontend → actions.

## Verify it's up

```bash
docker ps -a | grep -i datahub          # expect healthy broker/mysql/zookeeper/elastic/neo4j/schema-registry + gms/frontend/actions
curl -s http://localhost:28080/health   # 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:9002   # frontend, 200
```

## Sample data + GraphQL notes

Load sample datapack: `datahub datapack load showcase-ecommerce` (1,049 entities).
Authenticate first: `export DATAHUB_GMS_URL=http://localhost:28080; datahub init --username datahub --password datahub --host http://localhost:28080`.

GraphQL quirks (verify via `__type` introspection if a query 404s):
- Search field is `searchResults`, NOT `results`:
  `{ search(input:{type:DATASET, query:"*", start:0, count:5}) { total searchResults { entity { urn } } } }`
- Lineage: `{ dataset(urn:"...") { lineage(input:{direction:DOWNSTREAM, start:0, count:5}) { total } } }`

## Disk footprint

The 14-container stack pulls ~8GB images. On a VPS at 80-89% disk, reclaim first:
- Remove crash-looping containers (`docker ps -a` shows `Restarting (N)`), orphaned images
  with 0 running containers (`docker images` + `docker ps -a --filter ancestor=<id>`),
  and unused image stacks (e.g. rsshub/browserless ~6GB). See `self-hosted-oss-deployment`
  Phase 6c for the audit pattern.
