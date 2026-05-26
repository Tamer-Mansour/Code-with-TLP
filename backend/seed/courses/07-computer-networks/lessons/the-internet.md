# The Internet

The **Internet** is the largest computer network ever built — a global mesh of millions of interconnected networks operated by ISPs, universities, corporations, and governments. Understanding its structure and the path a packet takes when you load a webpage helps you reason about performance, reliability, and security in every system you build.

## How the Internet is Structured

### Autonomous Systems

The Internet is not owned by a single entity. Instead it is divided into roughly 75,000+ **Autonomous Systems (ASes)** — independently operated networks that agree to exchange traffic. Each AS has a globally unique **ASN** (Autonomous System Number), assigned by IANA and distributed to regional registries (ARIN, RIPE, APNIC, etc.).

```
Tier-1 ISP  (global backbone — AT&T AS7018, NTT AS2914, Level3 AS3356)
        |
  Tier-2 ISP  (regional — buys transit from Tier-1, peers with others)
        |
  Tier-3 ISP / Access Network  (residential / business customers)
        |
    Home Router (NAT, DHCP)
        |
    Your Laptop
```

- **Tier-1 ISPs** form the backbone of the Internet. They peer with each other for free (*settlement-free peering*) because traffic flows are roughly equal. They do not pay anyone for transit — they are at the top of the hierarchy.
- **Tier-2 ISPs** peer with many networks but also pay some Tier-1 ISPs for transit to reach the full Internet.
- **Tier-3 ISPs** (your home ISP) are pure transit customers — they pay a Tier-2 or Tier-1 for all traffic.

### Internet Exchange Points (IXPs)

IXPs are physical locations where many ASes connect their routers directly to exchange traffic, bypassing expensive transit providers. They consist of a shared switching fabric (Layer-2 Ethernet fabric) that any member can plug into.

Major IXPs include:
- **DE-CIX Frankfurt** – world's largest by peak traffic (~14+ Tbps).
- **AMS-IX Amsterdam** – a founding IXP.
- **LINX London**, **NYIIX New York**, **JPNAP Tokyo**.

A university AS joining DE-CIX can exchange traffic with hundreds of content providers (Google, Facebook, Akamai) with a single connection, dramatically reducing latency and cost.

## The Edge vs. The Core

- **Network edge** – end systems (hosts): laptops, phones, servers, IoT devices. They *generate* and *consume* data. They run application-layer software (browsers, email clients, streaming players).
- **Network core** – routers and high-speed fiber links owned by ISPs. They *forward* packets at wire speed, typically looking only at the IP destination address.

This edge-core split embodies the **end-to-end principle**: complex intelligence lives at the hosts; the core stays simple and fast. TCP congestion control runs on endpoints, not routers.

## Key Internet Services and Ports

| Service | Protocol | Standard Port | Notes |
|---------|----------|--------------|-------|
| HTTP | TCP | 80 | Unencrypted web |
| HTTPS | TCP | 443 | HTTP over TLS |
| DNS | UDP (TCP for large) | 53 | Name resolution |
| SMTP (relay) | TCP | 25 | Server-to-server email |
| SMTP (submit) | TCP | 587 | Client-to-server with auth |
| IMAP | TCP | 143 / 993 (TLS) | Email retrieval |
| SSH | TCP | 22 | Secure remote shell |
| FTP (control) | TCP | 21 | File transfer |
| NTP | UDP | 123 | Time synchronization |
| DHCP | UDP | 67/68 | IP address assignment |

## How a Packet Travels: Full Walkthrough

When you type `https://example.com` into your browser, this is what actually happens:

**Step 1 — DNS resolution**
- Your OS checks its local DNS cache. If the record is not there, it queries your configured DNS resolver (e.g., `8.8.8.8` or your ISP's resolver).
- The resolver performs a full recursive lookup (root → TLD → authoritative) and returns `93.184.216.34` with a TTL.

**Step 2 — TCP + TLS handshake**
- Your OS initiates a TCP three-way handshake to `93.184.216.34:443`.
- SYN leaves your machine, traverses 10–20 routers (each forwarding based on a longest-prefix-match lookup), arrives at the server.
- After TCP is established, a TLS 1.3 handshake (1 round trip) establishes an encrypted channel.

**Step 3 — HTTP request**
- Your browser sends `GET / HTTP/2` over the encrypted connection.
- The server responds with HTML. The browser parses it, discovers CSS/JS/image URLs, and makes additional requests.

**Step 4 — Packet traversal**
- Each IP packet hops through ~10–20 routers across one or more ASes.
- Every router strips the Ethernet header, reads the IP destination, looks up its routing table, and sends the packet out the chosen interface with a new Ethernet header for the next hop.

You can observe these hops with `traceroute`:

```
$ traceroute example.com
 1  192.168.1.1      1 ms   (home router)
 2  10.0.0.1         5 ms   (ISP gateway — CGN)
 3  203.0.113.10    12 ms   (ISP core router)
 4  198.51.100.5    30 ms   (peering router at IXP)
 5  93.184.216.34   45 ms   (Verizon edge → example.com)
```

**Reading traceroute:** Each line is a router that decremented the IP TTL field to zero and sent back an ICMP Time Exceeded message. Latency roughly doubles as you cross an ocean (~70 ms transatlantic, ~130 ms transpacific).

## Content Delivery Networks (CDNs)

Large content providers like Google, Netflix, and Cloudflare operate **CDNs** — geographically distributed caches placed inside or near ISPs. When you stream a Netflix video:

1. DNS returns the IP of a CDN server near you (DNS-based load balancing using anycast).
2. Your video flows from a nearby CDN edge node — a few milliseconds away — rather than from a distant origin.
3. CDNs reduce backbone traffic, lower latency, and absorb DDoS attacks.

CDNs illustrate a key networking truth: **proximity matters**. The speed of light limits how fast you can serve a user 10,000 km away.

## Standards Bodies

The Internet's protocols are defined by open standards maintained by:

- **IETF** (Internet Engineering Task Force) — publishes RFCs (Requests for Comments). TCP is RFC 793; HTTP/1.1 is RFC 7230; TLS 1.3 is RFC 8446.
- **IEEE** — standards for wired (802.3 Ethernet) and wireless (802.11 Wi-Fi, 802.15 Bluetooth) links.
- **ICANN** — manages domain names (DNS root zone) and IP address allocation via RIRs.
- **W3C** — web standards: HTML, CSS, WebRTC.
- **ITU** — telecommunications standards including G.711 (voice codecs) and X.509 (certificates).

Understanding the Internet's layered, decentralized design is the foundation for every topic in this course.
