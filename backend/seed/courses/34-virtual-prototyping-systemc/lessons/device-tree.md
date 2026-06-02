# Device Tree and Hardware Description

The **Device Tree** (DT) is the mechanism Linux uses to discover hardware at boot time on non-discoverable buses (ARM, RISC-V, etc.). Instead of hardcoding hardware addresses in the kernel, a Device Tree Blob (DTB) — a compiled binary — is passed to the kernel by the bootloader. The virtual platform must supply a DTB that accurately describes the modeled hardware.

## Why Device Tree Matters for VPs

In a real SoC, the hardware is fixed — the DTB describes what is physically present. In a VP, the hardware is defined by the SystemC model. If the DTB and the VP model disagree, the kernel either fails to find a device or accesses the wrong address:

- DTB says UART is at `0x0900_0000` → VP model is at `0x0800_0000` → kernel UART driver reads from wrong address → no console output
- DTB lists an interrupt number that the VP's GIC model does not drive → driver stalls waiting for an interrupt that never fires

**Interview answer:** The DTB passed to the Linux kernel must exactly match the addresses, interrupt numbers, and compatible strings of the peripherals modeled in the VP; any mismatch causes the kernel to silently skip the driver or access the wrong register.

## Device Tree Source Syntax

A Device Tree Source (DTS) file describes the platform hierarchy:

```dts
/dts-v1/;

/ {
    model = "VP ARM Cortex-A55 Platform";
    compatible = "arm,vexpress", "vp,platform-a55";
    #address-cells = <2>;
    #size-cells = <2>;

    cpus {
        #address-cells = <1>;
        #size-cells = <0>;
        cpu@0 {
            compatible = "arm,cortex-a55";
            device_type = "cpu";
            reg = <0>;
        };
    };

    memory@40000000 {
        device_type = "memory";
        reg = <0x0 0x40000000 0x0 0x80000000>; /* 2 GB at 1 GiB */
    };

    uart0: serial@09000000 {
        compatible = "arm,pl011", "arm,primecell";
        reg = <0x0 0x09000000 0x0 0x1000>;
        interrupts = <0 5 4>;       /* SPI 5, level-high */
        clocks = <&uartclk>, <&apb_pclk>;
        clock-names = "uartclk", "apb_pclk";
    };

    timer {
        compatible = "arm,armv8-timer";
        interrupts = <1 13 0xff08>,  /* secure physical */
                     <1 14 0xff08>,  /* non-secure physical */
                     <1 11 0xff08>,  /* virtual */
                     <1 10 0xff08>;  /* hypervisor */
    };
};
```

## Compiling and Loading the DTB

The DTS is compiled with `dtc` (Device Tree Compiler):

```bash
# Compile DTS → DTB
dtc -I dts -O dtb -o vp_platform.dtb vp_platform.dts

# Verify the compiled DTB
dtc -I dtb -O dts vp_platform.dtb | less
```

The resulting `.dtb` file is loaded into the VP's DRAM at a known address (e.g., `0x4FA0_0000`) and that address is passed to U-Boot, which then passes it to the kernel.

## Key Node Properties for VP Accuracy

| DTS Property | What It Controls | VP Impact |
|---|---|---|
| `reg` | Base address and size | Must match VP's address map exactly |
| `interrupts` | GIC interrupt type/number/flags | Must match VP's GIC model wiring |
| `compatible` | Driver selection string | Must match a kernel driver |
| `clocks` | Clock frequency | Affects baudrate, timer frequency |
| `memory` | DRAM base and size | Must match VP's DRAM model |

## Automating DTB Generation from VP Config

In sophisticated VPs, the address map is defined in a configuration file and the DTB is generated automatically:

```python
# generate_dtb.py — simplified example
import subprocess

config = {
    "uart_base": 0x09000000,
    "uart_irq":  5,
    "dram_base": 0x40000000,
    "dram_size": 0x80000000,
}

dts_template = """
/dts-v1/;
/ {{
    serial@{uart_base:08x} {{
        compatible = "arm,pl011";
        reg = <0x0 0x{uart_base:08x} 0x0 0x1000>;
        interrupts = <0 {uart_irq} 4>;
    }};
    memory@{dram_base:08x} {{
        device_type = "memory";
        reg = <0x0 0x{dram_base:08x} 0x0 0x{dram_size:08x}>;
    }};
}};
""".format(**config)

with open("generated.dts", "w") as f:
    f.write(dts_template)
subprocess.run(["dtc", "-I", "dts", "-O", "dtb",
                "-o", "generated.dtb", "generated.dts"])
```

## Common Pitfalls

- **Wrong `#address-cells`**: If `#address-cells = <1>` but you use 64-bit addresses, `dtc` will silently truncate the high bits.
- **Missing `status = "okay"`**: Nodes without `status = "okay"` (or without a `status` property on platforms that require it) are disabled by the kernel.
- **Interrupt cell format mismatch**: ARM GIC uses 3 cells `<type number flags>`; a common error is providing 2 cells, causing the kernel to misparse interrupt numbers.
