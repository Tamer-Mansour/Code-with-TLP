# Aliasing and Memory Mirrors

**Aliasing** occurs when two or more different addresses map to the same physical storage. **Mirroring** is a specific, intentional form of aliasing where a region is repeated at regular intervals. Both concepts appear frequently in real SoC address maps and must be faithfully modelled in a virtual prototype.

## Why Aliasing Exists in Hardware

Hardware decoders sometimes use only a subset of address bits. If a peripheral only decodes bits `[11:0]` of the address bus and ignores bits `[31:12]`, then addresses `0x4000_0000`, `0x4000_1000`, `0x4001_0000` all reach the same register — they are aliases of each other.

This is not a bug in the original hardware; it was a deliberate cost-saving choice in the address decoder. However, firmware that depends on aliases is non-portable and considered a defect by MISRA-C.

## Mirroring — Intentional Repetition

Many Cortex-M chips mirror Flash at address `0x0000_0000` in addition to its native address (e.g., `0x0800_0000`) to support the boot-from-Flash option. After reset the CPU fetches from `0x0000_0000`; by mirroring Flash there, no code changes are needed for different boot modes.

```
0x0000_0000 - 0x0007_FFFF  →  Mirror of Flash (same physical storage)
0x0800_0000 - 0x0807_FFFF  →  Flash (primary location)
```

A write to `0x0800_0010` and a read from `0x0000_0010` return the same byte.

## Modelling Aliases in TLM

The cleanest TLM approach is to register the same target under multiple address map entries in the router. The target receives an offset relative to whichever base matched:

```cpp
// Register Flash at two bases
map.push_back({ 0x0000'0000, FLASH_SIZE, &flash.socket });
map.push_back({ 0x0800'0000, FLASH_SIZE, &flash.socket });
```

Because the router subtracts the matched base before forwarding, both entries produce the same offset range `[0, FLASH_SIZE)` at the Flash target. The Flash model sees no difference — aliasing is handled entirely in the router.

## Modulo Mirroring

Some peripherals mirror themselves every power-of-two bytes. A 1 KB peripheral register block mirrored in a 4 KB region repeats four times:

```
Offset 0x000 - 0x3FF  → real registers
Offset 0x400 - 0x7FF  → mirror of 0x000 - 0x3FF
Offset 0x800 - 0xBFF  → mirror of 0x000 - 0x3FF
Offset 0xC00 - 0xFFF  → mirror of 0x000 - 0x3FF
```

Implement with the modulo operator in the target:

```cpp
void b_transport(tlm::tlm_generic_payload& txn, sc_core::sc_time& delay) {
    uint64_t addr   = txn.get_address();
    uint64_t offset = addr % REAL_REGISTER_SIZE;  // fold mirrors
    dispatch_register(offset, txn);
}
```

## Aliasing vs. Caching — A Critical Distinction

When a CPU cache is present, aliased addresses create a **cache coherency problem**. The cache uses the address as its key; if firmware writes via one alias and reads via another, the cache may serve stale data. Virtual prototypes that model caches must track all aliases of a line and invalidate them all on a write.

## Common Pitfalls

- **Forgetting to model the mirror**: Firmware that boots from `0x0000_0000` crashes in simulation because the mirror is absent, even though Flash at `0x0800_0000` works fine.
- **Alias used for peripheral reset**: Some chips clear a peripheral by writing to an alias that has a "clear on write" semantic. Treating all aliases as identical ignores this.
- **Aliased DMA descriptors**: A DMA engine may access memory through a physically-aliased window that bypasses the cache. Failure to alias in simulation gives wrong DMA results.

## Interview Answer

> "Aliasing maps multiple addresses to the same storage. In TLM, the router registers the same target socket under multiple base addresses; offset subtraction handles the translation. Modulo mirroring is implemented with `offset % real_size` inside the target, collapsing repeated regions to the same register set."
