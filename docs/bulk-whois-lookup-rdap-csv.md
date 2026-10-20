# Bulk WHOIS Lookup for a List of Domains: Expiry, Age and Registrar via RDAP (Script + CSV)

## WHOIS vs RDAP, and redaction

Classic WHOIS is a plain-text protocol on port 43 with no standard format, which is why bulk scripts built on it time out or mis-parse. Registries now also publish **RDAP**, the structured JSON successor over HTTPS. Since GDPR, registrant names and emails are mostly redacted in both, so expect registrar, dates, status and nameservers, not owner identity.

## One domain with curl

`rdap.org` is a public bootstrap that redirects to the right registry's RDAP server:

```bash
curl -sL https://rdap.org/domain/python.org | python3 -m json.tool | head -40
```

The `events` array holds `registration` and `expiration` dates; the entity with role `registrar` carries the registrar name in its vCard. An unregistered .com returns HTTP 404. rdap.org sits behind a bot filter: a request with aiohttp's default User-Agent got a 403 in my test, so send a descriptive User-Agent.

## Bulk script: asyncio, concurrency cap, backoff

Timeouts on big lists usually come from firing everything at once. This script caps concurrency at 5, retries timeouts, 429s and 5xx with exponential backoff, and writes CSV with age and days to expiry. Tested on 2026-10-20 with three domains (one long registered, one reserved, one unregistered).

```python
import asyncio, csv, sys
from datetime import datetime, timezone
import aiohttp

SEM = asyncio.Semaphore(5)  # stay polite: RDAP servers rate-limit

async def lookup(session, domain, tries=4):
    for i in range(tries):
        async with SEM:
            try:
                async with session.get(f"https://rdap.org/domain/{domain}", timeout=aiohttp.ClientTimeout(total=20)) as r:
                    if r.status == 404:
                        return {"domain": domain, "status": "not-registered"}
                    if r.status == 429 or r.status >= 500:
                        raise aiohttp.ClientError(r.status)
                    data = await r.json(content_type=None)
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
                await asyncio.sleep(2 ** i)
                continue
        ev = {e["eventAction"]: e["eventDate"] for e in data.get("events", [])}
        now = datetime.now(timezone.utc)
        parse = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
        created, expires = ev.get("registration"), ev.get("expiration")
        registrar = next((p[3] for e in data.get("entities", []) if "registrar" in e.get("roles", [])
                          for p in e.get("vcardArray", [None, []])[1] if p[0] == "fn"), "")
        return {"domain": domain, "status": "registered", "registrar": registrar,
                "created": created, "expires": expires,
                "age_days": (now - parse(created)).days if created else "",
                "days_to_expiry": (parse(expires) - now).days if expires else ""}
    return {"domain": domain, "status": "error"}

async def main(domains):
    async with aiohttp.ClientSession(headers={"User-Agent": "bulk-rdap-example/1.0 (script)", "Accept": "application/rdap+json"}) as s:
        rows = await asyncio.gather(*(lookup(s, d) for d in domains))
    w = csv.DictWriter(sys.stdout, ["domain", "status", "registrar", "created", "expires", "age_days", "days_to_expiry"])
    w.writeheader(); w.writerows(rows)

asyncio.run(main(sys.argv[1:] or ["python.org", "example.com", "some-name-nobody-registered-12345.com"]))
```

Run: `pip install aiohttp`, then `python rdap.py python.org example.com`, or pass your own list (for 20,000 domains, read a file and chunk it). Tested output for the defaults: `python.org,registered,Gandi SAS,1995-03-27...`, `example.com,registered,...`, and `not-registered` for the unregistered name. Expiry alerts: run it daily from cron and filter rows with `days_to_expiry < 30`. RDAP servers rate-limit, so keep concurrency low and honour 429 responses.

## Hosted option for large lists

Disclosure: I built an Apify actor for this, [pennydata/bulk-domain-whois-dns-lookup](https://apify.com/pennydata/bulk-domain-whois-dns-lookup). It queries official RDAP and adds DNS records (MX, TXT, nameservers), up to 1,000 domains per run. Pay-per-event: $0.002 per domain looked up (read live from the actor API on 2026-10-20; check the actor page for the current price); errors and unknown results are not charged.

```python
import os, sys, requests

token = os.getenv("APIFY_TOKEN")
if not token:
    sys.exit("Error: APIFY_TOKEN is not set. Get a token at https://console.apify.com/account/integrations")

resp = requests.post(
    "https://api.apify.com/v2/acts/pennydata~bulk-domain-whois-dns-lookup/run-sync-get-dataset-items",
    params={"token": token},
    json={"domains": ["example.com", "python.org", "some-name-nobody-registered-12345.com"]},
    timeout=300,
)
if not resp.ok:
    sys.exit(f"Error: Apify API returned {resp.status_code}: {resp.text[:300]}")
for r in resp.json():
    print(r.get("domain"), "available=%s" % r.get("available"), "expires=%s" % r.get("expires"), r.get("error") or "")
```

Needs `APIFY_TOKEN`; exits with an error message if it is not set.

[Hosted option: pennydata/bulk-domain-whois-dns-lookup on Apify](https://apify.com/pennydata/bulk-domain-whois-dns-lookup)

---
Written with AI (Claude). The author also built the linked Apify actor. Code examples were run on 2026-10-20; prices are read from the live actor API and may change.
