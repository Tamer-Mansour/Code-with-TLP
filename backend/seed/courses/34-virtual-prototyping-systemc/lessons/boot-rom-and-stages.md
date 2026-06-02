# Boot ROM and Multi-Stage Boot

Modern SoCs do not jump directly from reset to an operating system. Instead, they use a **multi-stage boot** process where each stage is responsible for a limited task and loads the next stage. The Boot ROM is the immutable first stage — burned into silicon and the root of the hardware trust chain.

## What the Boot ROM Does

The Boot ROM is a small, read-only memory that contains the SoC vendor's first-stage code. Its responsibilities are minimal but critical:

- Verify the integrity (and optionally the signature) of the next boot stage
- Initialize the bare minimum hardware: PLL clock, pin mux, possibly DRAM training
- Load the next stage from a boot medium (eMMC, QSPI NOR, SD card, USB)
- Jump to the loaded stage

**Interview answer:** The Boot ROM is immutable first-stage code stored in on-chip ROM; in a VP it is modeled as a read-only memory initialized from a binary file, with the CPU fetching from it at the reset vector.

## Modeling Boot ROM in SystemC/TLM

The Boot ROM model is a passive TLM target. It loads its content from a binary file at elaboration time:

```cpp
SC_MODULE(BootRom) {
    tlm_utils::simple_target_socket<BootRom> socket;
    std::vector<uint8_t> m_data;

    BootRom(sc_module_name name, const std::string& rom_file,
            size_t rom_size)
        : sc_module(name), m_data(rom_size, 0xFF) {
        socket.register_b_transport(this, &BootRom::b_transport);
        load(rom_file);
    }

    void load(const std::string& path) {
        std::ifstream f(path, std::ios::binary);
        if (!f) SC_REPORT_FATAL("BootRom", "Cannot open ROM file");
        f.read(reinterpret_cast<char*>(m_data.data()), m_data.size());
    }

    void b_transport(tlm::tlm_generic_payload& gp,
                     sc_core::sc_time& delay) {
        if (gp.get_command() == tlm::TLM_WRITE_COMMAND) {
            gp.set_response_status(tlm::TLM_COMMAND_ERROR_RESPONSE);
            return; // ROM is read-only
        }
        uint64_t offset = gp.get_address();
        std::memcpy(gp.get_data_ptr(), &m_data[offset],
                    gp.get_data_length());
        gp.set_response_status(tlm::TLM_OK_RESPONSE);
    }
};
```

## Multi-Stage Boot Sequence

A typical ARM SoC (e.g., based on TF-A + U-Boot) has these stages:

```
Stage 0  Boot ROM (on-chip)
   |      - Minimal HW init
   |      - Loads BL2 from storage
   v
Stage 1  BL2 / SPL (Secondary Program Loader)
   |      - DRAM initialization
   |      - Loads BL31 (EL3 runtime) + BL33 (U-Boot)
   v
Stage 2  BL31 – EL3 Runtime Firmware (ARM Trusted Firmware)
   |      - Sets up secure world, PSCI
   v
Stage 3  U-Boot (BL33, runs at EL2 or EL1)
   |      - Full peripheral init
   |      - Loads kernel + device tree blob (DTB)
   v
Stage 4  Linux Kernel
```

Each stage lives at a specific load address. The VP's memory map must accommodate all of them simultaneously or at the right times.

## Modeling Stage Transitions

The handoff between stages is usually a simple branch instruction. The VP doesn't need special modeling for this — the CPU ISS handles it naturally. What matters is that each stage's binary is loaded into the correct memory region.

For a loosely timed VP, you can pre-load all stages into DRAM at `start_of_simulation()` rather than simulating the storage-read:

```cpp
void Platform::load_images() {
    load_file("bl2.bin",    dram, BL2_LOAD_ADDR);
    load_file("bl31.bin",   dram, BL31_LOAD_ADDR);
    load_file("u-boot.bin", dram, UBOOT_LOAD_ADDR);
    load_file("Image",      dram, KERNEL_LOAD_ADDR);
    load_file("fdt.dtb",    dram, FDT_LOAD_ADDR);
}
```

This "pre-loading" approach is valid for bring-up because it skips storage simulation while still exercising the firmware logic.

## Common Pitfalls

- **ROM returns wrong data on writes**: Boot ROM should return `TLM_COMMAND_ERROR_RESPONSE` on writes. If it silently ignores writes and returns OK, buggy firmware that accidentally writes to ROM will not be caught.
- **Stage load address conflicts**: Two stages mapped to overlapping addresses cause corruption. Maintain a memory map table and assert no overlaps at `end_of_elaboration()`.
- **Missing BL31 in the VP**: Some teams skip the ARM Trusted Firmware model. This works until the bootloader or OS makes a Secure Monitor Call (SMC) — then the VP hangs waiting for EL3 to respond.

## Memory Map Table (Example)

| Binary | Load Address | Size |
|---|---|---|
| Boot ROM | `0x0000_0000` | 64 KB |
| BL2 (SRAM) | `0x0004_0000` | 256 KB |
| BL31 | `0x0100_0000` | 512 KB |
| U-Boot | `0x0200_0000` | 2 MB |
| Kernel (Image) | `0x4000_0000` | ~16 MB |
| DTB | `0x4FA0_0000` | ~64 KB |
