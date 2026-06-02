# Minimum Modeled Hardware to Boot Linux

A common misconception is that a VP must be complete before software bring-up can begin. In reality, Linux can boot on a surprisingly minimal set of modeled peripherals. Knowing the absolute minimum set helps teams prioritize what to model first and unblock software teams early.

## The Minimum Set

To boot Linux to a shell prompt, you need these and only these hardware models:

| Component | Why It Is Required |
|---|---|
| CPU ISS | Execute instructions; no CPU = nothing runs |
| DRAM (flat memory) | Kernel, stack, heap, page tables |
| Interrupt controller (GIC) | Timer interrupt delivery; kernel scheduling |
| System timer (ARM Generic Timer) | `jiffies`, `udelay`, kernel tick |
| UART (serial console) | Kernel console output; without this boot appears to hang |
| Bus / router | Connects all models; decode addresses |

Everything else — Ethernet, USB, GPU, storage — can be a stub that returns safe default values.

**Interview answer:** The minimum hardware to boot Linux in a VP is: CPU ISS, flat DRAM model, GIC interrupt controller, system timer, and a UART; everything else can be a stub returning zeros.

## Why Each Component Is Essential

### CPU ISS

Without a CPU ISS, there is nothing to execute instructions. A functional (non-cycle-accurate) ISS is sufficient; timing accuracy is not required to boot.

### Flat DRAM

Linux needs memory for kernel code, BSS, stack, heap, and page tables. A simple `std::vector<uint8_t>` of 512 MB is sufficient:

```cpp
SC_MODULE(FlatDram) {
    tlm_utils::simple_target_socket<FlatDram> socket;
    std::vector<uint8_t> m_mem;

    FlatDram(sc_module_name n, size_t size_bytes)
        : sc_module(n), m_mem(size_bytes, 0) {
        socket.register_b_transport(this, &FlatDram::b_transport);
    }

    void b_transport(tlm::tlm_generic_payload& gp,
                     sc_core::sc_time& delay) {
        uint64_t off = gp.get_address();
        if (gp.get_command() == tlm::TLM_READ_COMMAND)
            std::memcpy(gp.get_data_ptr(), &m_mem[off],
                        gp.get_data_length());
        else
            std::memcpy(&m_mem[off], gp.get_data_ptr(),
                        gp.get_data_length());
        gp.set_response_status(tlm::TLM_OK_RESPONSE);
    }
};
```

### GIC (Generic Interrupt Controller)

The ARM Generic Interrupt Controller v2 or v3 must be modeled. At minimum:

- Distributor registers: enable/disable SPIs
- CPU Interface registers: `IAR` (acknowledge), `EOIR` (end-of-interrupt)
- Deliver virtual IRQ to CPU ISS when a peripheral asserts an interrupt line

Without the GIC, the system timer interrupt is never delivered, the kernel scheduler never runs, and the boot process hangs after `start_kernel()`.

### ARM Generic Timer

The ARMv8 Generic Timer is accessed via system registers (`CNTPCT_EL0`, `CNTP_CTL_EL0`, etc.), not memory-mapped registers. The CPU ISS must emulate these system registers:

```cpp
uint64_t CpuModel::read_sysreg(uint32_t encoding) {
    switch (encoding) {
    case CNTPCT_EL0:
        // Return host nanoseconds / 10 to simulate 100 MHz counter
        return host_ns() / 10;
    case CNTFRQ_EL0:
        return 100000000ULL; // 100 MHz
    default:
        return m_sysregs[encoding];
    }
}
```

### UART

A minimal UART that prints to `stdout` (as shown in the bootloader lesson) is sufficient. The kernel's `earlycon` mechanism uses a UART very early, before the full driver is probed.

## What Can Be a Stub

These components can return hardcoded safe values without blocking the boot:

```cpp
// Stub peripheral: absorbs all accesses, returns 0
void StubPeripheral::b_transport(tlm::tlm_generic_payload& gp,
                                 sc_core::sc_time& delay) {
    if (gp.get_command() == tlm::TLM_READ_COMMAND)
        std::memset(gp.get_data_ptr(), 0, gp.get_data_length());
    gp.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

Stubbed components: Power management (PMIC), clock controller (if firmware does not check PLL lock), watchdog timer (disable in DTS with `status = "disabled"`), GPIO controller, DMA controller (if no DMA-dependent drivers are loaded).

## Incremental Model Maturity

A practical bring-up strategy is to start with the minimum set and add peripheral models as the software team needs them:

```
Week 1:  CPU + DRAM + UART → Boot ROM executes
Week 2:  + GIC + Timer     → U-Boot executes
Week 3:  + GIC properly    → Linux kernel boots to shell
Week 4:  + Ethernet stub   → Network driver loads (fails gracefully)
Week 5:  + Real Ethernet   → Network traffic flows
```

This approach keeps the software team unblocked while hardware model development continues in parallel.

## Checklist Before First Linux Boot Attempt

- [ ] Reset vector address in CPU model matches Boot ROM base address
- [ ] DRAM covers kernel load address (`0x4000_0000` typically)
- [ ] GIC distributor and CPU interface registers respond correctly
- [ ] Generic Timer `CNTPCT_EL0` increments monotonically
- [ ] UART TX path prints characters to host console
- [ ] DTB `memory` node matches DRAM base and size
- [ ] DTB `interrupts` for UART and timer match GIC model wiring
- [ ] All unknown peripheral accesses return `TLM_OK_RESPONSE` (not bus error)
