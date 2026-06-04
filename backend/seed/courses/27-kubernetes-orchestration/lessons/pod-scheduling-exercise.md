# Exercise: Pod Scheduling Feasibility Checker

The Kubernetes scheduler uses a **filtering** phase to eliminate nodes that cannot run a pod. The check order is:

1. **Node selector / node affinity** — does the node have all required labels?
2. **Taints and tolerations** — does the pod tolerate every `NoSchedule` / `NoExecute` taint on the node?
3. **Resource availability** — does the node have enough free CPU and memory?

If a node fails any check, the scheduler moves on to the next node. In this exercise you implement that filtering logic.

> **Key insight from research:** The scheduler does NOT create pods. Controllers (ReplicaSet, Deployment) create pods. The scheduler only selects the target node by writing the `nodeName` field, then the **kubelet** on that node actually starts the containers. These three responsibilities — creation, scheduling, execution — are strictly separated.

> **Further reading:** [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) in the official Kubernetes documentation.

See the exercise prompt for the full input/output specification.
