# Quiz: Debugging Virtual Prototypes

**Q1. You attach gdb to a virtual prototype and type `target remote localhost:1234`. What protocol does gdb use to communicate with the ISS?**

- [ ] JTAG over TCP
- [ ] OpenOCD binary protocol
- [x] GDB Remote Serial Protocol (RSP)
- [ ] GDB Machine Interface (MI)

RSP is the standard text-based packet protocol (`$data#checksum`) used by gdb to communicate with any remote target, including virtual-prototype ISS stubs.

---

**Q2. While debugging a hang, you inspect the ARM CPSR and find it contains `0x600000D3`. Which of the following is true?**

- [ ] The CPU is in User mode with IRQ enabled
- [ ] The CPU is in FIQ mode with IRQ disabled
- [x] The CPU is in Supervisor mode with IRQ and FIQ disabled
- [ ] The CPU is in Abort mode with IRQ enabled

`0xD3` in the low byte = `1101 0011`: bits [4:0] = `10011` = SVC mode, bit 7 (I) = 1 (IRQ disabled), bit 6 (F) = 1 (FIQ disabled).

---

**Q3. An instruction trace shows two PC values (`0x000100a0` and `0x000100a4`) repeating 500,000 times in a row. What is the most likely root cause?**

- [ ] A cache miss storm causing repeated refetches
- [ ] The ISS has a branch-prediction bug
- [x] The software is spinning on a peripheral ready bit that the model never sets
- [ ] The linker placed two functions at the same address

A tight two-instruction loop in an embedded context is the classic polling spin: the CPU reads a status register and branches back if the ready bit is zero. If the VP model never sets the bit, the loop runs forever.

---

**Q4. You want to catch the exact instruction that corrupts a global variable at address `0x20001048`. Which gdb command is most appropriate?**

- [ ] `break *0x20001048`
- [x] `watch *((uint32_t *)0x20001048)`
- [ ] `x/1wx 0x20001048`
- [ ] `set *((uint32_t *)0x20001048) = 0`

`watch` sets a hardware watchpoint that fires whenever the target address is written. `break` sets a code breakpoint (on instructions, not data). `x` reads memory. `set` writes memory.

---

**Q5. When Linux refuses to print any output on the VP console, what should you check first before investigating the kernel or device tree?**

- [ ] The kernel command line `root=` parameter
- [ ] Whether VBAR is correctly configured
- [ ] The calibrate_delay spin loop
- [x] Whether the UART model is correctly implemented and mapped

A broken or missing UART model makes every other boot failure look identical — a blank console. Always verify the UART first; if a "hello world" binary works, the UART is fine and you can investigate higher layers.

---

**Q6. An RSP stub receives the packet `$m20001000,4#xx`. What should it do?**

- [ ] Write 4 bytes to address `0x20001000`
- [ ] Single-step 4 instructions from address `0x20001000`
- [x] Read 4 bytes from address `0x20001000` and return them as a hex string
- [ ] Set a breakpoint at address `0x20001000`

The `m` command in RSP means memory read: `m addr,length`. The stub reads `length` bytes from `addr` and returns them as a hex-encoded string in the reply packet.
