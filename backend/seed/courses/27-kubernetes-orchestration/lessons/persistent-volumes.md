# Persistent Volumes and Claims

Containers are ephemeral — their filesystem disappears when the container restarts. Kubernetes provides a storage abstraction layer so applications can request durable storage without knowing the underlying infrastructure.

## The Three-Layer Abstraction

```
Administrator provisions        Developer requests        Pod uses
PersistentVolume (PV)    →     PersistentVolumeClaim →   Volume mount
  (actual disk/NFS/cloud)      (PVC)
```

- **PersistentVolume (PV)** — a piece of storage provisioned by an admin or dynamically by a StorageClass.
- **PersistentVolumeClaim (PVC)** — a request for storage (size, access mode). Bound to a PV.
- **Volume mount** — the PVC is mounted into a Pod at a specific path.

## Access Modes

| Mode              | Abbreviation | Meaning                               |
|-------------------|--------------|---------------------------------------|
| ReadWriteOnce     | RWO          | One node can mount read/write         |
| ReadOnlyMany      | ROX          | Many nodes can mount read-only        |
| ReadWriteMany     | RWX          | Many nodes can mount read/write       |
| ReadWriteOncePod  | RWOP         | One pod only (K8s 1.22+)             |

Most cloud block volumes (EBS, Persistent Disk) are RWO only. NFS and cloud file shares support RWX.

## Creating a PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
  namespace: production
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 20Gi
```

## Using a PVC in a Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: db
spec:
  containers:
  - name: postgres
    image: postgres:16
    env:
    - name: PGDATA
      value: /var/lib/postgresql/data/pgdata
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: data-pvc
```

## StorageClasses — Dynamic Provisioning

A **StorageClass** defines the provisioner and parameters for dynamic PV creation. When a PVC references a StorageClass, K8s automatically creates a matching PV.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

- `reclaimPolicy: Retain` — the PV is kept when the PVC is deleted (safe for databases).
- `reclaimPolicy: Delete` — the PV (and underlying disk) is deleted with the PVC.
- `volumeBindingMode: WaitForFirstConsumer` — delay provisioning until a Pod is scheduled (respects zone topology).

## Reclaim Policies Compared

| Policy  | On PVC Delete           | Use Case                 |
|---------|-------------------------|--------------------------|
| Retain  | PV stays, needs manual cleanup | Production databases   |
| Delete  | PV and disk deleted     | Ephemeral test clusters  |
| Recycle | Scrubs and makes available (deprecated) | —            |

## Checking Status

```bash
kubectl get pvc -n production          # Bound / Pending / Lost
kubectl get pv                         # Cluster-wide; shows capacity and status
kubectl describe pvc data-pvc -n prod  # Events if stuck in Pending
```

A PVC stuck in `Pending` usually means no PV matches its StorageClass, access mode, or size.
