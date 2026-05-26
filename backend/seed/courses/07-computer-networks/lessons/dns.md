# DNS: The Internet's Phone Book

The **Domain Name System (DNS)** translates human-friendly names like `www.example.com` into the IP addresses (like `93.184.216.34`) that routers need to deliver packets. Without DNS, every hyperlink would require users to memorize raw IP addresses that change whenever servers are migrated.

DNS is one of the most critical Internet protocols. A misconfigured or slow resolver causes mysterious failures that look like network outages. Understanding DNS in depth helps you diagnose slow page loads, configure domains correctly, and reason about security implications.

## The Problem DNS Solves

IP addresses identify hosts, but they are hard to remember and can change frequently — a company migrates its servers, a CDN rotates IPs for load balancing, or a service moves clouds. DNS provides a stable, human-readable namespace (the domain hierarchy) that can be updated independently of the underlying IP infrastructure.

The design goals of DNS (RFC 1034, 1987) are:
- **Scalability**: no single server can hold all records (trillions of lookups per day globally).
- **Availability**: the system must survive partial failures.
- **Consistency**: updates propagate within a bounded time window (TTL).

## DNS Hierarchy

DNS is a **distributed, hierarchical** database organized as an inverted tree:

```
                    . (root)
                  /    |    \
                com   org    net
               /   \
          example  google
          /    \       \
         www  mail      www
```

```
13 Root Name Server Clusters (a.root-servers.net … m.root-servers.net)
        │
   TLD (Top-Level Domain) Name Servers
   (.com, .org, .net, .uk, .edu, .io, …)
        │
   Authoritative Name Servers for each domain
   (ns1.example.com, ns2.example.com, …)
        │
   Resource Records: A, AAAA, MX, CNAME, TXT, NS, PTR, …
```

The **root servers** are not 13 physical machines — they are 13 *logical* root server addresses, each served by a anycast cluster of hundreds of physical machines worldwide.

## DNS Resolution: Recursive + Iterative Step-by-Step

When your browser asks for `www.example.com`:

```
Your Browser
    │
    ▼
OS Stub Resolver  ──check cache──► cache hit? → done (< 1 ms)
    │ cache miss
    ▼
Recursive Resolver (e.g., 8.8.8.8)  ──check its cache──► cache hit? → return
    │ cache miss — start iterative queries
    ├── Query root server: "Who handles .com?"
    │       Root returns NS records: a.gtld-servers.net, etc.
    ├── Query .com TLD server: "Who handles example.com?"
    │       TLD returns NS records: ns1.example.com, ns2.example.com
    └── Query ns1.example.com: "What is www.example.com?"
            Returns A record: 93.184.216.34  TTL=3600
    │
    ▼
Resolver caches result for TTL=3600 s
    │
    ▼
OS caches result, returns to browser
```

Key terms:
- **Recursive resolver** (also called a **full-service resolver** or **recursive nameserver**): performs the full lookup on behalf of the client. Your ISP or a public resolver like 8.8.8.8 (Google) or 1.1.1.1 (Cloudflare) plays this role.
- **Iterative query**: the resolver asks each server in the hierarchy in turn. Each server returns a *referral* (who to ask next) rather than the final answer.
- **Stub resolver**: the minimal DNS client built into your OS that only knows how to ask one recursive resolver.

**Timing:** A full uncached recursive lookup involves 3–6 round trips and typically takes 50–200 ms. A cached lookup returns in < 1 ms. This is why DNS caching matters so much for web performance.

## Common DNS Record Types

| Type  | Purpose                                         | Example Value                     |
|-------|-------------------------------------------------|-----------------------------------|
| A     | Maps hostname → IPv4 address                    | `93.184.216.34`                   |
| AAAA  | Maps hostname → IPv6 address                    | `2606:2800:220:1::93`             |
| CNAME | Alias — maps name → canonical name              | `www.example.com. → example.com.` |
| MX    | Mail exchanger — where to deliver email         | `10 mail.example.com.`            |
| NS    | Authoritative nameserver for a zone             | `ns1.example.com.`                |
| TXT   | Arbitrary text (SPF, DKIM, domain verification) | `"v=spf1 include:sendgrid.net ~all"` |
| PTR   | Reverse DNS: IP → hostname                      | `34.216.184.93.in-addr.arpa.`     |
| SOA   | Start of Authority: zone admin info + serial    | serial, refresh, retry, expire    |
| SRV   | Service location with priority + weight         | `_http._tcp 0 5 80 www.example.com.` |
| CAA   | Which CAs may issue certificates for this domain | `0 issue "letsencrypt.org"`       |

**CNAME chains:** `www.example.com → example.com → 93.184.216.34`. Only A/AAAA records return an IP; CNAME redirects to another name. You cannot have a CNAME at the zone apex (`example.com.` itself) — that would conflict with the SOA record. CDN providers use proprietary ANAME/ALIAS records to work around this.

## TTL (Time to Live)

Every DNS record carries a **TTL** in seconds that tells resolvers how long to cache it.

| TTL | Use case |
|-----|----------|
| 60 s | Active failover (accept high resolver load) |
| 300 s | Typical for dynamic services |
| 3600 s | Standard for stable services |
| 86400 s (1 day) | Rarely-changing records (MX, NS) |

Rule of thumb: **lower your TTL before** making a DNS change, wait for the old TTL to expire across the Internet, then make the change. Otherwise resolvers may cache the old answer for hours.

## DNS Wire Format

A DNS query/response is a compact binary message, typically < 512 bytes for UDP:

```
+─────────────────────────────────────+
|  Transaction ID (2 B)               |
|  Flags (2 B) — QR, Opcode, AA, TC,  |
|               RD, RA, RCODE         |
|  QDCOUNT (2 B)  ANCOUNT (2 B)       |
|  NSCOUNT (2 B)  ARCOUNT (2 B)       |
+─────────────────────────────────────+
|  Question section                   |
|  Answer section                     |
|  Authority section                  |
|  Additional section                 |
+─────────────────────────────────────+
```

- DNS uses **UDP port 53** for standard queries (small, single round-trip).
- Switches to **TCP port 53** if the response exceeds 512 bytes (the `TC` truncation bit is set), or for zone transfers (AXFR), or when the resolver signals EDNS0 buffer size.
- **DNS over HTTPS (DoH)** (RFC 8484) — DNS queries wrapped in HTTPS; hides queries from ISP-level observers.
- **DNS over TLS (DoT)** (RFC 7858) — DNS over a TLS-encrypted TCP connection on port 853.

## Security: DNS Cache Poisoning

DNS was designed in 1987 without authentication. An attacker who can inject a forged DNS response into a resolver's cache can redirect users to malicious servers for the full TTL — a **cache poisoning** attack (Kaminsky attack, 2008).

**DNSSEC** (DNS Security Extensions) mitigates this by adding cryptographic signatures to DNS records. Each zone has a key pair; records are signed with the zone's private key. Resolvers validate signatures using the public key published in DNSKEY records, chaining trust up to the root.

**DNSSEC limitations:** Only about 30% of domains are signed (as of 2024). Validation must also be performed by the resolver — if the resolver doesn't validate, clients get no benefit.

## Practical Commands

```bash
# Forward lookup — returns A records
dig www.example.com A
nslookup www.example.com

# Reverse lookup — PTR record
dig -x 93.184.216.34

# Check MX (mail server) records
dig example.com MX

# Check NS (nameserver) delegation
dig example.com NS

# Check TXT records (SPF, DKIM)
dig example.com TXT

# Query a specific resolver (bypass OS cache)
dig @1.1.1.1 www.example.com

# Trace the full iterative resolution path
dig +trace www.example.com

# Check DNSSEC validation
dig +dnssec www.example.com
```

DNS is often the first thing to check when a service is unreachable. Use `dig +short` for a quick IP lookup, and `dig +trace` to see exactly where the delegation chain breaks.
