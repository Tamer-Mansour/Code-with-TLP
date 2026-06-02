# Network Byte Order in Protocols

Network byte order is simply big-endian — most significant byte first. The Internet Engineering Task Force (IETF) standardised this in RFC 1700, and every TCP/IP protocol from IPv4 to DNS follows it. Understanding where and how it applies prevents a whole class of protocol bugs.

## Where Network Byte Order Applies

| Protocol field | Size | Notes |
|----------------|------|-------|
| IPv4 source/destination address | 32-bit | `struct in_addr` |
| IPv4 total length, checksum | 16-bit | `struct iphdr` |
| TCP/UDP port numbers | 16-bit | Always big-endian in packets |
| TCP sequence/ack numbers | 32-bit | Big-endian |
| DNS resource record TTL | 32-bit | Big-endian |
| HTTP/2 frame length | 24-bit | Big-endian, custom width |

## The Socket API and `sockaddr_in`

The POSIX socket API requires that ports and addresses in `sockaddr_in` be stored in network byte order:

```cpp
#include <arpa/inet.h>
#include <netinet/in.h>
#include <cstring>

sockaddr_in addr{};
addr.sin_family      = AF_INET;
addr.sin_port        = htons(8080);           // host → network byte order
addr.sin_addr.s_addr = htonl(INADDR_ANY);     // 0.0.0.0 in NBO
// or parse a dotted string:
inet_pton(AF_INET, "192.168.1.1", &addr.sin_addr);  // already stores in NBO
```

If you forget `htons` and write `addr.sin_port = 8080` on a little-endian machine, the port is stored as `0x901F` in the packet (bytes swapped), and the kernel binds to port 8224 instead.

## Reading a Raw Packet Header

When you receive raw bytes — via a raw socket or a packet capture — and interpret protocol fields, every multi-byte field must go through `ntohs`/`ntohl`:

```cpp
#include <netinet/ip.h>   // struct iphdr
#include <cstdio>

void print_ip_header(const uint8_t* packet) {
    const struct iphdr* ip = reinterpret_cast<const struct iphdr*>(packet);

    printf("Total length: %u bytes\n", ntohs(ip->tot_len));
    printf("Protocol:     %u\n",       ip->protocol);   // 1-byte, no swap needed
    printf("Checksum:     0x%04X\n",   ntohs(ip->check));
}
```

Single-byte fields require no byte swapping — there is nothing to swap.

## Implementing a Simple Protocol: Echo Header

```cpp
// Wire format: [4-byte magic BE][2-byte payload_len BE][payload bytes]
#include <cstdint>
#include <cstring>
#include <arpa/inet.h>

constexpr uint32_t MAGIC = 0xDEADBEEF;

void build_echo_header(uint8_t* buf, uint16_t payload_len) {
    uint32_t magic_net = htonl(MAGIC);
    uint16_t len_net   = htons(payload_len);
    std::memcpy(buf,     &magic_net, 4);
    std::memcpy(buf + 4, &len_net,   2);
}

bool parse_echo_header(const uint8_t* buf, uint16_t* payload_len) {
    uint32_t magic_net;
    std::memcpy(&magic_net, buf, 4);
    if (ntohl(magic_net) != MAGIC) return false;

    uint16_t len_net;
    std::memcpy(&len_net, buf + 4, 2);
    *payload_len = ntohs(len_net);
    return true;
}
```

## Common Mistakes

- **Forgetting `htons` for port numbers**: the most common socket programming bug for beginners.
- **Double conversion**: calling `htonl` on a value that is already in network byte order (e.g., the result of a previous `htonl`).
- **`inet_addr` vs `inet_pton`**: `inet_addr` returns an address already in network byte order; do not pass it through `htonl`. `inet_pton` stores to a `struct in_addr` which is also already in NBO.
- **Assuming NBO = host order**: on a big-endian machine, `htonl` is a no-op but you must still call it for portability — the code may be compiled for little-endian later.

## Tip: Use a Consistent Wrapper

In real protocol code, wrap every field access so the call sites are clean:

```cpp
struct EchoHeader {
    uint32_t magic;       // stored in NBO
    uint16_t payload_len; // stored in NBO
} __attribute__((packed));

uint16_t get_payload_len(const EchoHeader* h) {
    return ntohs(h->payload_len);
}
```

> **Interview answer:** Network byte order is big-endian. Use `htons`/`htonl` when writing values into packet buffers or `sockaddr_in`, and `ntohs`/`ntohl` when reading them back. Single-byte fields need no conversion.
