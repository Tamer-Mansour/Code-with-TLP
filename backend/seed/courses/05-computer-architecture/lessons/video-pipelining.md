# Video: CPU Pipelining and Hazards

This video visualizes how the classic 5-stage RISC pipeline (IF, ID, EX, MEM, WB) works and what happens when hazards interrupt the smooth flow of instructions. Timing diagrams make pipeline stalls and forwarding paths concrete.

**Key topics covered:**
- The 5-stage pipeline with pipeline registers between each stage
- Data hazards: RAW (read-after-write) and how forwarding (bypassing) eliminates most stalls
- Load-use hazards and why one stall cycle is unavoidable without speculation
- Control hazards: branch delay and static vs dynamic branch prediction
- Structural hazards and why separate instruction/data caches matter
- Pipeline CPI calculation: ideal CPI plus stall cycles per instruction type

**Takeaway:** You will be able to draw timing diagrams for pipelined instruction sequences, identify where forwarding helps, calculate effective CPI given hazard rates, and explain the trade-offs in branch prediction strategies.
