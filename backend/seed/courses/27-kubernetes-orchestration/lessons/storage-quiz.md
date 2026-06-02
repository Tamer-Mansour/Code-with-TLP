# Quiz: Kubernetes Storage

**Q1. Which object does a developer create to request storage in Kubernetes?**
- [ ] PersistentVolume
- [x] PersistentVolumeClaim
- [ ] StorageClass
- [ ] VolumeMount

**Q2. A PVC is stuck in "Pending" state. What is the most likely cause?**
- [ ] The pod using it has crashed
- [ ] The namespace is out of ResourceQuota
- [x] No PersistentVolume matches the PVC's StorageClass, access mode, or size
- [ ] The container image cannot be pulled

**Q3. Which access mode allows multiple nodes to read AND write simultaneously?**
- [ ] ReadWriteOnce (RWO)
- [ ] ReadOnlyMany (ROX)
- [x] ReadWriteMany (RWX)
- [ ] ReadWriteOncePod (RWOP)

**Q4. With reclaimPolicy: Delete on a StorageClass, what happens to the underlying disk when a PVC is deleted?**
- [ ] It is retained and must be cleaned up manually
- [ ] It is recycled and made available for new claims
- [x] It is deleted along with the PersistentVolume
- [ ] It is snapshotted before deletion

**Q5. What does volumeBindingMode: WaitForFirstConsumer do?**
- [ ] Prevents any binding until an admin approves
- [x] Delays PV provisioning until a Pod is scheduled, so it respects zone topology
- [ ] Makes the PVC wait for a matching PV to be created manually
- [ ] Binds the PVC only to the first available node

**Q6. Which QoS class does a Pod get when all containers have requests equal to limits?**
- [ ] BestEffort
- [ ] Burstable
- [x] Guaranteed
- [ ] Critical
