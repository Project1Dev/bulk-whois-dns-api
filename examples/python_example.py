# pip install requests
# APIFY_TOKEN=... python python_example.py example.com python.org ...
import os
import sys

import requests

token = os.environ.get("APIFY_TOKEN")
if not token:
    sys.exit("Error: APIFY_TOKEN is not set. Get a free token at https://console.apify.com/account/integrations")

domains = sys.argv[1:] or ["example.com", "python.org"]

resp = requests.post(
    "https://api.apify.com/v2/acts/pennydata~bulk-domain-whois-dns-lookup/run-sync-get-dataset-items",
    params={"token": token},
    json={"domains": domains},
    timeout=300,
)
resp.raise_for_status()
for item in resp.json():
    print(item["domain"], "available=%s" % item.get("available"), "expires=%s" % item.get("expires"), item.get("error") or "")
