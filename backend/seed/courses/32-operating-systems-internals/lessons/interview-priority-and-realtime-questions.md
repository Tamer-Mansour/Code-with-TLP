# Interview Drill: Priority and Real-Time Scheduling

This lesson runs through the most frequently asked interview questions on priority-based and real-time scheduling. Each question includes the crisp answer a strong candidate gives, the common mistakes interviewers watch for, and depth follow-ups.

---

## Q1: What is starvation and how do you prevent it?

**Crisp answer:** Starvation is when a low-priority process never gets CPU time because higher-priority processes continually arrive. The standard fix is **aging** — gradually increasing a process's effective priority the longer it waits, so it eventually overtakes even the highest-priority arrivals.

**Common mistake:** Saying "use Round-Robin instead." RR prevents starvation within one priority level, but in a strict multi-priority system, low-priority processes still starve.

**Follow-up:** "What happens to the aging counter when the process finally runs?" It resets to zero, or the process will immediately rocket back to the top after its first burst.

---

## Q2: What is priority inversion? Give a real example.

**Crisp answer:** Priority inversion occurs when a high-priority task is blocked waiting for a resource held by a low-priority task, while medium-priority tasks run and prevent the low-priority task from finishing. The Mars Pathfinder (1997) experienced this: a low-priority meteorological task held a mutex needed by a high-priority bus management task, while medium-priority tasks kept running, causing watchdog resets.

**Fix:** Priority inheritance — the low-priority holder runs at the ceiling of the highest waiting task's priority until it releases the resource.

---

## Q3: What is the difference between multilevel queue and multilevel feedback queue scheduling?

| | Multilevel Queue | Multilevel Feedback Queue |
|---|---|---|
| Migration | None — fixed queue | Processes move up/down based on behavior |
| Adapts to workload | No | Yes |
| Starvation risk | Yes (lower queues) | Reduced (priority boost) |
| Complexity | Low | Medium |

**Crisp answer:** In multilevel queue, a process stays in its assigned queue forever. MLFQ promotes I/O-bound processes and demotes CPU-bound ones, approximating SJF without knowing burst lengths.

---

## Q4: What is the MLFQ priority boost and why is it needed?

**Crisp answer:** The priority boost periodically moves all processes back to the top queue. It serves two purposes: (1) prevents starvation of processes that were demoted and now sit permanently in low queues, and (2) re-adapts to processes that have changed behavior (e.g., a batch job that becomes interactive after a phase change).

Without the boost, a CPU-bound process demoted early could be starved forever.

---

## Q5: What is the difference between hard and soft real-time?

**Crisp answer:** In hard real-time, a missed deadline is a system failure — the output is useless or dangerous (e.g., airbag trigger). The system must provide a **provable, deterministic** guarantee. In soft real-time, occasional deadline misses degrade quality but don't cause failure (e.g., a dropped video frame).

**Key consequence:** Hard RT requires measuring and bounding WCET and proving schedulability analytically. Soft RT relies on statistical/empirical guarantees.

---

## Q6: Compare Rate-Monotonic and EDF.

**Crisp answer:**

- **RM:** Static priorities — shorter period gets higher priority. Schedulable if U ≤ n(2^(1/n)−1) → ~69% for large n. Simple, predictable failure mode (lowest-priority task misses first). Preferred for safety-critical systems.
- **EDF:** Dynamic priorities — nearest deadline runs first. Optimal: schedulable up to U = 100%. Failure mode in overload is unpredictable. Preferred when high utilization is needed.

**Follow-up:** "Can EDF handle tasks with D < T (deadline before period end)?" Yes — the analysis generalizes, but the utilization bound becomes U ≤ Σ(C_i/D_i) ≤ 1.

---

## Q7: What is CPU affinity and when would you use it?

**Crisp answer:** CPU affinity restricts a thread to run on a specific set of CPUs. You use it when cache warmth matters (thread's hot data is already in a specific core's cache), for NUMA locality (thread's memory is on a specific NUMA node), or to isolate real-time threads from interference by OS housekeeping tasks.

**Pitfall to mention:** Over-pinning prevents load balancing and can leave some CPUs idle while pinned CPUs are overloaded.

---

## Q8: If total CPU utilization exceeds 100%, what can a real-time scheduler do?

**Crisp answer:** No scheduler can make deadlines when the system is overloaded (U > 1.0). The options are:

1. **Admission control** — reject new tasks when adding them would make the system infeasible.
2. **Task dropping** — under overload, deliberately drop the least-important task.
3. **Load shedding** — reduce the WCET of flexible tasks (e.g., reduce sensor sampling rate).
4. **More hardware** — add CPUs or reduce task WCETs.

An interviewer who asks this is testing whether you know that scheduling cannot create CPU cycles from nothing.

---

## Quick-Fire Concepts

| Term | One-line definition |
|------|---------------------|
| WCET | Maximum CPU time a task ever needs in one activation |
| Utilization | C/T — fraction of CPU consumed per period |
| Schedulability | Whether a task set can always meet its deadlines |
| Priority ceiling | Preemptively raises a mutex's holder to a fixed ceiling priority |
| Work stealing | Idle CPU pulls tasks from busiest CPU's queue |
| Soft affinity | Scheduler prefers last CPU but migrates freely |
| Hard affinity | Thread is never moved off its pinned CPU set |
