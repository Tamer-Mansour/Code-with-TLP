# Quiz: Kernel Architecture: Monolithic vs Microkernel

**Q1. Which component is part of the minimal kernel in a microkernel design?**
- [ ] File system server
- [ ] Device driver for disk I/O
- [x] Inter-process communication (IPC) mechanism
- [ ] Network protocol stack

A microkernel keeps only the absolute minimum in privileged mode: IPC, thread scheduling, and basic address-space management. File systems, drivers, and network stacks run as user-space servers.

---

**Q2. What is the primary performance disadvantage of microkernels compared to monolithic kernels?**
- [ ] Microkernels use more RAM for their kernel image
- [ ] Microkernels cannot support SMP (multi-core) systems
- [x] Every cross-service call requires message-passing IPC with multiple mode switches
- [ ] Microkernels cannot load device drivers at runtime

In a microkernel, calling from the file system server to a block device driver requires at least two full IPC round trips (two mode switches each), whereas a monolithic kernel makes a direct in-kernel function call with no mode switch penalty.

---

**Q3. Which of the following best describes a hybrid kernel?**
- [ ] A kernel that runs entirely in user space
- [ ] A kernel that uses only spinlocks for all synchronization
- [ ] A kernel that dynamically switches between monolithic and microkernel mode at runtime
- [x] A kernel with a small microkernel core that also runs some services in kernel mode for performance

Windows NT and XNU (macOS) are classic examples: they use microkernel-inspired internal structure but keep performance-critical subsystems (drivers, file systems) in kernel mode rather than as separate user-space servers.

---

**Q4. What property distinguishes seL4 from other microkernel designs?**
- [ ] seL4 is written entirely in assembly for maximum performance
- [ ] seL4 supports more hardware platforms than Linux
- [x] seL4's implementation has been machine-checked to be functionally correct and memory-safe
- [ ] seL4 uses a monolithic architecture with a formal type system

seL4 was formally verified using the Isabelle/HOL theorem prover, proving that its C implementation matches an abstract specification and contains no memory safety violations — the strongest correctness assurance achieved for a production OS kernel.

---

**Q5. In the Linux kernel, which synchronization primitive is appropriate for protecting data accessed by both a hardware interrupt handler and process-context code?**
- [x] spin_lock_irqsave() / spin_unlock_irqrestore()
- [ ] mutex_lock() / mutex_unlock()
- [ ] rcu_read_lock() / rcu_read_unlock()
- [ ] down_interruptible() / up()

`spin_lock_irqsave()` both acquires the spinlock and disables local interrupts, preventing the IRQ handler from firing on the same CPU and attempting to acquire the same lock — which would cause a deadlock. Mutexes sleep, so they cannot be used in interrupt context.

---

**Q6. What is the key architectural difference between an exokernel and a microkernel?**
- [ ] An exokernel is larger and more complex than a microkernel
- [ ] An exokernel provides richer OS abstractions than a microkernel
- [ ] An exokernel runs in user space while a microkernel runs in kernel space
- [x] An exokernel exposes raw hardware resources with no OS abstractions; applications supply their own via library OSes

A microkernel still provides OS abstractions (address spaces, threads, IPC). An exokernel strips away all abstractions and only securely multiplexes physical resources (CPU cycles, disk blocks, memory pages), delegating all abstraction-building to per-application library OSes.
