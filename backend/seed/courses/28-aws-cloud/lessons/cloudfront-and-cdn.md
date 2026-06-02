# CloudFront and Content Delivery

**Amazon CloudFront** is AWS's global CDN (Content Delivery Network). It sits in front of your origin — S3, ALB, API Gateway, or any HTTP server — and serves content from edge locations closest to your users. This cuts latency, reduces origin load, and enables HTTPS everywhere.

## How CloudFront works

```
User (Paris)
   │
   ▼
CloudFront edge (Paris POP)   ← cache hit: serves immediately
   │ cache miss
   ▼
Origin (S3 bucket / ALB in us-east-1)
```

CloudFront has 400+ **Points of Presence (PoPs)** globally. A cache miss still travels AWS's internal backbone, which is faster than the public internet.

## Creating a Distribution

```bash
aws cloudfront create-distribution \
  --distribution-config '{
    "Origins": {
      "Quantity": 1,
      "Items": [{
        "Id": "s3-origin",
        "DomainName": "my-bucket.s3.amazonaws.com",
        "S3OriginConfig": { "OriginAccessIdentity": "" }
      }]
    },
    "DefaultCacheBehavior": {
      "ViewerProtocolPolicy": "redirect-to-https",
      "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
      "TargetOriginId": "s3-origin",
      "Compress": true,
      "AllowedMethods": { "Quantity": 2, "Items": ["GET","HEAD"] }
    },
    "Enabled": true,
    "DefaultRootObject": "index.html"
  }'
```

For S3 origins, use an **Origin Access Control (OAC)** instead of public bucket access. The bucket policy allows only CloudFront to read it.

## Cache behaviors

A **cache behavior** matches URL path patterns to cache settings:

| Path pattern     | TTL    | Origin         | Use case                    |
|------------------|--------|----------------|-----------------------------|
| `/static/*`      | 1 year | S3             | Immutable hashed assets     |
| `/api/*`         | 0 s    | ALB            | Dynamic API, no caching     |
| `/*.html`        | 5 min  | S3             | HTML pages, short TTL       |
| `*` (default)    | 1 day  | S3             | Everything else             |

## Invalidations

After a deployment, force CloudFront to drop cached files:

```bash
aws cloudfront create-invalidation \
  --distribution-id EXXXXXXXXXXXXX \
  --paths "/index.html" "/static/app.*.js"
```

Tip: instead of invalidating, use **content-hashed filenames** for JS/CSS (`app.a1b2c3.js`). The hash changes on each build, so the new file is automatically fetched without invalidation.

## HTTPS and certificates

1. Request a public certificate in **ACM** (AWS Certificate Manager) — free.
2. Must be in `us-east-1` (CloudFront requires ACM certificates in that region regardless of your origin region).
3. Attach to your CloudFront distribution under "Custom SSL Certificate".
4. Set `ViewerProtocolPolicy: redirect-to-https`.

## Lambda@Edge and CloudFront Functions

Run logic at the edge without a round-trip to the origin:

- **CloudFront Functions** — lightweight JS, sub-ms, runs at every PoP. Good for URL rewrites, header manipulation, simple auth.
- **Lambda@Edge** — full Lambda (Node or Python), runs at regional edge caches. Good for A/B testing, auth token validation, personalization.

```javascript
// CloudFront Function: redirect /old-path to /new-path
function handler(event) {
  var request = event.request;
  if (request.uri === '/old-path') {
    return {
      statusCode: 301,
      headers: { location: { value: '/new-path' } }
    };
  }
  return request;
}
```

## Security features

- **AWS WAF** integration — block bad bots, SQL injection, rate-limit by IP.
- **Geo restriction** — block or allow specific countries.
- **Signed URLs / Signed Cookies** — restrict access to private content (video streaming, paid downloads).
- **Origin Shield** — extra caching layer in front of your origin to reduce origin hits.

## CloudFront vs S3 website vs ALB

| Scenario                           | Best choice                        |
|------------------------------------|------------------------------------|
| Static site with HTTPS             | CloudFront + S3                    |
| Global API acceleration            | CloudFront + ALB/API Gateway       |
| Region-local internal API          | ALB alone                          |
| Image / video streaming            | CloudFront + S3 + signed URLs      |
| No CDN needed (single-region test) | S3 website or ALB directly         |
