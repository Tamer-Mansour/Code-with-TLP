# Network Threats and Attacks

Network security begins with understanding what can go wrong. Real systems are exploited by combining protocol weaknesses, implementation bugs, and human factors. This lesson surveys the major categories of network threats, explains the underlying protocol mechanisms they exploit, and describes the countermeasures that modern networks deploy.

## The CIA Triad

All security goals can be framed around three properties:

| Property | Meaning | Example Threat |
|----------|---------|---------------|
| **Confidentiality** | Data is readable only by intended parties | Eavesdropping, packet sniffing, stolen TLS keys |
| **Integrity** | Data is not modified in transit or at rest | Man-in-the-middle modification, replay attacks |
| **Availability** | Services remain accessible to legitimate users | DoS/DDoS, ransomware, link flooding |

A fourth property is often added: **Authenticity** — the claim of identity is verifiable. TLS certificates, DNSSEC, and DKIM all provide authenticity.

## Passive Attacks

Passive attacks observe without modifying. They are hard to detect.

### Packet Sniffing (Eavesdropping)

An attacker on the same network segment (a compromised hub, rogue Wi-Fi access point, or insider on the LAN) captures all traffic passing by. On a Wi-Fi network, all frames are broadcast over the air — anyone with a wireless NIC in promiscuous mode can capture them.

```
Alice ──[plaintext HTTP]──► Switch ──[copy]──► Attacker
```

Tools like **Wireshark**, **tcpdump**, and **Zeek** make packet capture trivial. On unencrypted protocols (HTTP, FTP, Telnet), credentials and data are exposed in plaintext.

**Mitigations:** TLS/HTTPS for all application traffic; WPA3-Enterprise for Wi-Fi; end-to-end encryption (Signal protocol); VPN for remote access.

### Traffic Analysis

Even when traffic is encrypted, an attacker observing packet sizes, timing, and destination IPs can infer behavior — which websites you visit, when you communicate, with whom. This is **metadata-level surveillance**.

**Mitigations:** Tor (onion routing), VPNs (hide destination IP from ISP), padding to obscure packet sizes.

## Active Attacks

Active attacks modify, inject, or block traffic.

### Man-in-the-Middle (MitM)

The attacker positions themselves between two communicating parties, intercepting and potentially modifying traffic:

```
Alice ──► Attacker (reads, optionally modifies) ──► Bob
```

Enablers:
- **ARP poisoning**: attacker poisons LAN ARP caches so traffic to the gateway flows through the attacker first.
- **DNS hijacking / rogue DNS server**: attacker serves forged DNS responses mapping `bank.com` to the attacker's server.
- **Rogue Wi-Fi AP**: attacker creates an open hotspot with a convincing SSID; victims connect and all traffic passes through the attacker.
- **BGP hijacking**: attacker announces a more-specific prefix, attracting global traffic for a victim's address range.

**Mitigations:** TLS with strict certificate validation; HSTS (HTTP Strict Transport Security) with preloading; certificate pinning; DNSSEC; authenticated BGP (RPKI).

### IP Spoofing

An attacker sends packets with a **forged source IP address**, impersonating another host. TCP prevents impersonation for established connections (because the attacker can't see ACKs due to routing), but UDP is vulnerable.

IP spoofing enables:
- **DDoS amplification** — spoof the victim's IP as the source of small queries to amplifiers.
- **Bypassing IP-based access controls** (firewall rules that only check source IP).

**Mitigations:** BCP38 — ISPs should block outbound packets whose source IP is not from their own prefix (**ingress filtering**). Unfortunately, BCP38 is not universally deployed.

### TCP SYN Flood

The attacker sends a flood of SYN packets, never completing the three-way handshake. The server allocates state (**TCB — Transmission Control Block**) for each half-open connection, filling its connection table until legitimate clients are refused.

```
Attacker (spoofed src IPs) ──── SYN ──── SYN ──── SYN ────► Server
Server allocates state for each; SYN-ACKs go nowhere (spoofed source)
Server's connection table fills → new SYN packets are dropped
```

**SYN cookies** (RFC 4987): the server encodes the connection parameters in the initial sequence number (ISN) rather than allocating a TCB. The TCB is only allocated if the client completes the handshake with the correct ACK number. Effectively stateless until the handshake completes.

**Other mitigations:** SYN rate limiting; reverse-proxy/CDN absorbs the flood before it reaches the origin.

### DNS Cache Poisoning

An attacker attempts to inject a forged DNS response into a recursive resolver's cache, redirecting users to a malicious server. Before DNSSEC:
- The attacker sends many forged UDP responses to the resolver, trying to guess the transaction ID (16 bits) before the real response arrives.
- **Kaminsky attack (2008)**: ask for random nonexistent subdomains to force cache misses; race the authoritative server's response with floods of forged responses.

Modern resolvers use randomized source ports in addition to random query IDs — making the attack require 2³² guesses instead of 2¹⁶.

**Mitigations:** DNSSEC (cryptographic signatures on records); DNS over TLS/HTTPS (harder to inject in transit); resolver source-port randomization.

### Replay Attack

An attacker captures a valid authentication message (login token, session cookie) and replays it later to gain unauthorized access.

```
Alice ──► captures ──► bank.com: Cookie: session=abc123
Attacker replays: bank.com ←── Cookie: session=abc123
```

**Mitigations:** Short-lived session tokens with expiry; nonces (number used once) in authentication exchanges — the server checks that each nonce is unique; TOTP (time-based tokens, valid only for 30 seconds).

## Denial of Service (DoS and DDoS)

### DoS (Single Source)

A single machine floods the target with traffic, exhausting CPU, bandwidth, or connection table capacity.

### DDoS (Distributed DoS)

Many compromised machines (a **botnet**) simultaneously attack a target. Botnets can number in the millions of IoT devices (Mirai botnet, 2016: ~600,000 cameras and DVRs, ~1 Tbps peak).

### Amplification Attacks

UDP protocols that return large responses to small queries are **amplifiers**. The attacker sends a tiny spoofed request (src IP = victim's IP); the amplifier sends a large response to the victim.

| Amplifier Protocol | Request size | Response size | Amplification |
|-------------------|-------------|---------------|---------------|
| DNS (ANY query) | ~60 B | ~3,000 B | ~50× |
| NTP (monlist) | ~40 B | ~48 KB | ~1,200× |
| Memcached (UDP) | ~15 B | ~750 KB | ~50,000× |
| SSDP (UPnP) | ~30 B | ~1,900 B | ~60× |

**Mitigations:** Rate-limit large DNS/NTP responses; disable reflective UDP modes; BCP38 ingress filtering; scrubbing centers that absorb volumetric DDoS.

## Malware and Botnets

| Type | Behavior | Notable examples |
|------|----------|-----------------|
| **Worm** | Self-replicates over network without user action | WannaCry, Conficker, Mirai |
| **Botnet** | Network of compromised hosts controlled via C2 channel | Mirai, Emotet, ZeroAccess |
| **Rootkit** | Hides attacker's presence; intercepts OS calls | Necurs |
| **Ransomware** | Encrypts data; spreads via network shares | WannaCry, NotPetya |
| **Spyware** | Exfiltrates data (keyloggers, screenshots) | FinFisher |

WannaCry (2017) spread by exploiting EternalBlue, an SMBv1 vulnerability in Windows, propagating automatically across networks without user interaction — a worm behavior. It infected 200,000+ machines in 150 countries within days.

## Defense in Depth

No single control is sufficient. Security is layered:

```
Internet → Border Router (ACL) → Firewall → IDS/IPS → DMZ
                                                ↓
                                      Web/App Servers
                                                ↓
                                      Internal Firewall
                                                ↓
                                      Core LAN (VLANs, DAI, 802.1X)
```

- **Firewall**: packet filter or stateful inspection. Controls what traffic may enter/leave.
- **IDS** (Intrusion Detection System): monitors traffic for signatures of known attacks; generates alerts.
- **IPS** (Intrusion Prevention System): IDS that also drops/rejects malicious traffic inline.
- **DMZ** (Demilitarized Zone): public-facing servers isolated from the internal corporate network by a second firewall.
- **VPN**: encrypted tunnel for remote workers to access internal resources securely.
- **Network segmentation**: separate development, production, and HR networks using VLANs and ACLs — limit lateral movement after a compromise.
- **Zero Trust**: never assume a host is trusted based on network location alone; authenticate and authorize every request.

Understanding attacks in terms of which protocol layer they exploit — and which countermeasure operates at the same layer — is the foundation of network security engineering.
