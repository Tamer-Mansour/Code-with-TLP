# Base + Offset Address Translation

Address translation converts a **system-level (physical) address** into a **target-local offset** that the memory model uses to index its internal storage. This is the arithmetic that every router, bridge, and interconnect performs on every transaction.

## The Core Formula

```
offset = system_address - region_base
```

If a transaction arrives at system address `0x2000_1A34` and the SRAM region starts at `0x2000_0000`, the offset is:

```
offset = 0x2000_1A34 - 0x2000_0000 = 0x0000_1A34
```

The memory model indexes `storage[0x1A34]`. It knows nothing about system addresses — it only sees offsets from zero.

## Why Translation Matters

Without translation, a 128 KB SRAM model allocated from `0x2000_0000` to `0x2001_FFFF` would need a `storage` array of 537 MB to hold indices up to `0x2001_FFFF`. Translation collapses that to a 128 KB array.

## Worked Example — Full Decode Chain

Suppose the address map is:

```
Flash:  base=0x0800_0000, size=0x0008_0000  (512 KB)
SRAM:   base=0x2000_0000, size=0x0002_0000  (128 KB)
GPIOA:  base=0x4002_3800, size=0x0000_0400  (1 KB)
```

The CPU issues a 4-byte write to `0x2000_0040`:

```
1. Router receives address 0x2000_0040
2. Is 0x2000_0040 in Flash?   0x0800_0000 <= 0x2000_0040 < 0x0808_0000 → No
3. Is 0x2000_0040 in SRAM?    0x2000_0000 <= 0x2000_0040 < 0x2002_0000 → Yes
4. offset = 0x2000_0040 - 0x2000_0000 = 0x40
5. txn.set_address(0x40)
6. Forward to SRAM model
7. SRAM model copies 4 bytes to storage[0x40..0x43]
```

## Bit-Mask Variant

Hardware decoders often use AND/compare patterns. For a power-of-two region of size `S`:

```cpp
constexpr uint64_t BASE = 0x2000'0000;
constexpr uint64_t MASK = 0x0001'FFFF;  // size - 1 = 128 KB - 1

// Decode: check top bits match, then extract offset
if ((addr & ~MASK) == BASE) {
    uint64_t offset = addr & MASK;
    // forward with offset
}
```

This is equivalent to the subtraction method when `BASE` is aligned to `S`.

## Bridge Translation — Adding a Bias

A bridge (interconnect between two buses at different address bases) may need to **add** a bias, not just subtract:

```
target_address = source_address - source_base + target_base
```

Example: a PCIe bridge maps CPU addresses `0xC000_0000–0xCFFF_FFFF` to PCIe BAR space `0x0000_0000–0x0FFF_FFFF`:

```
target = 0xC123_4567 - 0xC000_0000 + 0x0000_0000 = 0x0123_4567
```

If the PCIe device's BAR is itself at offset `0x1000_0000` in its own space:

```
target = 0xC123_4567 - 0xC000_0000 + 0x1000_0000 = 0x1123_4567
```

## Validation — Checking the Offset Is In-Range

After computing the offset, always validate it before indexing:

```cpp
uint64_t sys_addr = txn.get_address();
uint64_t offset   = sys_addr - REGION_BASE;

if (offset + txn.get_data_length() > REGION_SIZE) {
    txn.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
    return;
}
// safe to use storage[offset]
```

The check must include `data_length` to catch accesses that start inside the region but extend past its end — a subtle bug that only appears with word-aligned accesses near the boundary.

## Summary

| Step | Formula |
|---|---|
| Compute offset | `offset = addr - base` |
| Validate | `offset + len <= size` |
| Bridge add bias | `target = addr - src_base + tgt_base` |
| Mask form | `offset = addr & (size - 1)` (power-of-two only) |

## Interview Answer

> "The router subtracts the region's base address from the incoming system address to produce a target-local offset, then calls `txn.set_address(offset)` before forwarding. The target's storage is indexed by offset, so it only needs to be as large as the region itself."
