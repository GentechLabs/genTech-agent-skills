# CVG → CEB (Cincinnati → Mactan-Cebu) — Route Reality

Researched Aug 27, 2026 for Jordan's possible Halloween trip. Reusable for any US→Cebu flight research.

## Route facts
- **No major flies CVG→CEB nonstop.** All route through hubs (ORD/IAH/SFO for United; ATL/DTW/LAX for Delta; YVR/YYZ for Air Canada).
- **October is the cheapest month** to fly US→Cebu (off-season). One-ways from CVG start ~$480–556.
- **The cheap one-ways are largely Alaska Airlines** (~$480, e.g. Oct 22). Alaska is a major that partners with United/Delta/American — status + miles transfer, and booking direct avoids OTA risk.

## One-way price snapshot (CVG→CEB, October)
| Source | One-Way From | Notes |
|--------|-------------|-------|
| Travelocity / Orbitz | $480 | Alaska, e.g. Oct 22 |
| Expedia | $490–515 | OTA — use for discovery only |
| Skyscanner | $532 | |
| CheapOair | $556 | |
| Farecompare | ~$802 avg | October = cheapest month |

## Direct-with-major reality (Jordan's preference)
- **United:** CEB round-trip from ~$1,017; CVG→MNL one-way ~$1,169. Routes via ORD/IAH/SFO. More expensive on this route.
- **Delta:** LAX→CEB one-way ~$441 on Delta metal; from CVG add a domestic leg (ATL/DTW) → higher.
- **Air Canada:** CVG→CEB via YVR/YYZ; cheap CVG fares (CAD 371) are regional, NOT to CEB.
- **Alaska:** ~$480 one-way — the sweet spot for "major + benefits + direct booking."

**Tradeoff:** United/Delta/Air Canada direct on this route typically cost $700–1,100 one-way because CEB isn't a primary hub for them. Alaska direct at ~$480 is the recommended play.

## Airlines on route
Alaska, American, United, Cathay Pacific, Philippine Airlines, Korean Air, EVA, STARLUX, China Airlines, Emirates, Japan Airlines.

## Tooling notes
- LetsFG CLI present but needs registration (`letsfg register` → error code 1000, API unreachable). Not usable without a working registration.
- Airline deep-link search URLs (united.com/flights-search?..., delta.com/flights-search/results?...) 404 or redirect; their search widgets fight automation. Use web_search snippets for airline fares + give the user the direct booking link.
