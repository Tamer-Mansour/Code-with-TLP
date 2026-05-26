# OSI vs TCP/IP Models

Networking is organized into **layers** so that each layer can evolve independently, be implemented separately, and be replaced without affecting the rest of the stack. Two reference models dominate: the **OSI model** (7 layers) and the **TCP/IP model** (4 layers). Understanding both is essential for reading documentation, diagnosing issues ("this is a Layer 3 problem"), and designing systems.

## The OSI Model (7 Layers)

OSI (Open Systems Interconnection) was designed by ISO in the late 1970s as a universal, vendor-neutral framework for protocol design. It is primarily a **conceptual reference** — real Internet implementations use the TCP/IP model — but its 7-layer vocabulary is used everywhere in documentation, network equipment, and troubleshooting.

```
Layer 7  Application   — HTTP, DNS, SMTP, FTP, SSH
Layer 6  Presentation  — Encryption/decryption (TLS), compression, encoding (MIME)
Layer 5  Session       — Session establishment, RPC, NetBIOS
Layer 4  Transport     — TCP, UDP  (end-to-end delivery, ports)
Layer 3  Network       — IP, ICMP, OSPF, BGP  (hop-by-hop routing)
Layer 2  Data Link     — Ethernet, 802.11 Wi-Fi, PPP  (node-to-node framing)
Layer 1  Physical      — Cables, radio, fiber, voltage levels, bit encoding
```

**Memory aid (top-down):** "All People Seem To Need Data Processing"

What each OSI layer does:

| Layer | Name         | Key Responsibility                                      | PDU Name  |
|-------|-------------|----------------------------------------------------------|-----------|
| 7     | Application  | Network services to user software (HTTP GET, DNS query) | Message   |
| 6     | Presentation | Translates data formats, handles encryption/decryption   | Message   |
| 5     | Session      | Establishes, manages, terminates sessions between apps   | Message   |
| 4     | Transport    | End-to-end delivery, multiplexing via ports              | Segment   |
| 3     | Network      | Logical addressing (IP), routing across multiple hops    | Packet    |
| 2     | Data Link    | Physical addressing (MAC), framing, error detection      | Frame     |
| 1     | Physical     | Raw bit transmission; defines voltages, timing, encoding | Bit       |

## The TCP/IP Model (4 Layers)

The TCP/IP (Internet) model maps directly to protocols used on the real Internet. It was defined through practical experience building ARPANET, not by a standards committee working top-down.

```
Layer 4  Application   — HTTP, DNS, SMTP, SSH, FTP, SNMP
Layer 3  Transport     — TCP, UDP
Layer 2  Internet      — IP (IPv4 / IPv6), ICMP, ARP (sometimes placed here)
Layer 1  Link          — Ethernet, Wi-Fi, PPP, ARP
```

## Comparison Table

| OSI Layer | OSI Name      | TCP/IP Layer | Example Protocols                    |
|-----------|---------------|--------------|--------------------------------------|
| 7         | Application   | Application  | HTTP, FTP, SMTP, DNS, SSH, SNMP      |
| 6         | Presentation  | Application  | TLS/SSL, MIME, JPEG, MPEG            |
| 5         | Session       | Application  | RPC, NetBIOS, TLS record protocol    |
| 4         | Transport     | Transport    | TCP, UDP, SCTP                       |
| 3         | Network       | Internet     | IPv4, IPv6, ICMP, OSPF, BGP          |
| 2         | Data Link     | Link         | Ethernet (802.3), 802.11 Wi-Fi, ARP  |
| 1         | Physical      | Link         | Cables, fiber, radio, NIC hardware   |

Key point: the top three OSI layers collapse into TCP/IP's single **Application** layer because the Internet protocol stack does not standardize session management or data encoding — it leaves those to the application.

## Encapsulation: Layer-by-Layer Walkthrough

When a browser sends an HTTP request, each layer of the sender's stack wraps the payload in its own **header** (and sometimes a trailer). This is called **encapsulation**. At the receiver, each layer **decapsulates** — strips its header and passes the payload up.

```
Application layer:
  [HTTP Request: GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n]

Transport layer (TCP adds segment header):
  [TCP Header | HTTP Request]
   src_port=54321  dst_port=80  seq=1000  ack=0  flags=PSH|ACK

Network layer (IP adds packet header):
  [IP Header | TCP Header | HTTP Request]
   src_ip=192.168.1.5  dst_ip=93.184.216.34  proto=6(TCP)  TTL=64

Link layer (Ethernet adds frame header + trailer):
  [Eth Header | IP Header | TCP Header | HTTP Request | CRC-32]
   src_mac=AA:BB:CC:DD:EE:FF  dst_mac=00:11:22:33:44:55  ethertype=0x0800
```

**Numeric sizes for a minimal HTTP GET:**
- HTTP request line: ~30 bytes
- TCP header: 20 bytes
- IP header: 20 bytes
- Ethernet header: 14 bytes + 4 byte FCS
- Total overhead just for headers: 58 bytes wrapping ~30 bytes of payload — more than 2× overhead on small requests!

At each hop (router), the router:
1. Strips the Ethernet frame header.
2. Reads the IP destination address — looks up routing table.
3. Decrements IP TTL by 1 (drops packet and sends ICMP "Time Exceeded" if TTL reaches 0).
4. Writes a *new* Ethernet header for the next hop's MAC address.
5. Sends the frame out the appropriate interface.

Critically, routers **never open** TCP segments or HTTP payloads — they only process Layer 3. This separation is what makes the Internet's core simple and fast.

## Protocol Data Unit (PDU) Names

Each layer has its own name for its unit of data:

| Layer (TCP/IP) | PDU Name | Typical Size |
|----------------|----------|-------------|
| Application    | Message  | Arbitrary   |
| Transport (TCP) | Segment | ≤ 64 KB      |
| Transport (UDP) | Datagram | ≤ 65,507 B  |
| Internet (IP)  | Packet   | ≤ 65,535 B  |
| Link (Ethernet)| Frame    | 64–1518 B   |
| Physical       | Bit      | 1 bit       |

## Why Two Models?

- Use **OSI** for conceptual discussions, vendor-neutral documentation, and troubleshooting frameworks ("this is a Layer 2 problem — check the switch").
- Use **TCP/IP** when describing actual protocols, implementations, and code.
- When a network engineer says "Layer 3," they almost always mean IP routing. "Layer 2" means switching / MAC. "Layer 7" means application-layer filtering or load balancing.

In practice, the lines blur: TLS lives between layers 4 and 7; ARP is sometimes called Layer 2.5; MPLS is "Layer 2.5" too. The layered model is a conceptual tool, not a rigid boundary.

## Troubleshooting with the Model

A structured approach to network debugging works bottom-up:

1. **Physical (L1):** Is the cable plugged in? Is the NIC active? (`ip link show`)
2. **Data Link (L2):** Is the switch port up? Is there an ARP entry? (`arp -a`, `ip neigh`)
3. **Network (L3):** Can you ping the gateway? Is the routing table correct? (`ip route`, `ping`)
4. **Transport (L4):** Is the port open? Is the firewall allowing the connection? (`netstat -an`, `telnet host port`)
5. **Application (L7):** Is the application listening? Are TLS certificates valid? (`curl -v`, browser devtools)

Working bottom-up avoids chasing application-level problems that are actually caused by a physical cable or a misconfigured subnet mask.
