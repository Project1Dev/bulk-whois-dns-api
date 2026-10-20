#!/usr/bin/env bash
# Bulk WHOIS / DNS lookup via the Apify API. Usage: APIFY_TOKEN=... ./curl.sh [input.json]
set -euo pipefail
if [ -z "${APIFY_TOKEN:-}" ]; then
  echo "Error: APIFY_TOKEN is not set. Get a free token at https://console.apify.com/account/integrations" >&2
  exit 1
fi
INPUT="${1:-$(dirname "$0")/input.json}"
curl -sS -X POST \
  "https://api.apify.com/v2/acts/pennydata~bulk-domain-whois-dns-lookup/run-sync-get-dataset-items?token=${APIFY_TOKEN}" \
  -H 'Content-Type: application/json' \
  --data @"$INPUT"
