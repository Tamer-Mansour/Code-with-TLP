# ConfigMaps and Secrets

Keep config and credentials out of container images. K8s gives you two objects: **ConfigMap** for non-sensitive config, **Secret** for sensitive.

## ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
data:
  log_level: info
  feature_x_enabled: "true"
  config.toml: |
    [server]
    port = 8080
    workers = 4
```

Use it three ways:

```yaml
spec:
  containers:
  - name: web
    env:
    - name: LOG_LEVEL
      valueFrom: { configMapKeyRef: { name: web-config, key: log_level } }

    envFrom:
    - configMapRef: { name: web-config }    # all keys as env vars

    volumeMounts:
    - name: cfg
      mountPath: /etc/app                   # files under /etc/app/log_level, /etc/app/config.toml
  volumes:
  - name: cfg
    configMap: { name: web-config }
```

## Secret

Same shape, base64-encoded values:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: cG9zdGdyZXM=      # echo -n postgres | base64
  password: c2VjcmV0
```

Or `stringData:` to write plain text (the API encodes for you):

```yaml
stringData:
  username: postgres
  password: secret
```

Mount the same way:

```yaml
env:
- name: DB_PASSWORD
  valueFrom: { secretKeyRef: { name: db-credentials, key: password } }
```

## Secret is not actually secret

By default, Secrets are stored **base64-encoded**, not encrypted. Anyone with API access to the namespace can read them. For real protection:

- Enable **encryption at rest** in the API server.
- Use **External Secrets Operator** to pull from AWS Secrets Manager, Vault, GCP Secret Manager.
- Use **SealedSecrets** or **SOPS** to encrypt secrets in git.
- Apply **RBAC** so only the right service accounts can read them.

## Reload on change

ConfigMap and Secret updates **do not automatically restart pods**. If you change a value:

- Files mounted as volumes update within ~1 minute (kubelet sync).
- Env vars require pod restart.

To force a rollout on ConfigMap change, change a label on the Deployment template (or use `kubectl rollout restart deploy/web`).

A common trick: include a hash of the config in the deployment annotations so updates trigger a rollout automatically.

## Best practice

- One ConfigMap per service. Don't share across services.
- Use **immutable** ConfigMaps/Secrets (`immutable: true`) — kubelet skips watching them, reduces API server load on large clusters.
- Don't put secrets in environment variables if you can help it — they leak via `kubectl describe`, env dumps, error reports.
- Use a secrets manager for anything truly sensitive. Native Secrets are convention, not protection.

## NamespaceQuotas and ResourceLimits

Defense against runaway workloads:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    pods: "50"
```

Pair with **LimitRange** to set default request/limit per container, so devs can't deploy unbounded pods.
