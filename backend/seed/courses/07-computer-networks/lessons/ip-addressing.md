# IP Addressing

Every device that participates in IP networking needs a unique identifier — this is the role of the **IP address**. Understanding IP addressing is fundamental to configuring networks, debugging connectivity issues, designing scalable systems, and passing any network engineering certification.

## IPv4 Addresses

An **IPv4 address** is a 32-bit unsigned integer, conventionally written as four decimal *octets* (8-bit groups) separated by dots — **dotted-decimal notation**:

```
192  .  168  .  10  .  45
 │        │      │      │
 byte 1   byte 2 byte 3  byte 4
 (MSB)                   (LSB)
```

In binary: `11000000.10101000.00001010.00101101`

32-bit integer value: `192×2²⁴ + 168×2¹⁶ + 10×2⁸ + 45 = 3232238637`

The range is `0.0.0.0` to `255.255.255.255` — 2³² ≈ **4.29 billion** unique addresses.

### Special IPv4 Ranges

| Range | Prefix | Purpose | RFC |
|-------|--------|---------|-----|
| `10.0.0.0` – `10.255.255.255` | /8 | Private (Class A) | RFC 1918 |
| `172.16.0.0` – `172.31.255.255` | /12 | Private (Class B) | RFC 1918 |
| `192.168.0.0` – `192.168.255.255` | /16 | Private (Class C) | RFC 1918 |
| `127.0.0.0` – `127.255.255.255` | /8 | Loopback (localhost) | RFC 1122 |
| `169.254.0.0` – `169.254.255.255` | /16 | Link-local / APIPA | RFC 3927 |
| `100.64.0.0` – `100.127.255.255` | /10 | Shared address (CGN) | RFC 6598 |
| `0.0.0.0/8` | /8 | This network | — |
| `255.255.255.255` | /32 | Limited broadcast | — |
| `224.0.0.0` – `239.255.255.255` | /4 | Multicast | RFC 5771 |

RFC 1918 addresses are **not routed on the public Internet** — routers drop them. This is why NAT is required for home and office networks.

## Subnets and CIDR

**CIDR (Classless Inter-Domain Routing)**, introduced in 1993 (RFC 1517–1520), replaced the rigid classful system. CIDR notation is:

```
<IP address>/<prefix length>
```

The **prefix length** is the number of bits used for the **network portion**. The remaining bits identify the **host** within that network.

```
192.168.10.0/26

Prefix length: 26 bits
Host bits: 32 − 26 = 6 bits
Block size: 2⁶ = 64 addresses
```

### Subnet Mask

The subnet mask is a 32-bit number where the first N bits are 1 (network) and the remaining are 0 (host):

```
/24  → 11111111.11111111.11111111.00000000 → 255.255.255.0
/26  → 11111111.11111111.11111111.11000000 → 255.255.255.192
/20  → 11111111.11111111.11110000.00000000 → 255.255.240.0
/8   → 11111111.00000000.00000000.00000000 → 255.0.0.0
```

### Worked Example: 192.168.10.45/26

Step 1 — Write the IP and mask in binary:

```
IP:   11000000.10101000.00001010.00101101   (192.168.10.45)
Mask: 11111111.11111111.11111111.11000000   (/26 = 255.255.255.192)
```

Step 2 — AND the IP with the mask → Network address:

```
      11000000.10101000.00001010.00000000   → 192.168.10.0
```

Step 3 — OR the network address with all-ones host bits → Broadcast address:

```
      11000000.10101000.00001010.00111111   → 192.168.10.63
```

Step 4 — Count usable hosts:

```
2⁶ − 2 = 62 usable hosts  (subtract network addr and broadcast addr)
```

Results:
- **Network address:** `192.168.10.0`
- **First usable host:** `192.168.10.1`
- **Last usable host:** `192.168.10.62`
- **Broadcast address:** `192.168.10.63`
- **Usable hosts:** 62

### Quick Reference Table

| Prefix | Mask | Addresses | Usable Hosts | Block size |
|--------|------|-----------|--------------|-----------|
| /30 | 255.255.255.252 | 4 | 2 | 4 |
| /29 | 255.255.255.248 | 8 | 6 | 8 |
| /28 | 255.255.255.240 | 16 | 14 | 16 |
| /27 | 255.255.255.224 | 32 | 30 | 32 |
| /26 | 255.255.255.192 | 64 | 62 | 64 |
| /25 | 255.255.255.128 | 128 | 126 | 128 |
| /24 | 255.255.255.0 | 256 | 254 | 256 |
| /22 | 255.255.252.0 | 1,024 | 1,022 | 1,024 |
| /20 | 255.255.240.0 | 4,096 | 4,094 | 4,096 |
| /16 | 255.255.0.0 | 65,536 | 65,534 | 65,536 |
| /8 | 255.0.0.0 | 16,777,216 | 16,777,214 | 16,777,216 |

### Classful Addressing (Legacy)

Before CIDR, addresses were divided into classes based on the first few bits:

| Class | First bits | Range | Default Mask | Approx Networks | Hosts/Net |
|-------|-----------|-------|--------------|-----------------|-----------|
| A | 0xxx | 1.0.0.0 – 126.255.255.255 | /8 | 126 | ~16.7 M |
| B | 10xx | 128.0.0.0 – 191.255.255.255 | /16 | 16,384 | 65,534 |
| C | 110x | 192.0.0.0 – 223.255.255.255 | /24 | ~2 M | 254 |
| D | 1110 | 224.0.0.0 – 239.255.255.255 | N/A | Multicast | — |
| E | 1111 | 240.0.0.0 – 255.255.255.255 | N/A | Reserved | — |

Classful addressing wasted enormous amounts of IPv4 space. A company needing 1000 addresses got a Class B (65,534 hosts!) — wasting 64,534 addresses. CIDR fixed this by allowing arbitrary prefix lengths.

## IPv6 Addresses

IPv6 uses **128-bit** addresses, written as eight groups of four hexadecimal digits:

```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

Shorthand rules:
1. Leading zeros in each group may be omitted: `0db8` → `db8`.
2. One contiguous sequence of all-zero groups may be collapsed to `::`: `0000:0000` → `::`.

```
Full:      2001:0db8:85a3:0000:0000:8a2e:0370:7334
Short:     2001:db8:85a3::8a2e:370:7334
```

IPv6 provides **2¹²⁸ ≈ 3.4 × 10³⁸** addresses — enough to give every atom on Earth a trillion addresses.

### IPv4 vs IPv6 Comparison

| Feature | IPv4 | IPv6 |
|---------|------|------|
| Address size | 32 bits | 128 bits |
| Notation | Dotted decimal | Colon-separated hex |
| Address space | ~4.3 billion | ~3.4 × 10³⁸ |
| Header size | 20–60 bytes (variable) | 40 bytes (fixed) |
| Fragmentation | Routers and hosts | Hosts only |
| Broadcast | Yes | No (uses multicast) |
| NAT required | Yes (address exhaustion) | No |
| IPsec | Optional | Mandatory (architecture) |
| Auto-configuration | DHCP | SLAAC + DHCPv6 |
| Checksum in header | Yes | Removed (transport handles it) |

### IPv6 Address Types

| Type | Prefix | Purpose |
|------|--------|---------|
| Global unicast | `2000::/3` | Public routable addresses |
| Link-local | `fe80::/10` | Auto-configured per interface; not routed |
| Unique-local | `fc00::/7` | Private (like RFC 1918 for IPv4) |
| Loopback | `::1/128` | Equivalent to 127.0.0.1 |
| IPv4-mapped | `::ffff:0:0/96` | Represent IPv4 in IPv6 context |
| Multicast | `ff00::/8` | One-to-many delivery |

## DHCP: Dynamic Address Assignment

Manually configuring IP addresses on every device doesn't scale. **DHCP (Dynamic Host Configuration Protocol)** automates it via a four-way exchange (DORA):

```
Client                              DHCP Server
  │── DHCPDISCOVER (broadcast) ───►│  "Anyone have an address for me?"
  │◄── DHCPOFFER ──────────────────│  "Here's 192.168.1.50, lease 24 hrs"
  │── DHCPREQUEST (broadcast) ────►│  "I accept 192.168.1.50"
  │◄── DHCPACK ────────────────────│  "Confirmed — lease starts now"
```

DHCP delivers: IP address, subnet mask, default gateway, DNS server(s), and lease duration. IPv6 uses DHCPv6 or **SLAAC** (Stateless Address Autoconfiguration), where devices generate their own address from the network prefix + their MAC address (EUI-64).
