# Quiz: Scheduling Algorithms: FCFS, SJF, and Round Robin

**Q1. Three processes arrive at time 0 with burst times P1=6 ms, P2=3 ms, P3=9 ms. Under FCFS (dispatched in input order P1→P2→P3), what is the average waiting time?**
- [ ] 3 ms
- [x] 5 ms
- [ ] 7 ms
- [ ] 9 ms

*Explanation: WT(P1)=0, WT(P2)=6, WT(P3)=6+3=9. Average = (0+6+9)/3 = 5 ms. Note that SJF (P2→P1→P3) would give average WT = (0+3+9)/3 = 4 ms — demonstrating SJF's advantage.*

**Q2. Which scheduling algorithm is provably optimal for minimizing average waiting time?**
- [ ] FCFS
- [x] Shortest-Job-First (SJF)
- [ ] Round Robin with quantum=1
- [ ] Priority scheduling

*Explanation: SJF (and its preemptive variant SRTF) is mathematically proven to minimize average waiting time. Round Robin prioritizes response time and fairness, not average waiting time.*

**Q3. What is the "convoy effect" in FCFS scheduling?**
- [ ] Long processes repeatedly starving short ones indefinitely
- [ ] Short processes blocking long processes at the head of the queue
- [x] A long CPU-bound process holds the CPU while many short processes queue behind it
- [ ] Context switches happening so frequently that throughput collapses

*Explanation: The convoy effect is analogous to a slow truck on a single-lane road — one long process causes all shorter processes behind it to wait, also leaving I/O devices idle because their processes cannot complete their brief CPU bursts.*

**Q4. A Round Robin scheduler has quantum=4 ms and context switch cost=1 ms. What fraction of CPU time is wasted on context switches?**
- [ ] 4%
- [ ] 10%
- [x] 20%
- [ ] 25%

*Explanation: Every 4 ms of useful work requires 1 ms of context-switch overhead. Wasted fraction = 1 / (4+1) = 1/5 = 20%. Reducing the quantum to 1 ms would raise waste to 50%.*

**Q5. Process P arrives at time 0 with burst 10 ms; process Q arrives at time 3 with burst 2 ms. Under non-preemptive SJF, in what order are they scheduled?**
- [x] P first, then Q
- [ ] Q first, then P
- [ ] Q and P simultaneously
- [ ] Determined by process priority

*Explanation: At time 0 only P is available, so P is dispatched immediately. Non-preemptive SJF cannot interrupt P even when the shorter Q arrives at t=3. P finishes at t=10, then Q runs from t=10 to t=12.*

**Q6. Which statement about Round Robin scheduling is TRUE?**
- [ ] It minimizes average waiting time for all workloads
- [ ] It can cause starvation if short processes keep arriving
- [ ] Increasing the quantum always improves system throughput
- [x] Worst-case response time is bounded by (n−1) × quantum

*Explanation: RR guarantees every process gets the CPU within (n−1) quanta, bounding response time. It does NOT minimize average waiting time, it does NOT cause starvation, and very large quanta degrade toward FCFS without guaranteeing throughput improvement.*
