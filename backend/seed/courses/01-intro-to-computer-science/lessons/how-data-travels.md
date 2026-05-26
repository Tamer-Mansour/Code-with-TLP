# How Data Travels: Networking Fundamentals

The Internet connects billions of devices worldwide. Understanding how data travels from one device to another is foundational for any software developer—it explains everything from why some websites load slowly to why video calls sometimes freeze.

## Packets: How Data Is Divided

When you send a file, a message, or a webpage request, the data is not sent as one continuous stream. Instead, it is split into small chunks called **packets**.

A typical packet is 1,500 bytes or smaller (the maximum is set by the **MTU**, Maximum Transmission Unit, for a given network link).

### Anatomy of a Packet

Each packet has two parts:

- **Header** — bookkeeping information:
  - Source IP address (where the packet came from)
  - Destination IP address (where it is going)
  - Sequence number (so the receiver can reassemble packets in order)
  - Protocol information (is this TCP or UDP?)
  - Checksum (to detect corruption in transit)
- **Payload** — a chunk of the actual data (typically up to 1,460 bytes for TCP)

### Why Packets?

Packet switching has major advantages over circuit switching (dedicated end-to-end connections):

1. **Multiplexing** — multiple conversations share the same physical link simultaneously; packets from different senders interleave.
2. **Resilience** — if one packet is lost or corrupted, only that packet is resent; the rest of the file is not affected.
3. **Routing flexibility** — packets from the same file can take different routes through the network and still arrive at the destination.
4. **Efficient use** — a link is only "used" when there are packets to send; idle capacity is shared.

**Analogy:** Imagine shipping a 100-page manuscript overseas. You could send all 100 pages in a single large parcel (circuit switching), but if it gets lost, you lose everything. Or you could send 10 envelopes of 10 pages each (packet switching)—if one envelope is lost, you only re-send 10 pages. The envelopes can even go via different postal routes.

## IP Addresses

Every device on the Internet needs an **IP address** (Internet Protocol address)—a unique numerical label that identifies it on the network, like a postal address for data.

### IPv4

The older standard uses four numbers (0–255) separated by dots. Underneath, this is a **32-bit binary number**:

```
192.168.1.42

In binary:
11000000 . 10101000 . 00000001 . 00101010
```

IPv4 allows 2³² ≈ **4.3 billion** addresses. In the early internet this seemed enormous, but with smartphones, IoT devices, and cloud servers, we have essentially exhausted the space. **NAT (Network Address Translation)** lets multiple devices share one public IP address, partially alleviating this.

### IPv6

The newer standard uses eight groups of four hex digits separated by colons:

```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

IPv6 uses **128 bits** → 2¹²⁸ ≈ **3.4 × 10³⁸** addresses. That is roughly 5 × 10²⁸ addresses for every person alive today—enough to assign a unique IP to every grain of sand on Earth many times over.

IPv6 addresses can be abbreviated: consecutive groups of zeros can be replaced with `::`. For example, `2001:0db8::1` is the shortened form of `2001:0db8:0000:0000:0000:0000:0000:0001`.

### Special IP Addresses

| Address | Purpose |
|---------|---------|
| `127.0.0.1` (IPv4) or `::1` (IPv6) | Loopback — refers to "this machine" |
| `192.168.x.x` or `10.x.x.x` | Private networks (not routed on the public Internet) |
| `0.0.0.0` | "Any address" — used when a server listens on all interfaces |
| `255.255.255.255` | Broadcast — send to all devices on local network |

## DNS: The Internet's Phone Book

Humans remember names like `google.com`, not `142.250.80.46`. The **Domain Name System (DNS)** is a globally distributed database that translates human-readable **domain names** into IP addresses.

### DNS Hierarchy

```
Root DNS servers (13 groups worldwide)
    └── TLD servers (.com, .org, .net, .uk, ...)
            └── Authoritative servers (google.com, example.org, ...)
```

### DNS Lookup Process

When you type `www.example.com` in your browser:

```
1. Check browser cache — has this IP been looked up recently?
       ↓ (cache miss)
2. Check OS hosts file (/etc/hosts) — any manual overrides?
       ↓
3. Ask your local DNS resolver (your ISP or 8.8.8.8/1.1.1.1)
       ↓ (if resolver doesn't have it cached)
4. Resolver asks a root DNS server: "Who handles .com?"
       ↓
5. Root server responds: "Ask the .com TLD server"
       ↓
6. Resolver asks the .com TLD server: "Who handles example.com?"
       ↓
7. TLD server responds: "Ask example.com's authoritative server"
       ↓
8. Resolver asks example.com's authoritative DNS server
       ↓
9. Authoritative server responds: "www.example.com is 93.184.216.34"
       ↓
10. Resolver caches the result (for the TTL duration) and returns it
```

This whole process typically takes **10–50 milliseconds**. Each result is cached for a period specified by the record's **TTL (Time To Live)**, so popular domains are usually answered from cache in microseconds.

### DNS Record Types

| Type | Purpose | Example |
|------|---------|---------|
| A | Domain → IPv4 address | `example.com → 93.184.216.34` |
| AAAA | Domain → IPv6 address | `example.com → 2606:2800::1` |
| CNAME | Alias to another domain | `www.example.com → example.com` |
| MX | Mail server for a domain | `example.com → mail.example.com` |
| TXT | Arbitrary text (verification, SPF) | `v=spf1 include:...` |

## Routers and Routing

**Routers** are specialised networking devices that forward packets toward their destination. They operate at the Internet layer and maintain **routing tables**: databases mapping destination IP ranges to the next hop (which interface/router to send the packet to).

When a packet arrives, a router:
1. Reads the destination IP from the packet header
2. Looks up the best matching entry in its routing table
3. Forwards the packet to the next-hop router or directly to the destination

A packet from London to Tokyo might traverse 10–20 routers. Each router looks at only the destination IP and makes a local forwarding decision—no router needs to know the complete path. This is called **hop-by-hop routing**.

You can see this in action with the `traceroute` (Linux/Mac) or `tracert` (Windows) command, which shows every router hop along the path.

## The TCP/IP Protocol Stack

Networking is organised into **layers**. Each layer adds a header (and removes it on the receiving side), creating a "envelope-within-envelope" structure called **encapsulation**.

The TCP/IP model has four layers:

| Layer | Protocols | Responsibility |
|-------|----------|---------------|
| **Application** | HTTP, HTTPS, FTP, SMTP, DNS, SSH | What the application wants to do |
| **Transport** | TCP, UDP | End-to-end delivery guarantees |
| **Internet** | IP (IPv4, IPv6), ICMP | Addressing and routing across networks |
| **Link** | Ethernet, Wi-Fi (802.11), fibre | Physical transmission on one link |

### TCP vs UDP

**TCP (Transmission Control Protocol):**
- Guarantees delivery: lost packets are automatically retransmitted
- Guarantees order: packets are reassembled in sequence even if they arrive out of order
- Detects corruption: checksums verify data integrity
- **Cost:** higher overhead, small delay from acknowledgements

**UDP (User Datagram Protocol):**
- Fire-and-forget: no retransmission, no ordering guarantees
- Much lower overhead
- **Ideal for:** live video calls, online games, DNS queries—where speed matters more than perfect reliability, and a missed packet is better than a late one

| Feature | TCP | UDP |
|---------|-----|-----|
| Delivery guaranteed | Yes | No |
| Order guaranteed | Yes | No |
| Connection setup | Yes (3-way handshake) | No (connectionless) |
| Overhead | Higher | Lower |
| Use cases | Web, email, file transfer | Video streaming, VoIP, gaming, DNS |

### The TCP Three-Way Handshake

Before any data is sent, TCP establishes a connection:

```
Client                          Server
  │──── SYN (sequence=x) ────→│
  │←── SYN-ACK (seq=y, ack=x+1) ─│
  │──── ACK (ack=y+1) ────────→│
  │                             │
  │←────── Data exchange ──────→│
```

This ensures both sides are ready and agree on starting sequence numbers. For HTTPS connections, a TLS handshake follows to establish encryption keys.

## Common Misconceptions

**"The Internet is a single network."**
The Internet is a **network of networks**: ISPs, data centre networks, university networks, corporate networks, mobile carrier networks—all interconnected. "The Internet" has no single owner or central control.

**"Wi-Fi is the Internet."**
Wi-Fi is a wireless link-layer technology that connects your device to a local router. That router then connects to an ISP (via fibre, cable, or cellular), which connects to the Internet backbone. Wi-Fi is just one hop in the chain.

**"Bigger packets are always faster."**
Larger packets carry more payload per header overhead, but they also take longer to transmit on slow links, are more likely to be corrupted (requiring a full retransmit), and can cause buffering issues. Network MTU limits exist for good reasons.

## Key Takeaways

- Data is broken into **packets** for multiplexed, resilient transmission across shared networks.
- **IP addresses** uniquely identify devices; IPv4 is 32-bit (~4.3 billion); IPv6 is 128-bit (effectively unlimited).
- **DNS** translates human-readable names to IP addresses using a hierarchical, globally distributed system.
- **Routers** make hop-by-hop forwarding decisions; packets from the same file can take different routes.
- **TCP** guarantees reliable, ordered delivery; **UDP** is faster and lighter but offers no guarantees.
- The TCP/IP stack organises networking into four layers: application → transport → internet → link.
