# Configurable and Parameterized Platforms

Hard-coding addresses, sizes, and frequencies makes a VP brittle. A well-designed VP uses configuration so the same model can represent a chip family — different SKUs share the same code base with different parameter files.

## Why Configurability Matters

- **Chip families** — Cortex-M33 with 256 KB vs 512 KB flash differ only in `ROM_SIZE`.
- **Regression suites** — tests run with different clock speeds to flush timing bugs.
- **Customer deliveries** — the vendor ships a VP; the customer configures it for their board.

## Parameterization Approaches

### 1. Constructor Arguments (compile-time flexibility)

```cpp
struct PlatformConfig {
    uint64_t    rom_base  = 0x00000000;
    uint32_t    rom_size  = 64 * 1024;
    uint64_t    ram_base  = 0x20000000;
    uint32_t    ram_size  = 128 * 1024;
    double      cpu_freq  = 48e6;
};

int sc_main(int argc, char *argv[]) {
    PlatformConfig cfg;
    RomModel rom("rom", cfg.rom_base, cfg.rom_size);
    // ...
}
```

### 2. JSON / INI Configuration File (runtime flexibility)

```json
{
  "rom_base":  "0x00000000",
  "rom_size":  65536,
  "ram_base":  "0x20000000",
  "ram_size":  131072,
  "cpu_freq":  48000000,
  "uart_base": "0x40000000"
}
```

```cpp
PlatformConfig cfg = load_config("platform.json");
```

Parsing the config file before Phase 1 of `sc_main` keeps the wiring section clean.

### 3. SystemC `sc_attribute` / CCI (Configuration, Control, Inspection)

The OSCI Configuration standard (CCI) lets tools query and set parameters through a broker without touching source code. This is the industry-standard approach for large VPs delivered to third parties.

```cpp
// Inside a module
cci::cci_param<uint32_t> ram_size{"ram_size", 131072, "RAM size in bytes"};
```

A GUI or script can then override `ram_size` before elaboration begins.

## Template Parameters for Zero-Cost Abstraction

When the bus width is known at compile time, use a template:

```cpp
template <unsigned BUS_WIDTH = 32>
class MemoryModel : public sc_core::sc_module {
    uint8_t mem[1 << BUS_WIDTH]; // statically sized
    // ...
};
```

This avoids runtime branching for the common case.

## Parameterized Address Map Table

Store the decode table externally:

```cpp
struct MapEntry { std::string name; uint64_t base; uint32_t size; };

std::vector<MapEntry> address_map = {
    {"rom",  0x00000000, 64*1024},
    {"ram",  0x20000000, 128*1024},
    {"uart", 0x40000000, 4096},
};
```

The bus constructor iterates this table to register targets. Adding a new peripheral means appending one row — no recompilation needed.

## Pitfalls

- **Overlapping ranges after resize** — if `rom_size` is changed carelessly it may overlap with RAM. Validate ranges at startup:

```cpp
for (size_t i = 0; i < address_map.size(); ++i)
    for (size_t j = i + 1; j < address_map.size(); ++j)
        assert(no_overlap(address_map[i], address_map[j]));
```

- **Circular dependencies** — config object must be fully parsed before any module constructor runs. Construct the config struct first.
- **Magic numbers** — never write `0x40000000` directly in binding code; always reference a named constant or config field.

## Worked Example: Dual-SKU Platform

```cpp
PlatformConfig sku_a = {.rom_size = 64*1024,  .ram_size = 128*1024};
PlatformConfig sku_b = {.rom_size = 128*1024, .ram_size = 256*1024};

PlatformConfig cfg = (argv[1] == std::string("SKU_B")) ? sku_b : sku_a;
```

One binary, two products.

**Interview answer:** A parameterized VP uses a config struct or CCI parameters to control memory sizes, base addresses, and clock frequencies. This lets a single code base represent a chip family — each SKU is just a different configuration file. Ranges must be validated at startup to catch overlaps introduced by resizing.
