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
