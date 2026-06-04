# Quiz: Kubernetes Networking

**Q1. In Kubernetes, which DNS name resolves to a Service named `api` in the `production` namespace?**
- [ ] `api.cluster.local`
- [ ] `api.production.cluster.local`
- [x] `api.production.svc.cluster.local`
- [ ] `production.api.svc.cluster.local`

**Q2. A ClusterIP Service:**
- [x] Is only reachable from within the cluster via a stable virtual IP
- [ ] Exposes a port on every node in the cluster
- [ ] Provisions an external cloud load balancer automatically
- [ ] Routes traffic based on HTTP host headers

**Q3. You deploy an NGINX Ingress controller and create an Ingress resource. What does the Ingress controller use to route external HTTP traffic to different backend Services?**
- [ ] Pod IP addresses stored in etcd
- [x] The `host` and `path` rules defined in the Ingress resource
- [ ] NodePort numbers assigned automatically to each Service
- [ ] Environment variables injected into each container

**Q4. You apply a NetworkPolicy that selects a set of pods and defines `policyTypes: [Ingress]` with no `ingress` rules. What is the effect?**
- [ ] All ingress traffic is allowed because no rules means no restriction
- [ ] The policy is invalid and rejected by the API server
- [x] All ingress traffic to the selected pods is denied
- [ ] Only traffic from outside the cluster is blocked

**Q5. Which CNI plugin characteristic is REQUIRED for NetworkPolicies to have any effect?**
- [ ] The plugin must support IPv6
- [ ] The plugin must be installed in the `kube-system` namespace
- [x] The plugin must implement the NetworkPolicy enforcement spec (e.g., Calico, Cilium)
- [ ] The plugin must use VXLAN encapsulation

**Q6. A LoadBalancer Service and an Ingress resource both expose workloads externally. What is the key advantage of Ingress over LoadBalancer Services?**
- [x] A single Ingress can route to multiple Services based on HTTP host/path rules, avoiding one cloud LB per Service
- [ ] Ingress is cheaper because it uses NodePort under the hood for free
- [ ] LoadBalancer Services require a separate controller; Ingress is built in
- [ ] Ingress supports UDP while LoadBalancer Services support only TCP

**Q7. All pods in a Kubernetes cluster can communicate with each other without NAT. This is called:**
- [ ] The service mesh model
- [ ] CNI isolation mode
- [x] The Kubernetes flat network model
- [ ] Pod IP masquerading

**Q8. EndpointSlices are introduced to replace Endpoints objects. The primary motivation is:**
- [ ] Better security by hiding pod IPs from etcd
- [ ] Support for UDP services
- [x] Scalability — Endpoints objects become very large in clusters with many pods, causing excessive API server load on each update
- [ ] Automatic TLS for intra-cluster communication
