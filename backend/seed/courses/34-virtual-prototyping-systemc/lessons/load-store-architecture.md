# Load/Store Architecture

One of the most fundamental design decisions in an ISA is how memory is accessed. The **load/store architecture** is the dominant model in modern RISC processors, and understanding it is critical when modeling data-path behavior in SystemC.

## The Core Rule

In a load/store architecture, **arithmetic and logic instructions operate only on registers**. Memory is accessed exclusively through dedicated `LOAD` and `STORE` instructions. No other instruction can directly read from or write to memory.

This contrasts with Complex Instruction Set Computing (CISC), where instructions like x86's `add [mem], reg` can both read memory and perform arithmetic in one instruction.

## Why Load/Store?

| Benefit | Explanation |
|---|---|
| Predictable timing | Memory latency is isolated to load/store. ALU instructions always take a known number of cycles. |
| Simpler pipeline | Only two instruction types interact with the memory bus, simplifying hazard detection. |
| Better register use | Operands stay in registers across multiple ALU operations, reducing memory traffic. |
| Easier out-of-order | The memory access point is explicit, simplifying dependency tracking. |

## Instruction Examples (RISC-V)

```asm
; Load word from memory into register
lw  x5, 8(x6)     ; x5 = Memory[x6 + 8]   (32-bit load)

; Store word from register to memory
sw  x5, 12(x7)    ; Memory[x7 + 12] = x5   (32-bit store)

; Load byte (sign-extended)
lb  x8, 0(x9)     ; x8 = sign_extend(Memory[x9])

; Load byte unsigned
lbu x8, 0(x9)     ; x8 = zero_extend(Memory[x9])
```

The address is always computed as `base_register + immediate_offset` — never register + register directly in most RISC-V load/store instructions.

## Memory Alignment

Most load/store architectures require **natural alignment**:

- A 32-bit (`lw`) access must be at an address divisible by 4.
- A 16-bit (`lh`) access must be at an address divisible by 2.
- An 8-bit (`lb`) access has no alignment constraint.

Unaligned access either raises a hardware exception (strict architectures) or is handled in microcode at a performance cost (permissive architectures).

## Modeling Load/Store in SystemC

In a TLM-2.0 CPU model, a load translates to a `tlm::TLM_READ_COMMAND` and a store to a `tlm::TLM_WRITE_COMMAND` on the initiator socket:

```cpp
void execute_load(uint32_t rd, uint32_t base, int32_t offset) {
    sc_dt::uint64 addr = read_reg(base) + offset;
    uint32_t data = 0;

    tlm::tlm_generic_payload txn;
    txn.set_command(tlm::TLM_READ_COMMAND);
    txn.set_address(addr);
    txn.set_data_ptr(reinterpret_cast<unsigned char*>(&data));
    txn.set_data_length(4);
    txn.set_streaming_width(4);
    txn.set_byte_enable_ptr(nullptr);
    txn.set_dmi_allowed(false);
    txn.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);

    sc_core::sc_time delay = sc_core::SC_ZERO_TIME;
    mem_socket->b_transport(txn, delay);

    write_reg(rd, data);
}
```

The store path is symmetric — set `TLM_WRITE_COMMAND` and provide the data buffer.

## Endianness and Byte Ordering

When your CPU model accesses a memory that returns raw bytes, you must reconstruct the word with the correct byte order. RISC-V is little-endian by default, so byte 0 is the least-significant byte.

```cpp
// Assemble 4 bytes into a 32-bit word (little-endian)
uint32_t word = (uint32_t)buf[0]
              | ((uint32_t)buf[1] << 8)
              | ((uint32_t)buf[2] << 16)
              | ((uint32_t)buf[3] << 24);
```

## Common Pitfalls

- **Misaligned access** — forgetting to check alignment before issuing a TLM transaction causes silent data corruption or model crashes.
- **Conflating address and data widths** — a 32-bit ISA may use 34-bit or 64-bit physical addresses. Keep `sc_dt::uint64` for addresses even on 32-bit models.
- **Sign vs zero extension on sub-word loads** — `lb` sign-extends; `lbu` zero-extends. Getting this wrong breaks arithmetic on byte-sized data.

## Interview Answer

> "In a load/store architecture only dedicated LOAD and STORE instructions touch memory; all arithmetic operates on registers. This isolates memory latency, simplifies pipeline hazard logic, and makes the memory access points explicit — which is why every major RISC ISA (ARM, RISC-V, MIPS) follows this model."
