# Loading Boot Images into Model Memory

Before the simulated CPU can execute firmware, the binary images (Boot ROM, bootloader, kernel, DTB, initrd) must be present in the VP's memory models. How and when these images are loaded significantly affects simulation startup time, debuggability, and fidelity.

## Two Loading Strategies

### 1. Pre-Loading at Elaboration Time

The host platform code loads all binaries into memory models before `sc_start()` is called. This is the most common approach for bring-up VPs:

```cpp
void Platform::end_of_elaboration() {
    // Load Boot ROM content
    boot_rom.load_binary("boot_rom.bin", 0x0000'0000);

    // Pre-load stages into DRAM (skips storage simulation)
    dram.load_binary("u-boot.bin",  0x0200'0000);
    dram.load_binary("Image",       0x4000'0000);
    dram.load_binary("vp.dtb",      0x4FA0'0000);
    dram.load_binary("initrd.img",  0x5000'0000);
}
```

**Pros:** Fast startup, no storage peripheral models needed, easy to swap images.  
**Cons:** Does not validate the storage read path; storage peripheral bugs go undetected.

### 2. Simulated Storage Loading

The CPU model executes actual bootloader code that reads from a modeled storage device (eMMC, QSPI NOR). The storage model serves data from a host-side image file:

```cpp
void QspiModel::b_transport(tlm::tlm_generic_payload& gp,
                            sc_core::sc_time& delay) {
    uint64_t offset = gp.get_address() - QSPI_BASE;
    // Map to flash image file on host
    std::memcpy(gp.get_data_ptr(),
                &m_flash_image[offset],
                gp.get_data_length());
    gp.set_response_status(tlm::TLM_OK_RESPONSE);
    // Add realistic latency for storage access
    delay += sc_core::sc_time(100, SC_NS);
}
```

**Pros:** Full validation of storage driver and boot ROM storage-read code path.  
**Cons:** Slower simulation; requires accurate storage peripheral model.

## The `load_binary` Helper

Every VP platform should provide a generic binary loader utility:

```cpp
void MemoryModel::load_binary(const std::string& path,
                              uint64_t load_address) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) {
        SC_REPORT_FATAL(name(),
            ("Cannot open image: " + path).c_str());
    }
    size_t size = f.tellg();
    f.seekg(0);

    uint64_t offset = load_address - m_base_address;
    if (offset + size > m_data.size()) {
        SC_REPORT_FATAL(name(), "Image does not fit in memory region");
    }
    f.read(reinterpret_cast<char*>(&m_data[offset]), size);
    SC_REPORT_INFO(name(),
        ("Loaded " + path + " (" + std::to_string(size) +
         " bytes) at 0x" + std::to_string(load_address)).c_str());
}
```

## ELF vs. Raw Binary Loading

Kernel images on ARM are raw binary (the `Image` file). Bootloaders and firmware may be either raw binary or ELF. For ELF files, use an ELF loader that reads the program headers:

```cpp
void load_elf(const std::string& path, MemoryModel& mem) {
    // Parse ELF program headers
    // For each LOAD segment:
    //   mem.write(segment.p_paddr, segment.data, segment.p_filesz);
    //   mem.zero(segment.p_paddr + segment.p_filesz,
    //            segment.p_memsz - segment.p_filesz); // BSS
}
```

ELF loading also gives you the **entry point address**, which is useful when you want to pre-set the CPU's PC for a specific stage (e.g., skipping the Boot ROM entirely).

## Image Layout in DRAM

Maintaining a clear memory map prevents collisions between images:

| Image | Base Address | Max Size | Notes |
|---|---|---|---|
| U-Boot | `0x0200_0000` | 2 MB | Relocates to top of DRAM |
| Kernel (Image) | `0x4000_0000` | 32 MB | Uncompressed ARM64 kernel |
| DTB | `0x4FA0_0000` | 256 KB | Must not overlap kernel |
| Initrd | `0x5000_0000` | variable | Passed to kernel via DTB |

## Common Pitfalls

- **Image loaded at wrong address**: A kernel loaded at `0x4000_1000` instead of `0x4000_0000` will crash at the very first branch. Always double-check the load address against U-Boot's `bootm`/`booti` command arguments.
- **File not found at simulation start**: Use absolute paths or a configuration variable, not relative paths that depend on the working directory.
- **BSS segment not zeroed**: ELF BSS sections must be explicitly zeroed; if the memory model returns random data for uninitialized regions, C global variables start with garbage values.
- **Initrd address in DTB not updated**: If you change the initrd load address, you must recompile the DTB or use U-Boot to patch it at runtime with `fdt addr` and `fdt set /chosen linux,initrd-start`.
