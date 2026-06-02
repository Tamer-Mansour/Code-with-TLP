# Designing Abstract Base Classes for Drivers

In systems and OS programming, **hardware drivers** are the canonical example where abstract base class design pays off directly. A well-designed base class lets kernel code interact with any peripheral — UART, SPI, I2C, GPIO — through a single stable interface, while concrete drivers handle hardware-specific details.

## The Design Goals

1. **Stable interface** — kernel/middleware code never changes when a new driver is added.
2. **Enforced contract** — every driver must implement required operations.
3. **Shared plumbing** — common bookkeeping (state tracking, error counts) lives in the base.
4. **Zero-overhead where possible** — base-class virtuals cost one vtable lookup per call, which is acceptable for I/O-bound operations.

## A Worked Example: `BlockDevice`

```cpp
#include <cstddef>
#include <cstdint>
#include <string>

class BlockDevice {
public:
    // ----- Contract: every concrete driver MUST implement these -----
    virtual int   open()                                          = 0;
    virtual int   close()                                         = 0;
    virtual int   read (uint64_t lba, void* buf, std::size_t n)  = 0;
    virtual int   write(uint64_t lba, const void* buf, std::size_t n) = 0;
    virtual int   flush()                                         = 0;
    virtual uint64_t capacity_bytes() const                       = 0;

    // ----- Shared helpers: implemented once in the base -----
    const std::string& name()  const { return name_; }
    bool               is_open() const { return open_; }
    uint32_t           error_count() const { return error_count_; }

    // Convenience: read/write full sectors
    int read_sector (uint64_t lba, void* buf) {
        return read(lba, buf, sector_size_);
    }
    int write_sector(uint64_t lba, const void* buf) {
        return write(lba, buf, sector_size_);
    }

    virtual ~BlockDevice() = default;

protected:
    explicit BlockDevice(std::string name, std::size_t sector_size = 512)
        : name_(std::move(name)), sector_size_(sector_size) {}

    void record_error() { ++error_count_; }
    void set_open(bool v) { open_ = v; }

private:
    std::string  name_;
    std::size_t  sector_size_;
    bool         open_        = false;
    uint32_t     error_count_ = 0;
};
```

## Concrete Driver: NVMe

```cpp
class NvmeDevice : public BlockDevice {
    int      namespace_id_;
    uint64_t capacity_;
public:
    NvmeDevice(std::string name, int nsid, uint64_t cap)
        : BlockDevice(std::move(name), 4096), namespace_id_(nsid), capacity_(cap) {}

    int open() override {
        set_open(true);
        return 0;   // initialize NVMe controller
    }
    int close() override { set_open(false); return 0; }

    int read(uint64_t lba, void* buf, std::size_t n) override {
        if (!is_open()) return -1;
        // submit NVMe read command …
        return static_cast<int>(n);
    }
    int write(uint64_t lba, const void* buf, std::size_t n) override {
        if (!is_open()) { record_error(); return -1; }
        // submit NVMe write command …
        return static_cast<int>(n);
    }
    int flush() override { return 0; }
    uint64_t capacity_bytes() const override { return capacity_; }
};
```

## Kernel Code: Talks Only to `BlockDevice*`

```cpp
void format_device(BlockDevice* dev) {
    if (dev->open() < 0) return;
    // Wipe the first sector
    char zeroes[4096] = {};
    dev->write_sector(0, zeroes);
    dev->flush();
    dev->close();
}

// Works with ANY driver:
NvmeDevice nvme("nvme0", 1, 512ULL << 30);
format_device(&nvme);
```

## Design Checklist for Abstract Driver Classes

| Question | Guidance |
|----------|----------|
| Which operations must ALL drivers support? | Make pure virtual |
| Which operations have a sensible default? | Make non-pure virtual with a default body |
| Which operations are invariants/helpers? | Make non-virtual in the base |
| Is there shared state (error count, name)? | Private data in base, accessed via protected setters |
| Memory ownership: stack, heap, or `unique_ptr`? | Prefer `unique_ptr<BlockDevice>` for heap |

## Common Pitfalls in Driver ABCs

- **Too many pure virtuals.** If most drivers implement `ioctl` identically, give it a non-pure default.
- **Public data members in the base.** Use private data with protected accessors to keep the invariant inside the base.
- **Forgetting `virtual ~BlockDevice()`** — the kernel will `delete` drivers through `BlockDevice*` pointers.
- **Platform-specific types leaking into the ABC.** Keep the interface in terms of `uint64_t`, `std::size_t`, and standard types — not kernel-internal structs.

> **Interview answer:** Design an abstract driver base class by identifying the minimal set of operations every concrete driver must implement (pure virtual), placing shared bookkeeping in private base-class data, and providing convenience helpers as non-virtual methods — so the kernel depends only on the stable base-class interface.
