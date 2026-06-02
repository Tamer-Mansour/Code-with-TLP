# Quiz: CPU Scheduling Fundamentals

**Q1. Which component performs the actual context switch after the scheduling decision is made?**
- [ ] The long-term scheduler
- [ ] The medium-term scheduler
- [x] The dispatcher
- [ ] The interrupt handler

The **dispatcher** carries out the context switch — saving the outgoing process's registers, loading the incoming process's state, and returning to user mode. The scheduler only decides who runs next.

---

**Q2. A process has arrival time = 0, burst time = 8, and completes at time 14 under Round Robin. What is its waiting time?**
- [ ] 14
- [ ] 8
- [x] 6
- [ ] 22

Turnaround = Completion - Arrival = 14 - 0 = 14. Waiting = Turnaround - Burst = 14 - 8 = **6**.

---

**Q3. Which of the following scheduling events occurs ONLY in a preemptive scheduler?**
- [ ] A process transitions from RUNNING to BLOCKED
- [ ] A process terminates
- [x] A timer interrupt moves a process from RUNNING to READY
- [ ] A new process is created and added to the ready queue

A timer-forced eviction of the running process (RUNNING → READY) is the defining characteristic of preemptive scheduling. The other options happen in both preemptive and non-preemptive schedulers.

---

**Q4. Three processes all arrive at time 0 with burst times 10, 4, and 6. Under FCFS (served in the given order), what is the average waiting time?**
- [ ] 0 ms
- [ ] 10 ms
- [x] 8 ms
- [ ] 6 ms

P1 waits 0 ms. P2 waits 10 ms. P3 waits 10+4=14 ms. Average = (0+10+14)/3 = 24/3 = **8 ms**.

---

**Q5. Which scheduling metric measures how quickly a process first receives CPU time, and is most critical for interactive systems?**
- [ ] Turnaround time
- [ ] Waiting time
- [x] Response time
- [ ] Throughput

**Response time** = first CPU start time - arrival time. It measures how soon the user gets any feedback, making it the key metric for interactive workloads. Turnaround time captures total completion time; waiting time captures total idle time in the ready queue.

---

**Q6. What is the primary cause of the convoy effect in FCFS scheduling?**
- [ ] Processes with the same priority blocking each other
- [x] A long CPU-bound process blocking many short processes behind it
- [ ] The scheduler spending too much time switching contexts
- [ ] I/O-bound processes monopolizing the ready queue

The **convoy effect** occurs when one long-running CPU-bound process arrives first and forces many shorter processes to wait, inflating average waiting time. SJF mitigates this by always scheduling the shortest burst first.
