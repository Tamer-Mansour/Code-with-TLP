# Video: CPU Datapath and the Fetch-Decode-Execute Cycle

This video shows, step by step, how a simple single-cycle RISC processor datapath is built — from the program counter and instruction memory, through the register file and ALU, to the data memory and write-back path.

**Key topics covered:**
- The role of each datapath component: PC, instruction memory, register file, ALU, data memory
- How control signals (RegWrite, ALUSrc, MemRead, MemWrite, MemToReg, Branch) route data
- Tracing a load word (lw) and add instruction through all datapath stages
- The control unit: how opcode bits fan out to produce correct control signals
- Limitations of the single-cycle design and why pipelining is needed

**Takeaway:** You will be able to draw the major datapath connections for a RISC processor, identify which control signals change for each instruction type, and explain the performance ceiling of a single-cycle implementation.
