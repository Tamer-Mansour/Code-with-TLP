# Trace Logging and Verbosity Levels

Trace logging is the lightest-weight observability mechanism in a virtual prototype. Done well, it gives you a replayable record of what the simulation did without requiring a debugger session. Done badly, it buries important events in megabytes of noise. This lesson covers structured logging, verbosity levels, and how to build a log that is actually useful.

## Why Structured Logging Beats Printf

A raw `printf("write to UART\n")` tells you something happened. A structured log entry tells you *when*, *where*, *what*, and *why*:

```
[0.000123450 s] [UART] [INFO ] TX byte 0x41 ('A') — fifo_depth=3/16
[0.000123500 s] [BUS ] [WARN ] Unaligned 3-byte read at 0x40001001
[0.000200000 s] [CPU ] [ERROR] PC=0x1054 data abort — addr=0x00000000
```

Fields: timestamp, component tag, severity, human-readable message, key-value context. This format is grep-friendly and parseable by scripts.

## Verbosity Levels

Most VP frameworks define a hierarchy similar to:

| Level | Value | Use |
|---|---|---|
| ERROR | 0 | Always printed; simulation may not continue |
| WARNING | 1 | Unexpected but recoverable condition |
| INFO | 2 | Notable events (reset, interrupt, DMA start) |
| DEBUG | 3 | Per-transaction detail |
| TRACE | 4 | Per-cycle or per-instruction detail |

SystemC uses `SC_REPORT_INFO`, `SC_REPORT_WARNING`, and `SC_REPORT_ERROR`. You can set the severity threshold at runtime:

```cpp
sc_report_handler::set_verbosity_level(SC_DEBUG);
```

For custom components, a simple flag works well:

```cpp
// In your model header:
int verbosity = 1;  // default: INFO only

// Usage:
if (verbosity >= 3)
    SC_REPORT_INFO(name(), ("TX byte " + std::to_string(byte)).c_str());
```

## Building a Configurable Logger

A minimal logger class that supports runtime verbosity:

```cpp
struct Logger {
    const char* tag;
    int level = 1;

    void log(int sev, const std::string& msg) const {
        if (sev > level) return;
        static const char* names[] = {"ERROR","WARN ","INFO ","DEBUG","TRACE"};
        std::cout << "[" << sc_time_stamp() << "] "
                  << "[" << tag << "] "
                  << "[" << names[sev] << "] "
                  << msg << "\n";
    }

    void error(const std::string& m) const { log(0, m); }
    void warn (const std::string& m) const { log(1, m); }
    void info (const std::string& m) const { log(2, m); }
    void debug(const std::string& m) const { log(3, m); }
    void trace(const std::string& m) const { log(4, m); }
};
```

Pass verbosity via command-line argument and fan it out to all models at build time.

## What to Log at Each Level

- **ERROR:** Illegal memory accesses, unimplemented mandatory registers, protocol violations.
- **WARNING:** Unaligned accesses the hardware silently ignores, deprecated register writes, reads of write-only registers.
- **INFO:** Peripheral initialization complete, interrupt asserted/deasserted, DMA transfer start/end.
- **DEBUG:** Every register read/write with address and value.
- **TRACE:** Every bus transaction, every instruction executed (better via a dedicated instruction trace).

## Correlating Log Lines with Source

Include the simulation time in every log entry so you can correlate with gdb (`set $pc` to the address visible in the trace) or with the instruction trace. A log line at `0.000123450 s` corresponds to exactly the same simulation state as an instruction trace entry with the same timestamp — they are from the same deterministic run.

## Common Pitfalls

- **Logging inside hot paths at high verbosity.** A TRACE log on every instruction can slow a 100 MIPS ISS to 1 MIPS. Gate expensive logging with `if (verbosity >= 4)`.
- **Forgetting to flush.** `std::cout` with `sync_with_stdio(false)` may not flush before a crash. Use `std::cerr` for errors or call `std::cout.flush()` periodically.
- **Log lines without timestamps.** Without a timestamp, you cannot place events in the simulation timeline or correlate with other logs.

> **Interview answer:** "I build a structured logger with at least five severity levels (ERROR through TRACE), gated by a runtime verbosity flag, and always include the sc_time_stamp() so log lines can be correlated with gdb and instruction traces."
