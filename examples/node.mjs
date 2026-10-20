// npm install apify-client
// APIFY_TOKEN=... node node.mjs example.com python.org ...
const token = process.env.APIFY_TOKEN;
if (!token) {
  console.error('Error: APIFY_TOKEN is not set. Get a free token at https://console.apify.com/account/integrations');
  process.exit(1);
}

const { ApifyClient } = await import('apify-client');

const domains = process.argv.slice(2);
if (domains.length === 0) domains.push('example.com', 'python.org');

const client = new ApifyClient({ token });
const run = await client.actor('pennydata/bulk-domain-whois-dns-lookup').call({ domains });
const { items } = await client.dataset(run.defaultDatasetId).listItems();
for (const item of items) {
  console.log(item.error ? `FAILED ${item.domain}: ${item.error}` : `${item.domain}\tavailable=${item.available}\texpires=${item.expires}\tregistrar=${item.registrar}`);
}
