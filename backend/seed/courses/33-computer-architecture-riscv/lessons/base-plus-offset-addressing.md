# Base-Plus-Offset Addressing

RISC-V supports exactly **one memory addressing mode**: base-plus-offset. Every load and store computes its effective address by adding a 12-bit signed immediate (the offset) to the value in a base register. Understanding this model deeply explains both why the architecture is simple and why it is sufficient.

## The Formula

```
effective_address = base_register + sign_extend(offset)
```

- **Base register**: any of the 32 general-purpose registers (`x0`–`x31`)
- **Offset**: a 12-bit signed integer embedded in the instruction, range −2048 to +2047

```asm
lw  x2, 16(x1)    # address = x1 + 16
lw  x3, -8(x1)    # address = x1 + (-8)
sw  x4, 0(x5)     # address = x5 + 0  (just the base, no offset)
```

## Why Only One Addressing Mode?

Many ISAs (x86, for example) support complex addressing modes such as:
- `base + index * scale + displacement`
- `[rsi + rax*4 + 0x10]`

RISC-V provides none of this. The benefits of the single mode:

- **Fixed-latency address calculation**: one adder, one cycle, always.
- **Simpler pipeline**: the address generation unit (AGU) is a single adder shared with the ALU.
- **No mode-decoding overhead**: hardware does not need to identify which formula to apply.

If you need `base + index * scale`, you compute it explicitly with shift and add instructions before the load/store.

## The 12-Bit Offset Range

With a 12-bit signed offset you can reach ±2047 bytes from the base register. This is large enough to:

- Address all fields in typical structs
- Walk arrays within a 4 KB window using a single base register
- Cover the local stack frame (within ~2 KB of the frame pointer)

If you need a larger offset, compute the full address in a register first:

```asm
# Access element at offset 8192 (beyond 12-bit range)
li   x10, 8192
add  x10, x1, x10    # x10 = base + 8192
lw   x2, 0(x10)      # load from that computed address
```

## Typical Patterns

### Array Access

```c
int arr[10];
int val = arr[i];   // arr[i] is at address &arr[0] + i*4
```

```asm
# x1 = base address of arr, x2 = i
slli  x3, x2, 2      # x3 = i * 4  (word size)
add   x3, x1, x3    # x3 = &arr[i]
lw    x4, 0(x3)     # load arr[i]
```

### Struct Field Access

```c
struct Foo { int a; int b; int c; };
struct Foo *p;
int val = p->c;   // c is at offset 8
```

```asm
lw  x5, 8(x10)    # x10 = p, offset 8 reaches field c
```

### Stack Frame Access

The frame pointer (`s0`/`fp`) serves as the base register. Local variables sit at negative offsets; saved registers at positive offsets from the previous frame.

```asm
# Typical function prologue (RV64)
addi  sp, sp, -32     # allocate 32 bytes on stack
sd    ra, 24(sp)      # save return address
sd    s0, 16(sp)      # save frame pointer
addi  s0, sp, 32      # set frame pointer

# Access local variable at -12(s0)
lw    x5, -12(s0)
```

## Worked Example: Offset Calculation

Given the instruction `lw x3, -4(x10)` and `x10 = 0x1000`:

1. The immediate `-4` is a 12-bit two's complement value.
2. Sign-extended to 64 bits: `0xFFFFFFFFFFFFFFFC` (= -4).
3. Effective address = `0x1000 + (-4)` = `0x0FFC`.
4. The CPU reads 4 bytes from `0x0FFC`–`0x0FFF` and places the result in `x3`.

## Common Pitfall

The offset is relative to the **register value**, not to the instruction's position in memory. Many beginners confuse this with PC-relative addressing (used by branches and `AUIPC`). `LW x2, 16(x1)` has nothing to do with where the `LW` instruction itself is stored.

> **Interview answer:** RISC-V uses a single addressing mode — base-plus-offset — where the effective address is a 12-bit signed immediate added to a base register. This simplicity allows a single-cycle fixed-latency address calculation and a uniform pipeline stage.
