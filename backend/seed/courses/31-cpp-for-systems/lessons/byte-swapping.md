# Byte Swapping and htonl/ntohl

Once you know two endpoints use different byte orders, you need to swap bytes to translate between them. C provides the classic `htonl`/`ntohl` family; modern C++ adds intrinsics and standard library helpers.

## The POSIX Socket Byte-Order Functions

These four functions live in `<arpa/inet.h>` on POSIX systems (`<winsock2.h>` on Windows):

| Function | Meaning | Operand |
|----------|---------|---------|
| `htons` | host to network short | `uint16_t` |
| `htonl` | host to network long | `uint32_t` |
| `ntohs` | network to host short | `uint16_t` |
| `ntohl` | network to host long | `uint32_t` |

"Network byte order" is big-endian. On a big-endian host these functions are no-ops; on a little-endian host they swap.

```cpp
#include <cstdint>
#include <arpa/inet.h>  // POSIX; use <winsock2.h> on Windows
#include <cstdio>

int main() {
    uint32_t host_val = 0x12345678;
    uint32_t net_val  = htonl(host_val);

    printf("Host:    0x%08X\n", host_val);  // 0x12345678
    printf("Network: 0x%08X\n", net_val);   // 0x78563412 on little-endian
}
```

There is no 64-bit version in the standard socket API. Projects often define `htonll` manually or use OS-specific helpers like `htobe64` (Linux) or `_byteswap_uint64` (MSVC).

## Manual Byte Swap

Understanding what swap actually does is important for writing portable code when no library function is available:

```cpp
#include <cstdint>

constexpr uint16_t swap16(uint16_t x) {
    return (uint16_t)((x >> 8) | (x << 8));
}

constexpr uint32_t swap32(uint32_t x) {
    return ((x & 0xFF000000u) >> 24) |
           ((x & 0x00FF0000u) >>  8) |
           ((x & 0x0000FF00u) <<  8) |
           ((x & 0x000000FFu) << 24);
}

constexpr uint64_t swap64(uint64_t x) {
    return ((x & 0xFF00000000000000ULL) >> 56) |
           ((x & 0x00FF000000000000ULL) >> 40) |
           ((x & 0x0000FF0000000000ULL) >> 24) |
           ((x & 0x000000FF00000000ULL) >>  8) |
           ((x & 0x00000000FF000000ULL) <<  8) |
           ((x & 0x0000000000FF0000ULL) << 24) |
           ((x & 0x000000000000FF00ULL) << 40) |
           ((x & 0x00000000000000FFULL) << 56);
}
```

Because these are `constexpr`, the compiler can evaluate them at compile time for constant operands.

## Compiler Intrinsics (Faster in Practice)

Modern compilers map byte-swap operations to a single instruction (`BSWAP` on x86) when you use their intrinsics:

```cpp
// GCC / Clang
uint32_t x = __builtin_bswap32(val);
uint64_t y = __builtin_bswap64(val);

// MSVC
#include <stdlib.h>
uint32_t x = _byteswap_ulong(val);
uint64_t y = _byteswap_uint64(val);
```

In practice, even the manual shift/OR version usually compiles to `BSWAP` under `-O2` because compilers recognise the pattern.

## C++23: `std::byteswap`

C++23 adds `std::byteswap` in `<bit>`:

```cpp
#include <bit>
#include <cstdint>

uint32_t swapped = std::byteswap(uint32_t{0x12345678});
// swapped == 0x78563412
```

This is the cleanest portable solution when targeting C++23.

## Worked Example: Sending a 32-bit Integer Over a Socket

```cpp
#include <cstdint>
#include <arpa/inet.h>
#include <cstring>

void send_uint32(int socket_fd, uint32_t value) {
    uint32_t net = htonl(value);     // convert to network byte order
    uint8_t buf[4];
    std::memcpy(buf, &net, 4);       // copy to byte buffer
    // write(socket_fd, buf, 4);     // send 4 bytes
}

uint32_t recv_uint32(const uint8_t* buf) {
    uint32_t net;
    std::memcpy(&net, buf, 4);       // reconstruct integer
    return ntohl(net);               // convert back to host byte order
}
```

## Common Pitfalls

- **Double-swapping**: calling `htonl` on data that is already in network order. This is especially easy when refactoring existing code.
- **Forgetting 64-bit**: `htonl` only handles 32-bit values. Ports, addresses, and sequence numbers fit; file sizes and timestamps often do not.
- **Swapping after write**: always convert before writing to the buffer, not after.

> **Interview answer:** `htonl`/`ntohl` convert a 32-bit integer between host byte order and big-endian network byte order. On little-endian machines they swap all four bytes; on big-endian machines they are no-ops. Use them whenever writing integers to sockets or network buffers.
