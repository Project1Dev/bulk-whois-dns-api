# Bulk WHOIS Lookup API & Bulk DNS Lookup (Domain Expiry Checker)

A **bulk WHOIS lookup API** and **bulk DNS lookup** for lists of domains: availability, registrar, creation and **expiry dates**, domain age, status flags, nameservers, and A / MX / TXT records. Up to 1,000 domains per run. It uses RDAP (the official successor to WHOIS) plus DNS, so there is no scraping, no proxy and no captcha. Errors and unknown results are not billed.

It runs as the [`pennydata/bulk-domain-whois-dns-lookup`](https://apify.com/pennydata/bulk-domain-whois-dns-lookup) Actor on Apify, so you call it over plain HTTP, with the Node or Python Apify client, or from the Apify Console with no code.

**Actor page:** https://apify.com/pennydata/bulk-domain-whois-dns-lookup

## Good for

- **Domain expiry checker**: sweep a portfolio and sort by `expires`
- **Domain availability check** for naming lists
- Domain age and registrar lookups for lead lists and due diligence
- Nameserver / MX / TXT audits across many domains

## Pricing

Pay per event (Apify pay-per-event, Free plan price as read from the actor page on 2026-10-20):

| Event | Price |
| --- | --- |
| One domain successfully looked up | $0.002 ($2 per 1,000 domains) |

Failed, blocked or unknown results are not charged. Paid Apify plans may get lower per-event prices. The [actor page](https://apify.com/pennydata/bulk-domain-whois-dns-lookup) is the source of truth. An Apify account is free and includes monthly free platform credit.

## Quick start

Get an API token at https://console.apify.com/account/integrations and export it:

```bash
export APIFY_TOKEN=your_token_here
```

### curl

```bash
curl -X POST "https://api.apify.com/v2/acts/pennydata~bulk-domain-whois-dns-lookup/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"domains":["example.com","python.org"]}'
```

### Node.js (apify-client)

```bash
npm install apify-client
APIFY_TOKEN=... node examples/node.mjs example.com python.org
```

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor('pennydata/bulk-domain-whois-dns-lookup').call({
  domains: ['example.com', 'python.org'],
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items);
```

### Python

```bash
pip install requests
APIFY_TOKEN=... python examples/python_example.py example.com python.org
```

```python
import os, requests

resp = requests.post(
    "https://api.apify.com/v2/acts/pennydata~bulk-domain-whois-dns-lookup/run-sync-get-dataset-items",
    params={"token": os.environ["APIFY_TOKEN"]},
    json={"domains": ["example.com", "python.org"]},
    timeout=300,
)
print(resp.json())
```

Without `APIFY_TOKEN` the example scripts exit immediately with a clear error and make no request.

## Output

One row per domain (abridged):

```json
{
  "domain": "python.org",
  "available": false,
  "registrar": "Gandi SAS",
  "created": "1995-03-27T05:00:00.545Z",
  "expires": "2033-03-28T05:00:00Z",
  "ageDays": 11525,
  "nameservers": ["ns-1134.awsdns-13.org"],
  "mx": ["50 mail.python.org"],
  "source": "rdap"
}
```

Other fields: `status`, `a`, `txt`, `checkedAt`, and `note` / `error` when relevant.

## Input reference

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `domains` | string[] | `["example.com","apify.com"]` | Domains or URLs (reduced to the host). Max 1,000 per run, duplicates removed |
| `maxConcurrency` | integer | `20` | Domains looked up in parallel (1-50); at most 5 requests in flight per RDAP server |

A ready-to-use input file: [`examples/input.json`](examples/input.json).

## Limits (honest notes)

- `available: true` means the registry answered "not found". It is not a purchase guarantee: reserved or premium names can be unobtainable.
- Some country-code TLDs have no RDAP service (e.g. `.de`, `.io` at the time of writing). These return `source: "dns-only"` with DNS records but no registrar or dates; a domain with no DNS records shows `available: null` (unknown, not charged).
- Registries may rate limit; persistent failures come back as `error` rows (not charged). Re-run them later.
- Registrant/contact personal data is never read or stored.

## More actors from the same account

- [Website Screenshot & URL to PDF](https://apify.com/pennydata/shot-pdf)
- [Bulk Email Validator (No SMTP)](https://apify.com/pennydata/bulk-email-validator-no-smtp)
- [App Store Reviews Scraper](https://apify.com/pennydata/appstore-reviews-rss)
- [Website Tech Stack Detector](https://apify.com/pennydata/website-tech-stack-detector)

## AI-built disclosure

This repository and the underlying Actor were built and are maintained by an AI-assisted workflow (Claude), operated by the owner of the `jjlarsensa` GitHub account and the `pennydata` Apify account. The example scripts were checked only for the no-token error path; run them yourself before depending on them.

## License

MIT, see [LICENSE](LICENSE). The README, examples and landing page are MIT; the Actor itself is a hosted service on Apify.
