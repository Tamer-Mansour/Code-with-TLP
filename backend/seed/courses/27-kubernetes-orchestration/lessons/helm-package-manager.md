# Helm — Kubernetes Package Manager

**Helm** is the package manager for Kubernetes. It lets you define, install, and upgrade complex Kubernetes applications as versioned, reusable packages called **charts**.

## Core Concepts

| Term       | Meaning                                                                 |
|------------|-------------------------------------------------------------------------|
| Chart      | A directory of YAML templates + a `Chart.yaml` describing the package  |
| Release    | A deployed instance of a chart in a cluster                            |
| Revision   | Each install or upgrade creates a new numbered revision                 |
| Repository | A collection of charts, hosted as an HTTP server                       |
| Values     | Configuration variables rendered into templates                        |

## Installing Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

## Common Commands

```bash
# Add a chart repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Search for a chart
helm search repo bitnami/postgresql

# Install a chart (creates a Release named "pg")
helm install pg bitnami/postgresql \
  --namespace production \
  --create-namespace \
  --set auth.postgresPassword=secret123

# See deployed releases
helm list -n production

# Upgrade a release with new values
helm upgrade pg bitnami/postgresql -n production \
  --set primary.resources.limits.memory=1Gi

# Roll back to revision 1
helm rollback pg 1 -n production

# Uninstall a release
helm uninstall pg -n production
```

## Chart Structure

```
mychart/
  Chart.yaml          # name, version, description, dependencies
  values.yaml         # default configuration values
  templates/
    deployment.yaml   # template files using Go text/template + Helm functions
    service.yaml
    _helpers.tpl      # reusable template snippets
  charts/             # bundled sub-charts (dependencies)
```

## values.yaml Example

```yaml
replicaCount: 2
image:
  repository: ghcr.io/myorg/api
  tag: "1.4.0"
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 80
resources:
  limits:
    cpu: "1"
    memory: 512Mi
```

## Template Example

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
      - name: api
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
```

## Overriding Values at Deploy Time

```bash
# Override with --set (simple values)
helm install api ./mychart --set replicaCount=3

# Override with a values file (complex overrides)
helm install api ./mychart -f prod-values.yaml
```

## Helm Secrets (Sensitive Values)

Never store secrets in `values.yaml`. Use:
- **helm-secrets** plugin (encrypts with SOPS/age/GPG).
- External Secrets Operator to pull secrets from Vault / AWS Secrets Manager.
- Kubernetes Secrets pre-created and referenced by name.

## Why Helm Over Plain kubectl?

- Atomic installs and rollbacks (revision history).
- Templating removes repetition across environments.
- Charts from public repos give you production-grade defaults instantly.
- Helm hooks (`pre-install`, `post-upgrade`) run jobs at lifecycle events (e.g., database migrations before upgrade).
