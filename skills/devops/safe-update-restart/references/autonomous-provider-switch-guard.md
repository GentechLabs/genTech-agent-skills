# Autonomous provider-switch guard

Scripts that switch the fleet's LLM provider automatically — whether hourly watchdogs,
rate-limit responders, or reset-driven fallbacks — encode a **doctrine**: which provider is
primary, which is fallback, and when to flip. When that doctrine changes, the script either
keeps up or becomes a hazard.

## The hazard class

A typical auto-switch has two branches:

1. **Switch out:** when the primary is exhausted, move to the fallback.
2. **Switch back:** when the primary resets (usage drops, subscription refills), move back to it.

The switch-back branch is the dangerous one. If the primary is **cancelled** rather than
merely capped, the usage reading will drop to zero / 401 / error — exactly the signal the
script interprets as "primary is healthy again." It then writes the cancelled provider into
every seat's config, autonomously, on schedule, with no error. A migration that took minutes
to apply is reverted in one cron tick.

The same class applies to usage monitors and token reports that hardcode
`PRIMARY = "old-provider"`: after the migration they mislabel, mis-attribute, or report
silently wrong health while exiting cleanly.

## Fail-closed guard pattern

Instead of hardcoding the primary, read it from the live config at runtime, and refuse to
act if the doctrine no longer matches.

### Python recipe

```python
import os, re, sys

PROFILES = "/root/.hermes/profiles"

def live_primary(seat: str = "gentech"):
    """Return the provider a seat's config currently names as primary."""
    try:
        with open(os.path.join(PROFILES, seat, "config.yaml")) as f:
            text = f.read()
        m = re.search(r"^model:\n((?:[ \t]+.*\n)+)", text, re.M)
        if m:
            p = re.search(r"^\s+provider:\s*(\S+)\s*$", m.group(1), re.M)
            if p:
                return p.group(1)
    except Exception:
        pass
    return None


def rail_order_still_holds(expected_primary: str, seat: str = "gentech"):
    """Refuse to act if the fleet's rail order has moved since this script was written."""
    got = live_primary(seat)
    if got is None:
        return False, "could not read the live primary from config — not flipping blind"
    if got != expected_primary:
        return False, (f"live primary is {got!r} but this script expects {expected_primary!r} — "
                       f"the rail order has moved; refusing to act")
    return True, ""


def main():
    holds, why = rail_order_still_holds(expected_primary="ollama-cloud")
    if not holds:
        # Never email/DM/alert on this — the whole point is to stay silent and safe.
        if "--quiet" not in sys.argv:
            print(f"⛔ {why}")
        return 0
    # ... rest of switch logic ...
```

**Why `return 0`:** the script is *behaving correctly* by refusing. A non-zero exit would
create cron noise and might trigger a "fix the failing cron" response that re-enables the
old behavior.

### Guard the whole chain, not just the primary

Some scripts switch among three or more providers. In that case, check whether the retired
provider is still present anywhere in the active chain (`model.provider` +
`fallback_providers`):

```python
def provider_still_in_chain(provider: str, seat: str = "gentech"):
    """Is `provider` still named anywhere in the active routing chain?"""
    try:
        with open(os.path.join(PROFILES, seat, "config.yaml")) as f:
            text = f.read()
    except Exception:
        return None
    chain = []
    m = re.search(r"^model:\n((?:[ \t]+.*\n)+)", text, re.M)
    if m:
        p = re.search(r"^\s+provider:\s*(\S+)\s*$", m.group(1), re.M)
        chain.append(p.group(1) if p else "")
    fm = re.search(r"^fallback_providers:\n((?:[ \t-]+.*\n)+)", text, re.M)
    if fm:
        chain += re.findall(r"provider:\s*(\S+)", fm.group(1))
    return provider in chain
```

If the retired provider is no longer in the chain, the script's premise is dead; refuse.

## What to change, what to leave

- **Hardcoded `PRIMARY` / `FALLBACK` constants** → replace with the guard, or read from config.
- **Usage probes that call a retired provider's API** → repoint to the live provider's usage
  endpoint, or remove the probe.
- **Monitors/reports that label outputs by hardcoded rail names** → resolve rail names from
  config so the report cannot go stale.
- **Paused-but-not-fixed watchdogs** → a paused cron job is still a loaded gun. Either delete
  it, or add the guard so re-enabling it is safe.

## Verification after patching

1. Run the script manually and confirm it refuses when the rail order has moved.
2. Check that `--quiet` and `--explain` modes also refuse (they should not bypass the guard).
3. Confirm the cron job is either removed or guarded; "paused" is not a fix.
4. Re-run the grep from Step 1.6 of `SKILL.md` and confirm no unguarded auto-switch remains.

## Case study: Ollama Cloud cancellation, 2026-09-30

Jordan cancelled the Ollama Cloud subscription at renewal and upgraded OpenCode Go to Go
Plus. The fleet migrated to `opencode-go` primary / `nous` fallback. Two hourly cron jobs
had encoded the old doctrine:

- `rail-switch.py`: `PRIMARY = "ollama-cloud"`. Switch-back at `weekly < 20%`.
- `provider-auto-switch.py`: Ollama-first, switch-back at `OLLAMA_LOW_WATER = 0.20`.

Both were paused minutes before the hour fired. They were then guarded:

- `rail-switch.py` checks `live_primary()` and refuses if it is not `ollama-cloud`.
- `provider-auto-switch.py` checks whether `ollama-cloud` is still in the active chain.

A usage report (`token-consumption-report.py`) and a quota sentinel
(`quota-sentinel.py`) were also repointed because they read from the dead rail and would
have reported healthy/mislabelled after the migration. A model-availability watchdog on
another seat was handed off for repointing rather than retirement.

**Lesson:** migration is not done when config is flipped. It is done when every script that
*acts on* the old provider has been found, guarded, repointed, or removed.
