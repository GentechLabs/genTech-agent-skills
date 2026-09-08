# VPS Remote Gateway Implementation

**Created**: July 1, 2026  
**Purpose**: Enable Gentech VPS to access home desktop compute resources for cost optimization

---

## Problem Statement

**User Context (July 1, 2026):**
- GLM subscription usage: 73-75% filled for the week
- Home desktop has Ollama Cloud subscription available
- Need to offload build queue to desktop when GLM quota is high
- Goal: Single agent (Gentech VPS) with distributed compute, not multiple agents

---

## Remote Gateway Options

### Option A: Hermes Relay Connector (Official)

**Command:**
```bash
hermes gateway enroll \
  --token YOUR_ENROLLMENT_TOKEN \
  --connector-url wss://your-connector.com/relay \
  --wake-url https://your-wake-url.com
```

**Requirements:**
- Enrollment token from relay connector
- Connector URL (WebSocket relay server)
- Wake URL (for idle gateway wake-up)

**Benefits:**
- Official Hermes feature
- Secure WebSocket relay
- Built-in authentication
- Automatic reconnection

**Drawbacks:**
- Requires relay connector infrastructure
- Additional dependency on connector service

**Use When:** You have or want to set up a relay connector infrastructure

---

### Option B: Cloudflare Tunnel + FastAPI (Recommended)

**Architecture:**
```
Gentech VPS ──► Cloudflare Tunnel ──► Home Desktop FastAPI
       │                 │                 │
       │              HTTPS               │
       │              Tunnel              │
       └───────────────────────────────────┘
                    Secure Tunnel
```

**VPS Setup (Gentech):**
```bash
# 1. Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# 2. Authenticate
cloudflared tunnel login

# 3. Create tunnel
cloudflared tunnel create gentech-vps-gateway

# 4. Configure tunnel
cat > ~/.cloudflared/config.yml << EOF
tunnel: <tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: gentech-gateway.your-domain.com
    service: http://localhost:8080
  - service: http_status:404
EOF

# 5. Run tunnel
cloudflared tunnel run gentech-vps-gateway
```

**Desktop Setup (Forge):**
```python
# api/gateway.py - FastAPI Task Gateway
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Gentech Compute Gateway")

class TaskRequest(BaseModel):
    task_id: str
    task_type: str  # "build", "analysis", "code"
    payload: dict
    priority: str  # "high", "normal", "low"

class TaskResult(BaseModel):
    task_id: str
    status: str  # "pending", "running", "completed", "failed"
    result: dict | None = None
    error: str | None = None

# In-memory queue (persist to DB in production)
task_queue: dict[str, TaskResult] = {}

@app.post("/task/offload")
async def offload_task(task: TaskRequest):
    """VPS sends task to desktop for execution"""
    if task.task_id in task_queue:
        raise HTTPException(status_code=400, detail="Task already exists")
    
    task_queue[task.task_id] = TaskResult(
        task_id=task.task_id,
        status="pending",
        result=None,
        error=None
    )
    
    # Trigger task execution in background
    execute_task(task)
    
    return {"status": "queued", "task_id": task.task_id}

@app.get("/task/status/{task_id}")
async def get_task_status(task_id: str):
    """VPS checks task progress"""
    if task_id not in task_queue:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_queue[task_id]

@app.post("/task/result/{task_id}")
async def submit_task_result(task_id: str, result: TaskResult):
    """Desktop submits task completion"""
    if task_id not in task_queue:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_queue[task_id] = result
    return {"status": "updated"}

def execute_task(task: TaskRequest):
    """Execute task using Ollama Cloud or desktop resources"""
    # Implementation depends on task_type
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

**VPS Usage:**
```python
import requests

GATEWAY_URL = "https://gentech-gateway.your-domain.com"

# Offload heavy task
task = {
    "task_id": "build-001",
    "task_type": "build",
    "payload": {"repo": "gentech-vault", "branch": "main"},
    "priority": "high"
}
response = requests.post(f"{GATEWAY_URL}/task/offload", json=task)

# Check status
status = requests.get(f"{GATEWAY_URL}/task/status/build-001").json()
print(status)  # {"task_id": "build-001", "status": "running", ...}
```

**Benefits:**
- Secure HTTPS tunnel (no open ports)
- Fast to set up (cloudflared handles networking)
- No relay infrastructure needed
- Industry-standard approach

**Drawbacks:**
- Requires Cloudflare account
- Tunnel must be running on desktop
- Polling overhead for status checks

**Use When:** Quick setup, no relay infrastructure, secure by default

---

### Option C: Direct SSH Tunnel (Simplest)

**Setup:**
```bash
# On VPS, establish reverse SSH tunnel to desktop
# Replace user@desktop-ip with actual credentials
ssh -R 8080:localhost:8080 -N -f user@desktop-ip

# Verify tunnel is running
ps aux | grep ssh
```

**Desktop FastAPI:**
Same as Option B, listens on `localhost:8080`

**VPS Usage:**
```python
# Access desktop via tunnel
GATEWAY_URL = "http://localhost:8080"  # Tunnel forwards to desktop:8080
```

**Benefits:**
- Zero external dependencies
- Works immediately if SSH access exists
- No cloudflare account needed

**Drawbacks:**
- Requires SSH access from VPS to desktop
- Desktop must be reachable from VPS (firewall, port forwarding)
- Less secure than HTTPS tunnel
- Tunnel can break and needs restart

**Use When:** SSH access already exists, quick prototype, trusted network

---

## Model Routing Logic

### Cost Optimization Router

```python
import os

def get_optimal_model(task_complexity: str) -> tuple[str, str]:
    """
    Route tasks to optimal model based on cost and complexity.
    
    Returns: (provider, model)
    """
    # Check GLM quota (need actual API call to provider)
    glm_quota_used = check_glm_quota()  # Returns percentage 0-100
    
    # High quota → use Ollama Cloud on desktop
    if glm_quota_used > 70 and desktop_available():
        if task_complexity == "simple":
            return ("ollama", "llama3.1:8b")
        elif task_complexity == "complex":
            return ("ollama", "llama3.1:70b")
    
    # Normal quota → use GLM based on complexity
    if task_complexity == "simple":
        return ("zai", "glm-4.7")
    elif task_complexity == "complex":
        return ("zai", "glm-5.2")
    
    # Fallback
    return ("zai", "glm-4.7")

def desktop_available() -> bool:
    """Check if desktop gateway is responsive"""
    try:
        response = requests.get(f"{GATEWAY_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_glm_quota() -> int:
    """Check current GLM token usage percentage"""
    # Implementation depends on provider API
    # Placeholder: return mock value
    return 75  # 75% used

def offload_to_desktop(task: dict):
    """Offload task to desktop for execution"""
    response = requests.post(f"{GATEWAY_URL}/task/offload", json=task)
    return response.json()
```

---

## Build Queue Integration

### Modified Build Queue Runner

```python
# scripts/run_build_queue.py with gateway integration

def execute_build(build_item: dict):
    """Execute build task with optimal routing"""
    task_type = classify_task(build_item)
    
    # Heavy builds → offload to desktop
    if task_type in ["complex_build", "analysis", "audit"]:
        if desktop_available():
            task = {
                "task_id": build_item["id"],
                "task_type": task_type,
                "payload": build_item,
                "priority": "normal"
            }
            result = offload_to_desktop(task)
            return result
    
    # Simple builds → execute on VPS
    return execute_local_build(build_item)

def classify_task(build_item: dict) -> str:
    """Classify build task by complexity"""
    description = build_item.get("description", "").lower()
    
    if "simple" in description or "quick" in description:
        return "simple_build"
    elif "complex" in description or "audit" in description:
        return "complex_build"
    elif "analysis" in description or "review" in description:
        return "analysis"
    else:
        return "normal_build"
```

---

## Implementation Checklist

### Phase 1: Gateway Setup
- [ ] Choose gateway option (Hermes Relay, Cloudflare, SSH)
- [ ] Configure VPS tunnel/gateway
- [ ] Install FastAPI on desktop (`pip install fastapi uvicorn`)
- [ ] Implement `/task/offload` endpoint
- [ ] Implement `/task/status/{id}` endpoint
- [ ] Test VPS → Desktop connectivity

### Phase 2: Model Routing
- [ ] Implement GLM quota checking
- [ ] Add desktop availability check
- [ ] Implement cost optimization router
- [ ] Update build queue runner with routing logic
- [ ] Test routing decisions (quota high vs low)

### Phase 3: Monitoring
- [ ] Add task execution logging
- [ ] Track cost savings (GLM vs Ollama)
- [ ] Monitor gateway uptime
- [ ] Alert on gateway failures
- [ ] Weekly cost report

---

## Troubleshooting

### Gateway Connection Issues

**Symptom:** `Connection refused` to gateway URL

**Diagnosis:**
```bash
# On VPS: Check tunnel status
ps aux | grep cloudflared  # Or SSH tunnel

# On Desktop: Check FastAPI is running
curl http://localhost:8080/health

# On VPS: Test tunnel connection
curl https://gentech-gateway.your-domain.com/health
```

**Fix:**
- Restart tunnel on VPS
- Restart FastAPI on desktop
- Check firewall rules (VPS → desktop)

### Task Not Executing

**Symptom:** Task status stuck at "pending"

**Diagnosis:**
```python
# Check task queue
response = requests.get(f"{GATEWAY_URL}/task/status/{task_id}")
print(response.json())  # Should show "running" or "completed"

# Check desktop logs
# tail -f /path/to/fastapi.log
```

**Fix:**
- Verify task execution logic in FastAPI
- Check Ollama Cloud availability on desktop
- Review error logs on desktop

### Desktop Unavailable

**Symptom:** `desktop_available()` returns False

**Diagnosis:**
```bash
# On VPS: Ping desktop (if SSH tunnel)
ping desktop-ip

# On Desktop: Check network
ip addr show
# Verify desktop is online
```

**Fix:**
- Wake desktop (Wake-on-LAN if configured)
- Verify network connectivity
- Restart gateway service

---

## Cost Savings Projection

**Assumptions:**
- GLM-5.2 cost: $0.01 per 1K tokens
- Ollama Cloud cost: $0 (included in subscription)
- Weekly GLM quota: 1M tokens
- Tasks offloaded: 40% (complex builds, analysis)

**Projected Monthly Savings:**
| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| GLM tokens | 4M | 2.4M | 1.6M tokens |
| GLM cost | $40 | $24 | $16/month |
| Ollama usage | 0 | 1.6M | $0 (sub) |
| **Total** | **$40** | **$24** | **$16/month (40%)** |

---

## Related Files

- `agent-economy` skill — x402 API infrastructure
- `gentech-ops` skill — operational workflows
- `model-routing` skill — model selection patterns
- Cloudflare tunnel config: `06-Content/Projects/rayban-gentech/detect-tunnel.sh`

---

**Next Steps:**
1. Choose gateway option (Recommend: Cloudflare Tunnel)
2. Set up desktop FastAPI server
3. Implement model routing logic
4. Update build queue runner
5. Test with sample tasks
6. Monitor cost savings