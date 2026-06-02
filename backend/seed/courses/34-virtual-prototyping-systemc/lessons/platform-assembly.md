# Assembling a Platform in sc_main

`sc_main` is the entry point of every SystemC simulation. It plays the role of a top-level netlist: instantiate modules, bind sockets, configure parameters, and launch the simulation. Keeping it clean is an art — a messy `sc_main` is the most common maintainability complaint in VP code bases.

## The Three-Phase Pattern

```cpp
int sc_main(int argc, char *argv[]) {
    // ── Phase 1: Instantiation ──────────────────────────────────────
    CpuModel   cpu ("cpu",  CPU_FREQ);
    SimpleBus  bus ("bus");
    RomModel   rom ("rom",  ROM_BASE, ROM_SIZE, "firmware.bin");
    RamModel   ram ("ram",  RAM_BASE, RAM_SIZE);
    UartModel  uart("uart", UART_BASE);

    // ── Phase 2: Binding (wiring) ───────────────────────────────────
    cpu.i_socket.bind(bus.target_socket);

    bus.add_target(rom.t_socket,  ROM_BASE,  ROM_BASE  + ROM_SIZE  - 1);
    bus.add_target(ram.t_socket,  RAM_BASE,  RAM_BASE  + RAM_SIZE  - 1);
    bus.add_target(uart.t_socket, UART_BASE, UART_BASE + UART_SIZE - 1);

    // Connect interrupt line
    uart.irq_out.bind(cpu.irq_in[0]);

    // ── Phase 3: Simulation ─────────────────────────────────────────
    sc_core::sc_start();   // run until sc_stop() or no more events
    return 0;
}
```

**Rule:** Never put functional logic in `sc_main`. It should read like a wiring diagram.

## Loading Firmware

Firmware (ELF or binary) is loaded into the ROM/RAM models before `sc_start`:

```cpp
// Load ELF into memory model
void load_elf(const std::string &path, RamModel &ram) {
    // parse ELF sections and memcpy into ram.mem[]
}

load_elf("firmware.elf", ram);
sc_core::sc_start();
```

Some platforms load the ELF inside the ROM constructor — whichever approach you choose, be consistent.

## Controlling Simulation End

`sc_main` returns when `sc_stop()` is called from any module. The CPU model typically calls `sc_stop()` when it executes a known halt instruction or a reset vector loops forever.

```cpp
// Inside ISS execute()
if (instr == HALT_OPCODE) {
    SC_REPORT_INFO("cpu", "Halt instruction executed");
    sc_core::sc_stop();
}
```

You can also impose a wall-clock timeout:

```cpp
sc_core::sc_start(sc_core::sc_time(10, sc_core::SC_MS)); // run 10 ms simulated
```

## Scoping and Lifetime

All modules **must outlive** `sc_start`. Declaring them as local variables in `sc_main` before `sc_start` is safe because `sc_main` does not return until simulation ends.

Do **not** use `new` without a corresponding `delete` — SystemC does not manage module memory for you and ASAN will report leaks.

## Command-Line Arguments

A minimal argument parser lets you change firmware path, simulation timeout, and log verbosity without recompiling:

```cpp
std::string firmware = "firmware.elf";
if (argc > 1) firmware = argv[1];
```

For larger platforms, use a JSON or INI configuration file parsed before Phase 1.

## Worked Example: Minimal Cortex-M0 VP

```
sc_main
 ├── Instantiate: armv6m_iss, simple_bus, rom(0x0, 64KB), ram(0x20000000, 128KB), uart(0x40000000)
 ├── Bind sockets
 ├── Load vector table + firmware binary into rom.mem
 └── sc_start()
```

```cpp
int sc_main(int argc, char *argv[]) {
    ArmV6mIss cpu ("cpu");
    SimpleBus bus ("bus");
    RomModel  rom ("rom",  0x00000000, 64  * 1024);
    RamModel  ram ("ram",  0x20000000, 128 * 1024);
    UartModel uart("uart", 0x40000000);

    cpu.i_socket.bind(bus.t_socket);
    bus.add(rom.t_socket,  0x00000000, 0x0000FFFF);
    bus.add(ram.t_socket,  0x20000000, 0x2001FFFF);
    bus.add(uart.t_socket, 0x40000000, 0x40000FFF);
    uart.irq.bind(cpu.irq[0]);

    rom.load_binary("firmware.bin");
    sc_core::sc_start();
    return 0;
}
```

## Common Mistakes

- Binding a socket **after** `sc_start` — forbidden; SystemC will throw.
- Using the same socket index twice in `add_target` — last binding silently wins.
- Forgetting to connect interrupt signals — firmware waits forever for an IRQ that never fires.

**Interview answer:** `sc_main` has three phases: instantiate modules with constructor arguments, bind TLM sockets and signal ports, then call `sc_start`. It should contain no logic — just wiring. Firmware is loaded before `sc_start`, and simulation ends when any module calls `sc_stop`.
