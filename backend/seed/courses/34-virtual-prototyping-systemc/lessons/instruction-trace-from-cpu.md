# Producing an Instruction Trace

An instruction trace is a log of every instruction executed by the CPU — with its address, encoding, disassembly, and register state. It is the most powerful debugging tool available for an ISS: when software behaves differently on the simulator than on hardware, comparing traces from both reveals exactly where they diverge.

## What Goes in a Trace Record

A useful trace record captures, at minimum:

| Field | Example | Why it Matters |
|---|---|---|
| Simulation time | `1234 ns` | Correlate with other model logs |
| PC | `0x80001024` | Absolute location in the memory map |
| Instruction word | `0x00a50533` | Verify fetch correctness |
| Disassembly | `add x10, x10, x10` | Human readable |
| Changed register | `x10 = 0x00000014` | Show side effect |
| Memory access | `[0x20001000] = 0x42` | Show load/store |

Not every trace needs all fields. A minimal trace for regression diffs needs only PC and instruction word; a rich trace for debugging needs registers and memory too.

## Hooking the Trace into the ISS

The cleanest architecture inserts a **trace callback** between execute and the next fetch, without contaminating the execute logic:

```cpp
// Trace hook type
using TraceCallback = std::function<void(const TraceRecord&)>;

struct TraceRecord {
    sc_core::sc_time time;
    uint32_t pc;
    uint32_t instr_word;
    uint8_t  rd;
    uint32_t rd_value;
    bool     is_store;
    uint32_t mem_addr;
    uint32_t mem_data;
};

void RISCVCPU::run_thread() {
    while (!halted) {
        uint32_t word;
        fetch(pc, word);
        DecodedInstr d = decode(word);
        execute(d);

        if (trace_cb) {
            TraceRecord rec;
            rec.time       = sc_core::sc_time_stamp() + local_time;
            rec.pc         = pc_before_execute; // saved before execute() changes pc
            rec.instr_word = word;
            rec.rd         = d.rd;
            rec.rd_value   = reg[d.rd];
            trace_cb(rec);
        }
    }
}
```

The callback is optional and zero-overhead when not registered — the `if (trace_cb)` check costs one branch prediction.

## Trace Output Formats

### Plain Text (for Human Debugging)

```
 1000 ns  PC=0x80000000  addi   x2, x0, 256       x2=0x00000100
 1010 ns  PC=0x80000004  lui    x1, 0x20001        x1=0x20001000
 1020 ns  PC=0x80000008  sw     x0, 0(x1)          [0x20001000]=0x00000000
 1030 ns  PC=0x8000000c  addi   x3, x2, -1         x3=0x000000ff
```

### CSV (for Diff and Scripting)

```csv
time_ns,pc,hex,asm,rd,rd_val
1000,2147483648,0x00010113,"addi x2,x0,256",2,256
1010,2147483652,0x200010b7,"lui x1,0x20001",1,536875008
```

CSV traces are ideal for automated regression: `diff expected.csv actual.csv` immediately shows where two runs diverged.

### VCD / GTKWave (for Waveform Viewing)

Some tools emit Value Change Dump files where each architectural register is a signal. This lets engineers view software execution alongside RTL waveforms in the same viewer.

## Filtering and Compression

Unfiltered traces are enormous — a firmware boot can easily produce tens of millions of records. Practical strategies:

- **Address range filter**: Only trace instructions in a specific function or module.
- **PC window**: Start tracing after the first `ecall` (OS entry) to skip bootloader noise.
- **N-instructions limit**: Trace only the first N instructions from a trigger point.
- **Branch-only trace**: Record only taken branches and function calls — similar to hardware ETM/PTM trace.

```python
# Post-process: extract only function calls and returns from a CSV trace
import csv
with open("trace.csv") as f:
    for row in csv.DictReader(f):
        if "jal" in row["asm"] or "ret" in row["asm"]:
            print(row["time_ns"], row["pc"], row["asm"])
```

## Comparing ISS Trace to Hardware Trace

When a bug is suspected to be a model inaccuracy (not a software bug), the workflow is:

1. Run the same firmware on hardware with trace collection enabled (ETM, JTAG trace buffer).
2. Run the same firmware on the ISS with trace output enabled.
3. Diff the two traces at PC granularity.
4. The first diverging PC is the instruction where the model and hardware disagree.

This workflow has caught ISS bugs in corner cases like shift-by-zero, signed division overflow, and CSR bit masking.

## Performance Cost of Tracing

Tracing is expensive. Writing 10 million trace records to a file takes seconds and gigabytes. Best practice:

- Enable trace only in debug builds or when triggered by a specific event.
- Use a ring buffer (circular log) that retains only the last N records in memory — capture it only on assertion failure.
- Compress on the fly with `zlib` or `lz4` if full traces are required.

## Interview Answer

> "An instruction trace hooks between the execute stage and the next fetch, recording the PC, instruction word, and register side effects for every instruction. The most powerful use is comparison between ISS and hardware traces to find the exact instruction where model and silicon diverge. In production, filtering and ring-buffer techniques keep trace overhead manageable."
