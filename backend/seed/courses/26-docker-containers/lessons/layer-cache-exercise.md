# Layer Cache Simulation

Docker caches each instruction's output as a layer. On the next build, layers stay cached as long as the **prefix** of instructions (and their inputs) matches. Once any line differs, all subsequent layers are rebuilt.

In this exercise you'll simulate that: given two Dockerfiles, count how many leading instructions match exactly.

See the prompt.
