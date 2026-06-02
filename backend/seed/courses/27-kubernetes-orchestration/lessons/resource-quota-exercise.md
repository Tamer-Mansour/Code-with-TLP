# Exercise: ResourceQuota Admission Check

Given a namespace ResourceQuota and a list of pod resource requests, determine which pods would be **admitted** by the quota and which would be **rejected**.

The quota tracks total CPU requests and total memory requests across all pods in the namespace. Pods are processed in the order given. A pod is rejected if adding its resources would exceed either quota limit.

Read the exercise prompt for full input/output format details.
