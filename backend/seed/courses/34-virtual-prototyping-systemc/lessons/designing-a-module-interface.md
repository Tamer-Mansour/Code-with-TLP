# Designing a Clean Module Interface

A module's interface is its contract with the rest of the world. A well-designed interface makes a module reusable across projects, easy to integrate into a larger platform, and simple to replace with a more detailed or more abstract model. Poor interface design creates tight coupling, hides assumptions, and forces downstream changes whenever the internals evolve.

## What Belongs in the Interface

A SystemC module's public interface consists of:

- **Ports** (`sc_in`, `sc_out`, `sc_inout`, `sc_port`) — the electrical or logical connections.
- **TLM sockets** — initiator or target sockets for transaction-level communication.
- **Constructor parameters** — configuration values (bus width, FIFO depth, clock period) that are fixed at elaboration time.
- **Public callbacks** — virtual methods that a subclass or testbench may override.

Keep everything else private or protected.

## Port Naming Conventions

Use descriptive, self-documenting names. Mirror RTL naming conventions when the model must correspond to an existing IP block:

```cpp
SC_MODULE(SpiController) {
    sc_in<bool>           clk;
    sc_in<bool>           rst_n;       // active-low reset, matching RTL convention
    sc_out<bool>          spi_csn;     // chip select, active low
    sc_out<bool>          spi_clk;
    sc_inout<bool>        spi_mosi;
    sc_in<bool>           spi_miso;

    // TLM interface for CPU-side register access
    tlm_utils::simple_target_socket<SpiController> reg_socket;

    SpiController(sc_module_name nm, unsigned clk_div = 4)
        : sc_module(nm), clk_div_(clk_div) {
        // ...
    }

private:
    unsigned clk_div_;
};
```

## Minimizing the Interface

Every port you expose is a commitment. Unnecessary ports:

- Force every instantiation to wire a signal to them, even if unused.
- Make refactoring harder when the signal is eliminated.

Ask for each port: "Does the parent module need to see this?" If the answer is no — it is inter-process communication *within* the module — use an internal `sc_signal` instead.

## Configuration Parameters vs. Runtime Signals

Decide early whether a value is:

- **Elaboration-time constant** — bus width, number of channels. Make it a constructor parameter and store it as a `const` member.
- **Runtime variable** — a value that changes during simulation. Make it a port or an `sc_signal` member.

Mixing these categories creates problems:

```cpp
// BAD: using a port for something that never changes after reset
sc_in<int> data_width;  // data_width.read() called in every compute cycle

// GOOD: configuration resolved once at elaboration
const int DATA_WIDTH;
MyMod(sc_module_name nm, int dw) : sc_module(nm), DATA_WIDTH(dw) {}
```

## Abstract Interfaces with sc_port and Interfaces

For maximum reusability, accept an interface class rather than a concrete channel:

```cpp
struct WriteIf : sc_interface {
    virtual void write(uint32_t addr, uint32_t data) = 0;
};

SC_MODULE(Dma) {
    sc_port<WriteIf> mem_port;  // accepts any implementation of WriteIf

    SC_CTOR(Dma) { SC_THREAD(run); }
    void run() {
        mem_port->write(0x1000, 0xDEAD);
    }
};
```

This pattern allows the testbench to plug in a fast functional memory model during unit test and a detailed DRAM model during full-system simulation — with no change to `Dma`.

## Documenting the Interface

Add a comment block above the module declaration that captures:

- The purpose of the module in one sentence.
- The clock domain and reset polarity.
- Any protocol assumptions (e.g., "address is stable for 2 cycles after `req` is asserted").
- Latency or throughput guarantees.

```cpp
/// SPI controller: manages a single SPI bus at up to clk/clk_div frequency.
/// Reset: active-low, synchronous.
/// reg_socket: AHB-Lite target, 32-bit aligned word accesses only.
SC_MODULE(SpiController) { ... };
```

## Common Pitfalls

- **Exposing internal signals as ports.** If `done` is only read by one internal process, it should not be a port.
- **Using plain C++ getter/setter functions as the interface.** Functions work for testbenches but cannot be used in sensitivity lists or TLM bindings.
- **Hardcoding bus widths with magic numbers.** Parameterize them; hardcoded widths make the module useless the moment a different bus standard is needed.
- **Mixing concerns in the same module.** A single module that handles both the SPI protocol and the DMA engine is hard to test and reuse. Split at natural boundaries.

> **Interview answer:** A clean SystemC module interface exposes only the ports and sockets needed by the parent — everything else is internal. Configuration values that are fixed at elaboration should be constructor parameters (stored as `const` members), not signals. Using abstract `sc_interface` types with `sc_port` instead of concrete channels maximizes reusability and makes it easy to swap implementation models.
