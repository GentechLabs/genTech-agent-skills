# web3.career JSON-LD Job Extraction

Extract structured JobPosting data from web3.career via curl — no API keys, no payment, no browser.

## Background

web3.career is server-rendered. Despite being a "modern" site, it embeds full JSON-LD structured data for every job listing directly in the HTML. This means **curl works as a primary tool** — not a fallback.

Each JobPosting block contains:
- `title` — Job title
- `hiringOrganization.name` — Company name
- `datePosted` — ISO date (e.g., `2026-07-23 20:28:11 +0100`)
- `baseSalary.value.minValue` / `maxValue` — Salary range
- `jobLocationType` — `TELECOMMUTE` = remote eligible
- `applicantLocationRequirements.name` — `Anywhere` = worldwide
- `description` — Full job description (HTML-ish)
- `validThrough` — Expiry date
- `employmentType` — Full-time, Contract, etc.

## Full Extraction Script

```python
import re, json
from datetime import datetime, timezone

# Fetch the page
# curl -s -L -A "Mozilla/5.0" "https://web3.career/remote-jobs" > /tmp/web3-jobs.html

with open('/tmp/web3-jobs.html') as f:
    html = f.read()

pattern = r'<script type="application/ld\+json">(.*?)</script>'
today = datetime.now(timezone.utc)

jobs = []
for m in re.findall(pattern, html, re.DOTALL):
    try:
        data = json.loads(m.strip())
        if data.get('@type') != 'JobPosting':
            continue
        
        date = data.get('datePosted', '')
        days_ago = None
        if date:
            try:
                days_ago = (today - datetime.fromisoformat(date)).days
            except: pass
        
        salary = data.get('baseSalary', {})
        sal = salary.get('value', {})
        
        desc = data.get('description', '')
        clean_desc = re.sub(r'<[^>]+>', ' ', desc)
        clean_desc = re.sub(r'&amp;|&gt;|&lt;', ' ', clean_desc)
        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
        
        jobs.append({
            'title': data.get('title', ''),
            'company': data.get('hiringOrganization', {}).get('name', ''),
            'date_posted': date,
            'days_ago': days_ago,
            'salary_min': sal.get('minValue'),
            'salary_max': sal.get('maxValue'),
            'remote': data.get('jobLocationType', ''),
            'applicant_region': data.get('applicantLocationRequirements', {}).get('name', ''),
            'desc': clean_desc,
            'valid_through': data.get('validThrough', ''),
        })
    except json.JSONDecodeError:
        pass

# Sort by recency
jobs.sort(key=lambda j: j['days_ago'] if j['days_ago'] is not None else 999)

# Print table
print(f"{'TITLE':<55} {'COMPANY':<25} {'DAYS':<5} {'SALARY':<25}")
print('='*110)
for j in jobs:
    sal = f"${j['salary_min']}-${j['salary_max']}" if j['salary_min'] else 'N/A'
    days = str(j['days_ago']) if j['days_ago'] is not None else '?'
    print(f"{j['title'][:53]:<55} {j['company'][:23]:<25} {days:<5} {sal[:23]:<25}")
```

## Tag-Filtered URLs

Use the same extraction on these tag-filtered pages:

| URL | Focus |
|-----|-------|
| `https://web3.career/remote-jobs` | All remote jobs (default) |
| `https://web3.career/dev+entry-level-jobs` | Entry-level dev jobs |
| `https://web3.career/intern-jobs` | Internships |
| `https://web3.career/solidity+remote-jobs` | Solidity roles |
| `https://web3.career/defi+remote-jobs` | DeFi roles |
| `https://web3.career/python+remote-jobs` | Python roles |
| `https://web3.career/ai+remote-jobs` | AI roles |
| `https://web3.career/smart-contract+remote-jobs` | Smart contract roles |
| `https://web3.career/blockchain+remote-jobs` | General blockchain roles |

## Pitfalls

- The `description` field contains HTML entities (`&amp;`, `&gt;`, `&lt;`, `<p>`, `<br>`) — clean with regex before analysis.
- `datePosted` is in `+0100` format — `datetime.fromisoformat()` handles it in Python 3.11+.
- `salary_min`/`max` may be `None` for unlisted salaries.
- The page title says "15 New" but includes jobs beyond the "new" filter — always check `days_ago`.
- Some jobs say `jobLocationType: TELECOMMUTE` but the description mentions a physical office (NY, London, SF). Always cross-check the description text against location claims.
- `applicantLocationRequirements.name` may say "Anywhere" but the description restricts by region (e.g., "Europe / Asia"). Trust the description text over the structured field when they conflict.
