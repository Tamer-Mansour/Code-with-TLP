# Quiz: Kubernetes Workloads

**Q1. What is the atomic unit of scheduling in Kubernetes?**
- [ ] Container
- [x] Pod
- [ ] Deployment
- [ ] ReplicaSet

**Q2. Which field in a Deployment spec controls how many old pods can be unavailable during a rolling update?**
- [ ] `maxSurge`
- [x] `maxUnavailable`
- [ ] `minReadySeconds`
- [ ] `revisionHistoryLimit`

**Q3. A ReplicaSet ensures the cluster always has exactly N running pods. What happens if you manually delete a pod managed by a ReplicaSet?**
- [ ] The pod is gone permanently and the ReplicaSet does nothing
- [ ] The ReplicaSet deletes the entire deployment
- [x] The ReplicaSet detects the pod is missing and creates a replacement automatically
- [ ] The node is cordoned to prevent further scheduling

**Q4. Which workload resource is best suited for a log-shipper that must run on every node, including nodes added in the future?**
- [ ] Deployment with `replicas: 1`
- [x] DaemonSet
- [ ] StatefulSet
- [ ] CronJob

**Q5. An init container in a Pod:**
- [ ] Runs alongside the main containers to provide shared utilities
- [ ] Is used for health checks before liveness probes fire
- [x] Runs to completion before any main containers start, enabling setup tasks
- [ ] Restarts on every request handled by the main container

**Q6. A Job with `completions: 5` and `parallelism: 2` will:**
- [ ] Run 2 pods, each completing 5 tasks
- [x] Run up to 2 pods in parallel until a total of 5 pods have succeeded
- [ ] Run 5 pods all at once and fail if any exit non-zero
- [ ] Run 5 sequential batches of 2 pods each

**Q7. You want to roll back a Deployment to the previous version. Which command is correct?**
- [ ] `kubectl rollback deployment/api`
- [x] `kubectl rollout undo deployment/api`
- [ ] `kubectl apply -f previous.yaml --force`
- [ ] `kubectl scale deployment/api --replicas=0`

**Q8. Which statement about StatefulSets is TRUE?**
- [ ] StatefulSet pods are interchangeable and can be replaced in any order
- [x] StatefulSet pods have stable network identities (e.g., `pod-0`, `pod-1`) and ordered rollout/termination
- [ ] StatefulSets do not support persistent storage
- [ ] StatefulSet pods all share a single PersistentVolumeClaim
