# Quiz: Advanced Workloads

**Q1. A StatefulSet named `db` with 3 replicas creates pods named:**
- [ ] `db-pod-0`, `db-pod-1`, `db-pod-2`
- [x] `db-0`, `db-1`, `db-2`
- [ ] `db-replica-1`, `db-replica-2`, `db-replica-3`
- [ ] Random names prefixed with `db-`

**Q2. You need to expose a StatefulSet so that each pod gets its own stable DNS entry (`db-0.db-svc`, `db-1.db-svc`, etc.). Which Service type is required?**
- [ ] ClusterIP
- [ ] NodePort
- [x] Headless Service (`clusterIP: None`)
- [ ] ExternalName

**Q3. A DaemonSet pod is running on node `worker-3`. You add a new node `worker-4` to the cluster. What happens?**
- [ ] Nothing — DaemonSets only affect nodes existing at creation time
- [x] Kubernetes automatically schedules a DaemonSet pod on `worker-4`
- [ ] You must run `kubectl rollout restart daemonset` to pick up the new node
- [ ] A new DaemonSet must be created for the new node

**Q4. A CronJob with schedule `0 */6 * * *` runs:**
- [ ] Every 6 minutes
- [x] Every 6 hours (at minute 0)
- [ ] 6 times per second
- [ ] Once daily at 6:00 AM

**Q5. Which Job field controls the maximum number of pods that can run in parallel at any time?**
- [ ] `completions`
- [x] `parallelism`
- [ ] `backoffLimit`
- [ ] `activeDeadlineSeconds`

**Q6. An init container in a Pod fails repeatedly. What happens to the main container?**
- [x] The main container never starts; Kubernetes keeps restarting the init container until it succeeds or `restartPolicy: Never` is set
- [ ] The main container starts immediately; init containers are advisory only
- [ ] The entire Pod is deleted and replaced
- [ ] The init container failure is ignored after 3 retries and the main container starts anyway

**Q7. The sidecar pattern uses a second container in the same Pod to:**
- [ ] Replace the main container if it crashes
- [ ] Provide a separate network namespace for isolation
- [x] Augment the main container — e.g., a log-shipping agent or service mesh proxy running alongside it
- [ ] Gate startup until a dependency is ready (that is the init container pattern)

**Q8. A Job finishes successfully. By default, the completed pods are:**
- [ ] Deleted immediately by the garbage collector
- [x] Kept in `Completed` state until the Job is deleted or `ttlSecondsAfterFinished` elapses
- [ ] Restarted automatically because `restartPolicy: Always` is the default for Jobs
- [ ] Converted to long-running pods by the controller manager
