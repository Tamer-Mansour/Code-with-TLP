# Boot Checkpointing and Snapshots

Booting Linux on a VP — even an approximately timed one — can take minutes of simulation time. Every developer on a project cannot afford to wait for a full boot each time they run a test. **Checkpointing** (also called **snapshotting**) solves this by saving the complete simulation state after boot and restoring it instantly for subsequent runs.

## What Is a Checkpoint?

A checkpoint is a serialized snapshot of the entire VP state at a specific simulation instant:

- All memory contents (DRAM, SRAM, Boot ROM)
- All CPU register file values (GPRs, system registers, PC, PSTATE)
- All peripheral register states (UART, GIC, timer, etc.)
- SystemC simulation time (`sc_time_stamp()`)

Restoring a checkpoint means the simulation resumes exactly where it was saved — the kernel is already running, processes are alive, and software can immediately begin testing.

**Interview answer:** A VP checkpoint serializes the complete hardware state (memory, registers, peripherals, simulation time) to disk; restoring it skips the boot sequence entirely, reducing developer iteration time from minutes to seconds.

## Checkpoint Points in the Boot Flow

| Checkpoint | State Saved | Benefit |
|---|---|---|
| After DRAM init | DRAM initialized, CPU at bootloader entry | Skip DRAM training simulation |
| After U-Boot | Kernel + DTB loaded in DRAM | Skip bootloader execution |
| After kernel boot | Full Linux userspace running | Directly test application software |
| After app install | Specific test environment ready | Reproducible integration tests |

## Implementing Checkpointing in a SystemC VP

### Saving a Checkpoint

```cpp
void Platform::save_checkpoint(const std::string& dir) {
    // 1. Pause simulation
    sc_core::sc_pause();

    // 2. Serialize memory
    dram.serialize(dir + "/dram.bin");
    sram.serialize(dir + "/sram.bin");

    // 3. Serialize CPU state
    cpu.serialize(dir + "/cpu_state.json");

    // 4. Serialize peripherals
    uart.serialize(dir + "/uart.json");
    gic.serialize(dir + "/gic.json");
    timer.serialize(dir + "/timer.json");

    // 5. Save simulation timestamp
    std::ofstream ts(dir + "/timestamp.txt");
    ts << sc_core::sc_time_stamp().to_string();

    SC_REPORT_INFO("Platform", ("Checkpoint saved to " + dir).c_str());
}
```

### Restoring a Checkpoint

```cpp
void Platform::restore_checkpoint(const std::string& dir) {
    dram.deserialize(dir + "/dram.bin");
    sram.deserialize(dir + "/sram.bin");
    cpu.deserialize(dir + "/cpu_state.json");
    uart.deserialize(dir + "/uart.json");
    gic.deserialize(dir + "/gic.json");
    timer.deserialize(dir + "/timer.json");

    // Restore simulated time
    std::ifstream ts(dir + "/timestamp.txt");
    std::string time_str;
    ts >> time_str;
    // Note: sc_time cannot be set retroactively;
    // use a time offset variable in the CPU model
    SC_REPORT_INFO("Platform",
        ("Checkpoint restored from " + dir).c_str());
}
```

## Memory Serialization

For large DRAM models (1–8 GB), raw serialization is slow. Compression and sparse representation dramatically reduce checkpoint size:

```cpp
void DramModel::serialize(const std::string& path) {
    // Only save pages that have been written
    std::ofstream f(path, std::ios::binary);
    for (auto& [page_addr, page_data] : m_dirty_pages) {
        f.write(reinterpret_cast<char*>(&page_addr), 8);
        f.write(reinterpret_cast<char*>(page_data.data()),
                PAGE_SIZE);
    }
}
```

Using a **copy-on-write** (COW) DRAM model means only pages that have been written since the last checkpoint need to be saved — typically much less than the full DRAM size.

## Trigger Mechanisms

Checkpoints can be triggered several ways:

- **Time-based**: Save at a fixed `sc_time` (e.g., 500 ms simulated time after boot)
- **PC-based watchpoint**: Save when the CPU reaches a specific address (e.g., `init` process entry)
- **Console string match**: Save when the UART outputs a specific string (e.g., `"login:"`)
- **Manual command**: External script sends a signal to the VP process

```cpp
// Console-triggered checkpoint
void UartModel::on_tx_char(char c) {
    m_console_buffer += c;
    if (m_console_buffer.find("login:") != std::string::npos) {
        platform->save_checkpoint("checkpoints/post_boot");
        m_console_buffer.clear();
    }
}
```

## Common Pitfalls

- **Timer discontinuity after restore**: If the simulated timer value jumps backward (or forward) on restore, the kernel's time-keeping breaks. Ensure the timer model's internal counter is included in the checkpoint.
- **File descriptor state not saved**: If the VP has open network connections or file handles, these are host OS resources and cannot be checkpointed. Design peripheral models to reconnect on restore.
- **Non-determinism breaks reproducibility**: If any model uses `rand()` or host time (`gettimeofday`), two runs from the same checkpoint may diverge. Seed random sources from the checkpoint.
