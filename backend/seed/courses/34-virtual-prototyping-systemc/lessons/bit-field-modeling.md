# Modeling Register Bit Fields

A 32-bit register is rarely treated as a monolithic value. Hardware designers carve it into **bit fields** — contiguous groups of bits that each have an independent meaning, access type, and reset value. Modeling these fields explicitly is what separates a robust peripheral model from a fragile byte-array hack.

## Why Explicit Bit-Field Modeling?

- **Correctness** — different fields in the same register may have different access types (some RO, some RW, some W1C). A monolithic write handler cannot distinguish them.
- **Maintainability** — when the datasheet changes a field definition, you change one descriptor, not scattered bitmask constants.
- **Debug visibility** — a self-describing field struct can print its name and current value in simulation logs, making traces human-readable.

## Representing a Bit Field in C++

The minimal representation needs four things: the mask, the shift, the access type, and the reset value.

```cpp
enum class AccessType { RO, RW, W1C, RC, WO };

struct BitField {
    std::string name;
    uint32_t    shift;      // LSB position (0–31)
    uint32_t    width;      // number of bits
    AccessType  access;
    uint32_t    reset_val;  // field value (not register value) after reset

    uint32_t mask() const { return ((1u << width) - 1u) << shift; }

    uint32_t extract(uint32_t reg) const {
        return (reg & mask()) >> shift;
    }

    uint32_t insert(uint32_t reg, uint32_t field_val) const {
        return (reg & ~mask()) | ((field_val << shift) & mask());
    }
};
```

## Applying Field Access Rules During a Write

When firmware writes a value to a register, the model must apply each field's access rule independently:

```cpp
uint32_t Register::apply_write(uint32_t current, uint32_t written) {
    uint32_t result = current;
    for (const auto& f : fields) {
        switch (f.access) {
            case AccessType::RW:
                result = f.insert(result, f.extract(written));
                break;
            case AccessType::W1C:
                // clear bits where software writes 1
                result &= ~(written & f.mask());
                break;
            case AccessType::RO:
            case AccessType::RC:
                // ignore write — hardware owns this field
                break;
            case AccessType::WO:
                // write accepted but not readable
                result = f.insert(result, f.extract(written));
                break;
        }
    }
    return result;
}
```

## Worked Example: UART Line Control Register

| Bits | Field | Access | Reset | Description |
|------|-------|--------|-------|-------------|
| 31:8 | Reserved | RO | 0 | Must read as 0 |
| 7 | DLAB | RW | 0 | Divisor Latch Access Bit |
| 6 | BRK | RW | 0 | Set break condition |
| 5:3 | PARITY | RW | 0 | Parity mode |
| 2 | STOP | RW | 0 | Stop bits (0=1, 1=2) |
| 1:0 | WORD_LEN | RW | 3 | 0=5-bit … 3=8-bit |

```cpp
// Build the LCR register descriptor
Register lcr;
lcr.name      = "LCR";
lcr.offset    = 0x0C;
lcr.reset_val = 0x00000003;  // WORD_LEN=3 (8-bit) at reset

lcr.fields = {
    {"WORD_LEN", 0, 2, AccessType::RW, 3},
    {"STOP",     2, 1, AccessType::RW, 0},
    {"PARITY",   3, 3, AccessType::RW, 0},
    {"BRK",      6, 1, AccessType::RW, 0},
    {"DLAB",     7, 1, AccessType::RW, 0},
};
```

Firmware writing `0x83` (binary `10000011`) to LCR should set DLAB=1 and WORD_LEN=3, leaving others unchanged. The `apply_write` function above handles this correctly field by field.

## Using C++ Bit-Field Structs (with Caveats)

C++ offers a built-in syntax for bit fields:

```cpp
union LCR_t {
    struct {
        uint32_t WORD_LEN : 2;
        uint32_t STOP     : 1;
        uint32_t PARITY   : 3;
        uint32_t BRK      : 1;
        uint32_t DLAB     : 1;
        uint32_t reserved : 24;
    };
    uint32_t raw;
};
```

This is convenient for reading field values but **dangerous for a register model** because:
- Bit ordering is implementation-defined (compiler-dependent).
- It cannot encode per-field access types or side effects.
- Endianness mismatches cause silent bugs on cross-compilation.

Use the struct syntax for quick internal state; use the explicit `BitField` descriptor approach for the authoritative model.

## Common Pitfalls

- **Width-1 field mask overflow** — `(1u << 32) - 1` is undefined behaviour in C++. Guard against zero-width and 32-bit-wide fields specially.
- **Forgetting to mask before shift** — always apply the field mask after shifting to avoid sign extension corrupting neighbouring fields.
- **Skipping reserved fields** — reserved bits should be modeled as RO with their documented read value (often 0, sometimes 1).

> **Interview answer:** Explicit bit-field modeling encodes each field's mask, shift, access type, and reset value as data, allowing the register's write handler to apply the correct rule per field rather than treating the entire register as uniform read/write storage.
