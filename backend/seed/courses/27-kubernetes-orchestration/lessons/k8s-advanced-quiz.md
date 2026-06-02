# Quiz: Advanced Kubernetes

**Q1. What is the purpose of a Pod Disruption Budget (PDB)?**
- [ ] Limits the CPU a pod can consume
- [x] Ensures a minimum number of pods remain available during voluntary disruptions (node drain, upgrades)
- [ ] Controls how many pods can be scheduled on a single node
- [ ] Sets the maximum number of pods in a namespace

**Q2. A DaemonSet is best used for which type of workload?**
- [ ] A stateful database that needs stable storage per replica
- [ ] A batch job that runs once and exits
- [x] A log collector that must run on every node in the cluster
- [ ] A web API that needs to scale with traffic

**Q3. Which Helm command rolls back a release to the previous revision?**
- [ ] `helm downgrade`
- [ ] `helm revert`
- [x] `helm rollback`
- [ ] `helm undo`

**Q4. A Pod with no resource requests or limits is assigned which QoS class?**
- [ ] Guaranteed
- [ ] Burstable
- [x] BestEffort
- [ ] Limited

**Q5. What is the key difference between a StatefulSet and a Deployment?**
- [x] StatefulSet pods have stable, ordered identities and per-pod PVCs; Deployment pods are interchangeable
- [ ] StatefulSet scales faster than Deployment
- [ ] Deployment supports rolling updates; StatefulSet does not
- [ ] StatefulSet requires a LoadBalancer Service

**Q6. In RBAC, which combination grants read-only access cluster-wide?**
- [ ] Role + RoleBinding
- [x] ClusterRole `view` + ClusterRoleBinding
- [ ] Role `view` + ClusterRoleBinding
- [ ] ClusterRole + RoleBinding in kube-system

**Q7. HPA scale-down is delayed by configuring which field?**
- [ ] `periodSeconds`
- [ ] `failureThreshold`
- [x] `stabilizationWindowSeconds` in `behavior.scaleDown`
- [ ] `maxUnavailable`

**Q8. A NetworkPolicy with `policyTypes: [Ingress]` and no `ingress` rules does what?**
- [ ] Allows all ingress to selected pods
- [x] Denies all ingress to selected pods
- [ ] Has no effect until ingress rules are added
- [ ] Blocks only external traffic, not intra-cluster
