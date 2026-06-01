# Quiz: Kubernetes Basics

**Q1. Which component is the source of truth for cluster state?**
- [ ] kube-apiserver
- [x] etcd
- [ ] kubelet
- [ ] kube-proxy

**Q2. The smallest deployable unit in Kubernetes is:**
- [ ] A container
- [x] A Pod
- [ ] A Deployment
- [ ] A Node

**Q3. Which object manages rolling updates of a set of Pods?**
- [ ] Pod
- [ ] ReplicaSet (alone)
- [x] Deployment
- [ ] StatefulSet

**Q4. To expose a set of pods at a stable virtual IP, use a:**
- [ ] Pod
- [ ] Ingress
- [x] Service
- [ ] ConfigMap

**Q5. Which command applies all YAML files in a folder?**
- [ ] `kubectl run -f ./manifests/`
- [x] `kubectl apply -f ./manifests/`
- [ ] `kubectl create -all ./manifests/`
- [ ] `kubectl manifest apply ./manifests/`

**Q6. Pods that need stable identities and persistent storage are managed by:**
- [ ] Deployment
- [ ] DaemonSet
- [x] StatefulSet
- [ ] Job
