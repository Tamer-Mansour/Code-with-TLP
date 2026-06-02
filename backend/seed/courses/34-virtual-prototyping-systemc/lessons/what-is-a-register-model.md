# What Is a Register Model?

A **register model** is the structured software representation of a peripheral's memory-mapped register space. It captures not just the raw storage but also the access rules, reset values, bit-field layout, and behavioral side effects associated with every register the hardware exposes.

## Registers vs. Plain Memory

It is tempting to model a peripheral's registers as a flat byte array, but hardware registers differ from ordinary RAM in important ways:

| Property | Plain RAM | Hardware Register |
|----------|-----------|-------------------|
| Read always returns last written value | Yes | Not necessarily (e.g., RC clears on read) |
| Write stores the value verbatim | Yes | Not necessarily (e.g., W1C ignores written 0s) |
| Access has no side effect | Yes | Usually has side effects |
| Reset value | Undefined | Specified in datasheet |
| Bit-level access semantics | Uniform | Per-field (RO, RW, W1C …) |

A proper register model encodes all of these distinctions explicitly.

## Anatomy of a Register Model

A well-designed register model typically has three layers:

1. **Register descriptor** — metadata: name, offset, reset value, access type.
2. **Bit-field descriptors** — for each field: bit range, access type, reset value, description.
3. **Access handlers** — functions called on read or write that implement side effects.

```cpp
struct RegField {
    std::string name;
    uint32_t    mask;      // bitmask within the 32-bit register word
    uint32_t    shift;     // LSB position
    AccessType  access;    // RO, RW, W1C, RC, WO …
    uint32_t    reset_val; // value after hardware reset
};

struct Register {
    std::string          name;
    uint32_t             offset;
    uint32_t             reset_val;
    uint32_t             value;       // current hardware value
    std::vector<RegField> fields;

    void reset() { value = reset_val; }
};
```

## Building a Register Bank

A peripheral typically exposes several registers at consecutive or sparse offsets. A register bank maps offsets to `Register` objects and routes TLM transactions to the correct entry.

```cpp
class RegisterBank {
    std::map<uint32_t, Register> bank_;
public:
    void add(Register r) { bank_[r.offset] = r; }

    uint32_t read(uint32_t offset) {
        auto it = bank_.find(offset);
        if (it == bank_.end()) return 0xDEADBEEF; // unmapped
        return it->second.on_read();
    }

    void write(uint32_t offset, uint32_t data) {
        auto it = bank_.find(offset);
        if (it != bank_.end()) it->second.on_write(data);
    }
};
```

## Reset Values Matter

Every register in a real device powers up to a documented reset value. The model must reproduce this so that firmware that checks reset defaults works correctly.

```cpp
// Populate a UART Line Control Register
Register lcr;
lcr.name      = "LCR";
lcr.offset    = 0x0C;
lcr.reset_val = 0x00000003;  // 8-bit word length by default
lcr.reset();
```

Forgetting to call `reset()` — or initialising with zero when the reset value is non-zero — is a silent correctness bug that causes firmware initialisation code to malfunction.

## Self-Describing Register Maps

Production-quality models make the register map machine-readable. The UVM Register Abstraction Layer (RAL) and IP-XACT are industry-standard formats that describe registers in XML or a domain-specific language, from which C++ model code is auto-generated. Even without those tools, keeping an explicit struct per register (rather than a raw array) makes the model self-documenting.

## Common Pitfalls

- **Treating all bits as RW.** Real registers have read-only status bits, write-only command bits, and mixed access fields. Collapsing them to a single RW value breaks firmware that relies on the correct semantics.
- **Aliased registers.** Some peripherals map the same hardware resource to different offsets depending on whether you read or write. A naive array misses the aliasing entirely.
- **Forgetting reserved bits.** The datasheet often says reserved bits must be written as zero and may read back as one. The model should enforce the write mask and return the documented read value.

## Worked Example: UART Control Register Decode

```cpp
// Firmware writes 0x00000061 to UART_CR (offset 0x30)
// Bit layout: [7:6]=parity(01=odd), [5]=stop_bits(1=2-stop),
//             [1:0]=word_len(01=7-bit)
void UartModel::on_cr_write(uint32_t val) {
    uint32_t parity    = (val >> 6) & 0x3;
    uint32_t stop_bits = (val >> 5) & 0x1;
    uint32_t word_len  = (val >> 0) & 0x3;
    apply_uart_config(parity, stop_bits, word_len);
    regs_[CR_OFFSET] = val & CR_WRITE_MASK; // mask reserved bits
}
```

> **Interview answer:** A register model encodes a peripheral's register map with correct reset values, per-field access semantics, and side-effect callbacks — it is the behavioral contract between hardware and the firmware that programs it.
