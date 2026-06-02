# Sparse and Backed Memory Models

A flat `std::vector<uint8_t>` works perfectly for 128 KB of SRAM. It does not work for a 4 GB DRAM region or a 64-bit address space where the actual footprint is tiny — allocating the full range is impossible. The solution is a **sparse memory model**.

## What Is Sparse Memory?

A sparse memory model only allocates storage for pages that are actually written. All other pages return a default value (typically `0x00`) on read without using any RAM. This is exactly how a host OS implements virtual memory through demand paging.

## Hash-Map Implementation

The most common approach is a hash map keyed on page number:

```cpp
#include <unordered_map>
#include <cstring>
#include <cstdint>

class SparseMemory {
public:
    static constexpr size_t PAGE_SIZE = 4096;  // 4 KB pages

    uint8_t read_byte(uint64_t addr) const {
        uint64_t page = addr / PAGE_SIZE;
        auto it = pages.find(page);
        if (it == pages.end()) return 0x00;    // unwritten page → zero
        return it->second[addr % PAGE_SIZE];
    }

    void write_byte(uint64_t addr, uint8_t val) {
        uint64_t page   = addr / PAGE_SIZE;
        size_t   offset = addr % PAGE_SIZE;
        auto& p = pages[page];                  // creates page on first write
        if (p.empty()) p.resize(PAGE_SIZE, 0);
        p[offset] = val;
    }

private:
    std::unordered_map<uint64_t, std::vector<uint8_t>> pages;
};
```

For bulk transfers, extend this to copy across page boundaries by splitting the transfer at each page boundary.

## Page Size Trade-offs

| Page size | Pros | Cons |
|---|---|---|
| 64 B | Minimal over-allocation | High hash-map overhead for sequential writes |
| 4 KB | Matches host OS pages, good cache locality | 4 KB wasted per touched region |
| 64 KB | Fast bulk init | Large waste if only a few bytes written |

4 KB is the most common choice because it matches the host MMU page size, giving good TLB behavior.

## Backed Memory — Loading from a File

A **backed** memory model loads its initial contents from an external source — a binary image, an ELF segment, or a hex file — then behaves like normal RAM for subsequent accesses:

```cpp
void load_binary(const std::string& path, uint64_t load_addr) {
    std::ifstream f(path, std::ios::binary);
    char byte;
    uint64_t addr = load_addr;
    while (f.get(byte))
        write_byte(addr++, static_cast<uint8_t>(byte));
}
```

This is how a virtual prototype loads firmware into Flash before reset is released. The loader writes the image into the sparse backing store; subsequent instruction fetches read from the same backing store.

## Copy-on-Write Backing

A more memory-efficient variant keeps the loaded image in a read-only buffer and only allocates writable pages when the first write occurs. This is analogous to mmap with `MAP_PRIVATE`:

```cpp
uint8_t read_byte(uint64_t addr) const {
    // check writable overlay first
    auto it = dirty_pages.find(addr / PAGE_SIZE);
    if (it != dirty_pages.end())
        return it->second[addr % PAGE_SIZE];
    // fall back to read-only image
    if (addr < image.size()) return image[addr];
    return 0x00;
}
```

This is valuable for Flash regions in SoC models where the firmware image is large but rarely modified during simulation.

## When to Use Each Model

| Scenario | Recommended model |
|---|---|
| Small, fully-populated SRAM | `std::vector<uint8_t>` |
| Large or sparse DRAM (> 64 MB) | Hash-map sparse model |
| Firmware Flash (read-mostly) | Backed with copy-on-write |
| 64-bit address space exploration | Sparse with 4 KB pages |

## Interview Answer

> "A sparse memory model uses a hash map keyed on page number. Unwritten pages return zero on read with no allocation. The first write to a page allocates it. This makes it practical to model gigabyte address spaces without exhausting host RAM."
