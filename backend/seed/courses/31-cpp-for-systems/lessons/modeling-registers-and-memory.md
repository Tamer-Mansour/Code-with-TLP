# Modeling Registers, Memory, and Buses in C++

The three pillars of every virtual prototype are: a **register file** (CPU state), a **flat memory** (RAM/ROM), and a **bus** (address decoder that routes transactions). Getting these right unlocks everything else.

## Modeling a Register File

A CPU register file is simply an array of fixed-width integers. For a 32-bit RISC-V core:

```cpp
struct RegisterFile {
    uint32_t x[32] = {};   // x0 is hardwired to zero

    uint32_t read(int idx) const {
        return (idx == 0) ? 0u : x[idx];
    }

    void write(int idx, uint32_t val) {
        if (idx != 0) x[idx] = val;   // writes to x0 are silently discarded
    }
};
```

Key rule: **x0 is always zero**. Missing this produces subtle firmware bugs that are hard to trace.

## Modeling Flat Memory

RAM is a byte array with helpers for aligned 32-bit access:

```cpp
class Memory {
public:
    explicit Memory(std::size_t size) : data_(size, 0) {}

    uint32_t load32(uint32_t addr) const {
        check(addr, 4);
        uint32_t v;
        std::memcpy(&v, data_.data() + addr, 4);
        return v;  // host must be little-endian or you need bswap
    }

    void store32(uint32_t addr, uint32_t val) {
        check(addr, 4);
        std::memcpy(data_.data() + addr, &val, 4);
    }

private:
    std::vector<uint8_t> data_;

    void check(uint32_t addr, uint32_t sz) const {
        if (addr + sz > data_.size())
            throw std::out_of_range("memory access out of bounds");
    }
};
```

Use `std::memcpy` instead of pointer casts to avoid undefined behavior from strict-aliasing violations.

## Endianness

Most modern hosts and RISC-V targets are **little-endian**, so `memcpy` just works. If your target is big-endian (e.g., classic MIPS, PowerPC), add a byte-swap helper:

```cpp
inline uint32_t bswap32(uint32_t v) {
    return __builtin_bswap32(v);   // GCC/Clang intrinsic
    // or: ((v>>24)&0xFF)|((v>>8)&0xFF00)|((v<<8)&0xFF0000)|((v<<24)&0xFF000000)
}
```

Always document which side of the conversion each function expects — this is one of the most common VP bug categories.

## Modeling a Bus (Address Decoder)

A bus maps address ranges to devices. The simplest model is a sorted list of regions:

```cpp
struct Region {
    uint32_t base, size;
    Memory*  mem;   // or a Device* interface
};

class Bus {
public:
    void map(uint32_t base, uint32_t size, Memory* dev) {
        regions_.push_back({base, size, dev});
    }

    uint32_t read32(uint32_t addr) const {
        for (auto& r : regions_)
            if (addr >= r.base && addr < r.base + r.size)
                return r.mem->load32(addr - r.base);
        throw std::runtime_error("unmapped read @ " + std::to_string(addr));
    }

private:
    std::vector<Region> regions_;
};
```

For large address spaces, replace the linear scan with a sorted vector + `lower_bound` or a flat page table for O(1) lookup.

## Adding Control/Status Registers (CSRs)

Peripheral registers are not plain RAM — reads may have side effects (e.g., clearing an interrupt flag). Model them with a virtual interface:

```cpp
struct Device {
    virtual uint32_t read(uint32_t offset)           = 0;
    virtual void     write(uint32_t offset, uint32_t v) = 0;
    virtual ~Device() = default;
};
```

A UART peripheral then implements `Device`, mapping offset 0 to the transmit register, offset 4 to the status register, and so on.

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Pointer-cast aliasing (UB) | Use `memcpy` or `std::bit_cast` (C++20) |
| Forgetting x0 == 0 | Guard in `read()` and `write()` |
| Overlapping bus regions | Assert no overlap during `map()` |
| Unaligned accesses silently misread | Check alignment in load/store |

## Interview Takeaway

> **Interview answer:** "I model registers as a fixed-width array with a zero-register guard, memory as a byte vector with memcpy-based accessors to avoid aliasing UB, and the bus as a region list that dispatches reads/writes to the correct device — throwing on unmapped addresses so bugs surface immediately."
