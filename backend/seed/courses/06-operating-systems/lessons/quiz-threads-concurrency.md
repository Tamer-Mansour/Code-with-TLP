# Quiz: Threads & Concurrency

**Q1. Which resource is NOT shared between threads of the same process?**

- [ ] Heap memory
- [ ] Open file descriptors
- [x] Each thread's stack
- [ ] Global variables

**Q2. Why is a context switch between two threads of the SAME process cheaper than between two different processes?**

- [ ] Threads have smaller stacks, so less data must be saved
- [x] The page table base register (CR3 on x86) does not change, avoiding a costly TLB flush
- [ ] Threads do not need to save floating-point registers
- [ ] The kernel skips saving the program counter for in-process thread switches

**Q3. What are the three required properties of a correct solution to the critical section problem?**

- [ ] Atomicity, durability, and isolation
- [ ] Fairness, throughput, and latency
- [x] Mutual exclusion, progress, and bounded waiting
- [ ] Safety, liveness, and lock-freedom

**Q4. What is a data race?**

- [ ] Any situation where two threads access the same file simultaneously
- [x] Two threads access the same memory location concurrently, at least one writes, and there is no synchronization between them
- [ ] A race condition caused specifically by network I/O ordering issues
- [ ] When two threads reach a barrier instruction at exactly the same time

**Q5. Python's Global Interpreter Lock (GIL) means that:**

- [ ] Python threads cannot share memory or global variables
- [ ] Python does not support threading at all
- [x] Only one Python thread can execute Python bytecode at a time, limiting CPU-bound parallelism to a single core in CPython
- [ ] Python threads cannot perform blocking I/O operations while other threads run

**Q6. In Peterson's algorithm, what is the role of the `turn` variable?**

- [ ] It stores the thread's scheduling priority
- [ ] It tracks how many times each thread has entered the critical section
- [x] It acts as a polite tie-breaker: when both threads want to enter simultaneously, `turn` grants access to one of them
- [ ] It counts the number of context switches between the two threads
