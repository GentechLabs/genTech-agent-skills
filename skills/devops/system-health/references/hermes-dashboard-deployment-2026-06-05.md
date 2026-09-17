# Hermes Web Dashboard — Deployment & Troubleshooting (Jun 5, 2026)

## The Problem

Hermes v0.15.2 `web_server.py` imports `hermes_cli.dashboard_auth` extensively (middleware, routes, audit, WebSocket tickets, prefix normalization) but **the module is not shipped in the pip package**. On a fresh install, `hermes dashboard` crashes immediately:

```
ModuleNotFoundError: No module named 'hermes_cli.dashboard_auth'
```

## The Fix

### 1. Create stub modules

Create directory and files at `${INSTALL_DIR}/venv/lib/python3.11/site-packages/hermes_cli/dashboard_auth/`:

**`__init__.py`** — Main stub with all required classes:
```python
"""Stub dashboard_auth module — auth disabled until proper module ships."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from fastapi import APIRouter

router = APIRouter()
_providers: List[Any] = []

def list_providers():
    return list(_providers)

class DashboardAuthProvider:
    name: str = ""
    display_name: str = ""

@dataclass
class LoginStart:
    redirect_url: str = ""
    cookie_payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Session:
    user_id: str = ""
    email: str = ""
    display_name: str = ""
    org_id: str = ""
    provider: str = ""
    expires_at: int = 0
    access_token: str = ""
    refresh_token: str = ""

class ProviderError(Exception):
    pass

class InvalidCodeError(Exception):
    pass

class RefreshExpiredError(Exception):
    pass
```

**`middleware.py`**:
```python
"""No-op auth middleware stub."""
async def gated_auth_middleware(request, call_next):
    return await call_next(request)
```

**`routes.py`**:
```python
"""Empty routes stub."""
from fastapi import APIRouter
router = APIRouter()
```

**`audit.py`**:
```python
"""Audit stub."""
from dataclasses import dataclass

@dataclass
class AuditEvent:
    event: str = ""
    details: dict = None

def audit_log(*args, **kwargs):
    pass
```

**`ws_tickets.py`**:
```python
"""WebSocket ticket stub."""
async def mint_ticket(*args, **kwargs):
    return "stub-ticket"
```

**`prefix.py`**:
```python
"""Prefix normalisation stub."""
def normalise_prefix(prefix: str) -> str:
    return prefix.rstrip("/") if prefix else ""
```

### 2. Start with `--insecure` flag

The dashboard refuses non-loopback binds without a registered OAuth provider. Since we run on Tailscale (trusted network), use `--insecure`:

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open --insecure
```

### 3. Create systemd service for persistence

```bash
cat > /etc/systemd/system/hermes-dashboard.service << 'EOF'
[Unit]
Description=Hermes Web Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=${INSTALL_DIR}/venv/bin/hermes dashboard --host 0.0.0.0 --port 9119 --no-open --insecure
Restart=always
RestartSec=5
Environment=HOME=/root
Environment=PATH=${INSTALL_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable hermes-dashboard
systemctl start hermes-dashboard
```

### 4. Verify

```bash
systemctl status hermes-dashboard --no-pager
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119/
# Should return 200
```

## Key Details

- **Dashboard auth**: No auth when using `--insecure` — anyone on the Tailscale network can access. Acceptable for single-user VPS.
- **Stub verification**: `python3 -c "import hermes_cli.dashboard_auth; print('OK')"` should print `OK` after creating stubs.
- **systemd service**: Uses `Restart=always` + `RestartSec=5` for auto-recovery on crash.
- **Port**: 9119 (Hermes default). Access via Tailscale: `http://100.73.143.15:9119`

## Theme Activation

**⚠️ CRITICAL PATH RESOLUTION:** `get_hermes_home()` returns the *profile* directory (`~/.hermes/profiles/gentech/`), NOT `~/.hermes/`. Theme files MUST go in:

```
~/.hermes/profiles/gentech/dashboard-themes/*.yaml
```

NOT `~/.hermes/dashboard-themes/`. Placing themes in the wrong directory is the #1 reason themes don't appear in the picker.

After creating a theme YAML, **activate** it in `config.yaml`:

```yaml
dashboard:
  theme: gentech-aae  # must match the `name:` field in the theme YAML
```

**Config path:** `~/.hermes/profiles/gentech/config.yaml` (line ~308)

**Important:** The dashboard must be **restarted** after changing the theme in config.yaml — theme changes do not take effect live.

```bash
systemctl restart hermes-dashboard
```

**Pitfall:** The dashboard theme picker (palette icon) only shows themes that are in the *profile-scoped* `dashboard-themes/` dir AND set in `config.yaml`. If a theme file exists but the config says `default`, the custom theme won't activate. Also: the API at `/api/dashboard/themes` shows the active theme name — if it shows "ember" or "default" after you set "gentech-aae", someone clicked the theme picker (it overrides config.yaml via API PUT).

**Theme file validation:** The normalizer accepts both `{hex, alpha}` objects and bare hex strings for palette values. Midground can be `"#ff8c00"` (string) or `{hex: "#ff8c00", alpha: 1.0}` (object) — both work.

## Pitfalls

- **Don't use shell `&`** for the dashboard — use `terminal(background=true)` or systemd. Shell backgrounding doesn't track the process.
- **Kill existing processes before systemd start** — if a background `hermes dashboard` is running, the systemd service will fail to bind the port.
- **The Nous Portal OAuth plugin** (`plugins/dashboard_auth/nous/`) exists but requires `HERMES_DASHBOARD_OAUTH_CLIENT_ID` env var — only relevant for Fly.io hosted deployments, not our self-hosted VPS.
- **Theme changes require restart** — `config.yaml` `dashboard.theme` is read at startup only. Switching themes via API persists to config but won't apply until the dashboard process restarts.

## Future

When Hermes ships the `dashboard_auth` module properly (likely v0.16+), delete the stubs. The real module will provide OAuth, session management, and audit logging. The `--insecure` flag can then be replaced with proper auth configuration.
