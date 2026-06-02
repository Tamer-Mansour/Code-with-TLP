# Endianness Across Buses and Peripherals

In a real SoC, multiple components with potentially different native endianness are connected by a shared bus fabric. Understanding how endianness is handled — or mis-handled — at bus boundaries is critical for correct hardware design and for building accurate TLM virtual platforms.

## The Problem: Mismatched Endianness

Consider a little-endian ARM CPU writing `0xDEADBEEF` to a big-endian PCIe endpoint. The CPU stores bytes in memory as:

```
Address:  +0   +1   +2   +3
Data:     EF   BE   AD   DE   (little-endian in CPU memory)
```

The PCIe endpoint expects the MSB first:

```
Address:  +0   +1   +2   +3
Expected: DE   AD   BE   EF   (big-endian)
```

Without an explicit byte-swap, the endpoint reads `0xEFBEADDE` — completely wrong.

## Where Byte-Swapping Happens

Endianness conversion can occur at several points in the path:

1. **Software** — the driver calls `htobe32()` / `cpu_to_be32()` before writing to the device.
2. **Bus bridge** — a dedicated byte-swap bridge module in the interconnect reverses bytes on the fly. AHB-to-AXI bridges sometimes include this.
3. **The peripheral itself** — some peripherals expose an endian-configuration register so they can be set to match the host.
4. **DMA controller** — some DMA engines have a byte-swap mode bit.

The golden rule: **decide where the swap happens and enforce it at exactly one point** — doing it at two points cancels out (correctly), but doing it at none or at three is a bug.

## AXI and AMBA Endianness

ARM's AXI and AHB buses are endian-neutral: they carry bytes on byte lanes without reordering them. The `HBIGENDIN` (AHB) or system-level big-endian signals determine how a component interprets those bytes. A BE8 (byte-invariant big-endian) configuration keeps bytes in their original positions but reinterprets word-level grouping — this differs from BE32 (word-invariant) which also reorders bytes within a word.

Most modern ARM SoCs run in little-endian mode throughout; big-endian is a configuration option rarely used in new designs.

## TLM-2.0 and Endianness

In a TLM-2.0 model, the generic payload carries raw bytes in a flat buffer. The byte at `data_ptr[0]` always maps to the lowest address of the transfer. The model does not inherently know the endianness of the initiator or the target — that knowledge lives in the initiator (when constructing the payload) and the target (when interpreting it).

A correct big-endian initiator writing `0xDEADBEEF` must place bytes in the buffer as:

```cpp
uint8_t buf[4] = { 0xDE, 0xAD, 0xBE, 0xEF };
trans.set_data_ptr(buf);
```

A little-endian initiator writing the same value places:

```cpp
uint8_t buf[4] = { 0xEF, 0xBE, 0xAD, 0xDE };
trans.set_data_ptr(buf);
```

A bus bridge model between the two must swap bytes in transit:

```cpp
void swap32(uint8_t *p) {
    uint8_t tmp = p[0]; p[0] = p[3]; p[3] = tmp;
    tmp = p[1]; p[1] = p[2]; p[2] = tmp;
}
```

## Network Peripherals (Ethernet, USB)

Network protocols use big-endian (network byte order) for multi-byte header fields. A 10/100 Ethernet MAC peripheral therefore expects the host to swap header fields before transmission. The Linux kernel macros `htonl`, `htons`, `ntohl`, `ntohs` handle this; in bare-metal firmware you must call the equivalent yourself or rely on the MAC's descriptor ring, which sometimes has a byte-swap option.

## Practical Checklist for TLM Bridge Models

- [ ] Identify the endianness of the initiator socket's native byte order.
- [ ] Identify the endianness of the target socket's native byte order.
- [ ] If they differ, implement a byte-swap in the `b_transport` pass-through.
- [ ] Verify with a known test vector (e.g., write `0x01020304`, read it back, confirm the correct value on each side).
- [ ] Check that byte enables are also adjusted — a byte enable array from a LE initiator refers to bytes in ascending address order, and that mapping is endianness-independent, but which physical byte lane each enable corresponds to depends on the bus width and endianness.

## Common Pitfalls

- Swapping bytes in the bridge when software already swapped them — double-swap produces the "correct" result in testing but hides the real bug.
- Forgetting that AMBA byte lane assignment (HADDR[1:0] × bus width) interacts with endianness for sub-word accesses.
- Assuming all USB or PCIe registers are big-endian — many modern PCIe endpoints are little-endian to ease integration with x86 hosts.

## Interview Answer

> "When a little-endian CPU communicates with a big-endian peripheral, bytes must be swapped at exactly one point in the path — either in software (using `htobe32`), in a hardware bus bridge, or in the peripheral itself. In TLM models, the payload buffer is always in ascending-address byte order, and a bridge module is responsible for reversing the byte order in its `b_transport` when the initiator and target endianness differ."
