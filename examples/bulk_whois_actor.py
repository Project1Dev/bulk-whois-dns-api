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
