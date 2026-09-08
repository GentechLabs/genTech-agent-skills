# Career Scanner Validation Rules

**Source:** Jordan's feedback, June 20, 2026

## Mandatory Checks (Every Scan)

### 1. Verify Job Is Active
- Check posting date — skip anything older than 30 days without recent activity
- Look for "closed", "expired", "no longer accepting" indicators
- If the link 404s → SKIP, don't report
- Test the apply link — if it's broken, the job is likely dead

### 2. Verify "Remote" Means Remote
- Asia-based companies saying "remote" often mean "remote within Asia"
- Red flags: company HQ in China/Taiwan/Singapore, Asian time zones mentioned, "overlap with Asia hours required"
- **Binance specifically:** All "remote" roles require Asia location — SKIP unless explicitly confirmed worldwide
- When in doubt, check the company's other listings for location patterns

### 3. Site Maintenance Awareness
- web3.career goes down for maintenance periodically — check before relying on it
- If a site is down, note it in the report and skip gracefully
- Don't fail the whole scan because one source is unavailable

### 4. No Duplicate Reporting
- Check session history before reporting a job
- If it was found in a prior scan, skip it
- Track reported jobs in vault to prevent re-reporting across weekly scans

## Jordan's Positioning
- **Level:** Entry-level (0-3 years), NOT mid or senior
- **Strengths:** Python, Solidity, AI agent architecture, DeFi, smart contracts
- **Weaknesses:** Full-stack React/Postgres, TypeScript production experience
- **Best fit roles:** AI Agent Engineer, LLM Engineer, DeFi Engineer, Blockchain Dev (Python/Solidity)
- **Avoid roles:** Full-stack heavy, Java/C++, 5+ yrs required, senior-level, Asia-based
