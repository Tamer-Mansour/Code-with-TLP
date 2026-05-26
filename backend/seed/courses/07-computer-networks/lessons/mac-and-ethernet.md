# MAC Addresses and Ethernet

The **Link Layer** (Layer 2) is responsible for transferring frames between two *directly connected* nodes — nodes on the same physical network segment. Ethernet is the dominant wired link-layer technology for LANs; Wi-Fi (IEEE 802.11) is its wireless counterpart. MAC addresses are the link-layer identifiers that make local delivery possible.

## MAC Addresses

A **MAC (Media Access Control) address** is a 48-bit hardware identifier, typically burned into a **NIC (Network Interface Card)** at manufacturing time. It uniquely identifies an interface within a single network segment.

```
Format: 6 octets written as colon-separated (or hyphen-separated) hex
Example: 00:1A:2B:3C:4D:5E

Byte layout:
+──────────────+──────────────+
│ OUI (3 B)    │  NIC-ID (3 B) │
│ (manufacturer)│ (unique to card) │
+──────────────+──────────────+
```

The **OUI (Organizationally Unique Identifier)** — the first 3 bytes — is assigned by IEEE to manufacturers. `00:1A:2B` is assigned to a specific vendor. You can look up any OUI at standards.ieee.org/develop/regauth/oui/. The remaining 3 bytes are assigned by the manufacturer to uniquely identify the NIC.

Two special bit flags in the first byte:
- **Bit 0 (LSB)**: Multicast bit. If 1, the frame is addressed to a group. `FF:FF:FF:FF:FF:FF` (all bits 1) is the **broadcast** address — received and processed by every device on the segment.
- **Bit 1**: Locally administered (LAA) bit. If 1, the address was assigned by software rather than burned in at the factory. VMs, containers, and VPNs commonly set this bit.

MAC addresses are **link-local** — they have no meaning beyond a single network segment. When a packet traverses a router, the Ethernet frame is stripped and rebuilt with new MAC addresses for the next segment. The IP addresses in the packet's header remain unchanged end-to-end; the MAC addresses change at every hop.

## Ethernet Frame Format (IEEE 802.3)

```
+──────────+───────+───────+───────────+──────────────+──────+
│ Preamble │DstMAC │SrcMAC │ EtherType │   Payload    │ FCS  │
│  (8 B)   │ (6 B) │ (6 B) │  (2 B)   │ (46–1500 B)  │ (4 B)│
+──────────+───────+───────+───────────+──────────────+──────+
```

| Field | Size | Purpose |
|-------|------|---------|
| Preamble | 7 B | Alternating 1s and 0s (`10101010…`) — allows receiver to synchronize clock |
| SFD (Start Frame Delimiter) | 1 B | `10101011` — signals start of frame; last byte of preamble field |
| Destination MAC | 6 B | Target hardware address (unicast, multicast, or broadcast) |
| Source MAC | 6 B | Sender's hardware address |
| EtherType | 2 B | Layer-3 protocol: `0x0800`=IPv4, `0x0806`=ARP, `0x86DD`=IPv6, `0x8100`=VLAN-tagged |
| Payload | 46–1500 B | Encapsulated IP packet (or ARP, etc.). Minimum 46 bytes — padded if needed |
| FCS (Frame Check Sequence) | 4 B | CRC-32 over Dst+Src+EtherType+Payload — detects transmission errors |

The maximum payload is **1500 bytes** — the standard **MTU (Maximum Transmission Unit)**. IP packets larger than the MTU must be **fragmented** at the IP layer (each fragment fits in one Ethernet frame). Jumbo frames (up to 9000 bytes) are supported on many switches and can dramatically improve throughput for bulk transfers inside data centers.

**Minimum frame size:** 64 bytes (including header and FCS). Short frames are padded. This is needed for collision detection in half-duplex Ethernet.

## Ethernet Hubs vs. Switches vs. Routers

| Device | Layer | How it forwards | Collision domain | Broadcast domain |
|--------|-------|----------------|-----------------|-----------------|
| **Hub** | L1 | Replicates bits on all ports | Single (all ports) | Single |
| **Bridge** | L2 | Forwards frames by MAC table | Per-port | Single |
| **Switch** | L2 | Forwards frames by MAC table | Per-port (micro-segmentation) | Single |
| **Router** | L3 | Routes packets by IP + routing table | Per-port | Per-interface (separate broadcast domain) |

Hubs are obsolete. Modern networks use switches exclusively. Switches eliminate collisions by dedicating a full-duplex link to each device.

### Switch MAC Address Learning

A switch learns MAC-to-port mappings dynamically by watching the **source MAC** of every incoming frame:

```
Time 0: Frame arrives on port 1 with src=AA:BB:CC
        → Learn: AA:BB:CC lives on port 1
        → Destination DD:EE:FF not in table → Flood all ports except 1

Time 5: Reply arrives on port 3 with src=DD:EE:FF
        → Learn: DD:EE:FF lives on port 3
        → Now forward future frames for DD:EE:FF only to port 3
```

The MAC table (also called a **CAM table** — Content Addressable Memory) has a limited size. A **MAC flooding attack** fills the table with fake MACs, causing the switch to flood frames like a hub — allowing an attacker to eavesdrop (implemented via tools like `macof`).

**VLAN (Virtual LAN):** Switches can partition a physical switch into multiple logical broadcast domains using VLANs (IEEE 802.1Q). Each VLAN is an isolated Layer-2 network. A trunk port carries frames for multiple VLANs, tagged with a 4-byte 802.1Q header (`EtherType=0x8100`).

## ARP: Address Resolution Protocol (RFC 826)

When a host wants to send an IP packet to another host **on the same subnet**, it needs the destination's MAC address. **ARP** discovers this mapping dynamically.

### ARP Process — Full Walkthrough

```
Host A:  IP=192.168.1.10, MAC=AA:AA:AA:AA:AA:AA
Host B:  IP=192.168.1.20, MAC=BB:BB:BB:BB:BB:BB
Host C:  IP=192.168.1.30, MAC=CC:CC:CC:CC:CC:CC
All connected to the same switch.

A wants to send a packet to 192.168.1.20.
A's ARP cache: empty.

Step 1: A broadcasts ARP Request:
  Ethernet: src=AA:AA:AA:AA:AA:AA  dst=FF:FF:FF:FF:FF:FF
  ARP:      sender_ip=192.168.1.10  sender_mac=AA:AA:AA:AA:AA:AA
            target_ip=192.168.1.20  target_mac=00:00:00:00:00:00 (unknown)

  Switch floods this frame to B and C.

Step 2: B recognizes its own IP, sends unicast ARP Reply:
  Ethernet: src=BB:BB:BB:BB:BB:BB  dst=AA:AA:AA:AA:AA:AA
  ARP:      sender_ip=192.168.1.20  sender_mac=BB:BB:BB:BB:BB:BB
            target_ip=192.168.1.10  target_mac=AA:AA:AA:AA:AA:AA

Step 3: A caches 192.168.1.20 → BB:BB:BB:BB:BB:BB (typically for 10–20 minutes).
        A can now send the IP packet directly to B.
```

ARP cache inspection:

```bash
arp -a                  # Windows / macOS / Linux
ip neigh show           # Linux (iproute2)
```

### ARP for Off-Subnet Traffic

If Host A wants to reach a host on a *different* subnet (e.g., `8.8.8.8`), it ARPs for the **default gateway's** IP address, not for `8.8.8.8`. The gateway's MAC is placed in the Ethernet header; the IP destination is `8.8.8.8`. The router decapsulates the Ethernet frame and routes the IP packet onward.

### Gratuitous ARP

A **gratuitous ARP** is an ARP reply sent by a host without a prior request, announcing `"IP X is at MAC Y"`. Used for:
- Updating neighbors' ARP caches after a failover (VRRP/HSRP).
- Detecting IP address conflicts on startup.
- **ARP poisoning attacks** — malicious gratuitous ARPs.

### ARP Poisoning (ARP Spoofing)

An attacker sends unsolicited ARP Replies claiming their MAC corresponds to the gateway's IP. All hosts update their ARP caches, routing their traffic through the attacker — a classic Layer-2 man-in-the-middle attack.

**Defense:** **Dynamic ARP Inspection (DAI)** on managed switches cross-references ARP packets against the DHCP snooping binding table and drops packets with mismatched IP-MAC pairs.
