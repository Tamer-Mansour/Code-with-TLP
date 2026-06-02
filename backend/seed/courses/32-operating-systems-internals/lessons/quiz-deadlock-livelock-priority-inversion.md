# Quiz: Deadlock, Livelock, and Priority Inversion

**Q1. Which of the four Coffman conditions is MOST easily eliminated in practice through software design?**
- [ ] Mutual exclusion
- [ ] Hold and wait
- [ ] No preemption
- [x] Circular wait

Circular wait is eliminated by enforcing a global lock-ordering discipline — require all threads to acquire locks in a fixed ascending order. Mutual exclusion is inherent to non-shareable resources; no preemption is difficult to implement safely; hold-and-wait elimination reduces throughput significantly.

---

**Q2. In a Resource Allocation Graph with multi-instance resources, which statement about cycles is correct?**
- [ ] A cycle guarantees deadlock, regardless of the number of resource instances.
- [x] A cycle is necessary but not sufficient for deadlock; further analysis is needed.
- [ ] A cycle is sufficient but not necessary for deadlock.
- [ ] Cycles are impossible when resources have more than one instance.

For single-instance resources, a cycle is both necessary and sufficient. For multi-instance resources, a cycle indicates a possible deadlock, but a process outside the cycle might release an instance that breaks the wait chain — requiring the Banker-style reachability analysis to confirm.

---

**Q3. The Banker's Algorithm grants a resource request only when:**
- [ ] The requesting process has the highest priority in the system.
- [ ] The request does not exceed the process's declared maximum need.
- [x] The resulting state passes the safety algorithm — every process can still finish.
- [ ] At least half of the total resource instances remain available after granting.

The Banker's Algorithm checks whether the post-grant state is "safe" — i.e., there exists a sequence in which all processes can complete given their remaining needs and the remaining available resources. The simple availability check (option 4) is necessary but not sufficient.

---

**Q4. How does livelock differ from deadlock at the operating system level?**
- [ ] Livelock occurs only in single-core systems; deadlock occurs in multi-core systems.
- [ ] In livelock, processes are blocked on a mutex; in deadlock, processes are spinning.
- [x] In livelock, processes are actively running but making no progress; in deadlock, processes are blocked.
- [ ] Livelock can be detected by a Wait-For Graph cycle; deadlock cannot.

Livelock processes are in a running state and consume CPU — they just keep yielding to each other in a loop. Deadlocked processes are blocked waiting for a resource, consuming no CPU. A WFG cycle detects deadlock; livelock leaves no blocked edges in the WFG.

---

**Q5. Which scenario best describes priority inversion?**
- [ ] A high-priority task preempts a low-priority task and runs immediately.
- [ ] Two equal-priority tasks deadlock on a shared mutex.
- [x] A high-priority task waits for a mutex held by a low-priority task that has been preempted by a medium-priority task.
- [ ] A low-priority task starves because the scheduler always picks higher-priority tasks.

This is the classic three-task priority inversion scenario. H needs a mutex held by L; M (which has no relation to the mutex) preempts L because M > L; H is forced to wait as long as M runs — even though H > M. Priority inheritance fixes this by temporarily boosting L's priority to H's level.

---

**Q6. Which POSIX mutex attribute enables priority inheritance on Linux?**
- [ ] `PTHREAD_MUTEX_RECURSIVE`
- [ ] `PTHREAD_PRIO_PROTECT`
- [x] `PTHREAD_PRIO_INHERIT`
- [ ] `PTHREAD_MUTEX_ERRORCHECK`

`PTHREAD_PRIO_INHERIT` makes the mutex owner inherit the priority of the highest-priority blocked waiter. `PTHREAD_PRIO_PROTECT` implements the Priority Ceiling Protocol instead. `RECURSIVE` and `ERRORCHECK` are unrelated to priority management.
