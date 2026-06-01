# kubectl Essentials

`kubectl` is the universal CLI for K8s clusters.

## Configuration

```bash
kubectl config get-contexts        # available clusters
kubectl config use-context prod    # switch
kubectl config current-context
kubectl config set-context --current --namespace=staging   # default ns
```

`~/.kube/config` holds your cluster connections. `kubectx` and `kubens` (CLI tools) make switching faster.

## Read

```bash
kubectl get pods
kubectl get pods -A                # all namespaces
kubectl get pods -o wide           # with node info
kubectl get pods -l app=web        # label selector
kubectl get deploy,svc,ingress     # multiple kinds
kubectl get pods -w                # watch (live updates)
kubectl get pod web-abc -o yaml    # full manifest
kubectl describe pod web-abc       # rich human-readable + events
```

`describe` is your first tool when something's wrong — events at the bottom show why a pod isn't starting.

## Apply

```bash
kubectl apply -f deployment.yaml
kubectl apply -f ./manifests/      # all files in a dir
kubectl apply -k ./overlay/        # kustomize
```

`apply` is **declarative** — it computes the diff and updates only what changed. Prefer over `create`.

## Logs and exec

```bash
kubectl logs web-abc
kubectl logs -f web-abc            # follow
kubectl logs --tail=50 web-abc
kubectl logs web-abc -c sidecar    # specific container
kubectl logs -l app=web --tail=20 --prefix    # all matching pods

kubectl exec -it web-abc -- sh
kubectl exec web-abc -- env
```

## Port forward

```bash
kubectl port-forward svc/web 8080:80
```

Now `localhost:8080` reaches the service inside the cluster. Useful for debugging or accessing dashboards.

## Delete

```bash
kubectl delete pod web-abc
kubectl delete -f deployment.yaml
kubectl delete deploy web
kubectl delete pods -l app=web,env=staging
```

Deleting a Pod managed by a Deployment recreates it (the controller fills the gap). To truly delete the workload, delete the Deployment.

## Rollouts

```bash
kubectl rollout status deploy/web
kubectl rollout history deploy/web
kubectl rollout undo deploy/web              # back to previous
kubectl rollout undo deploy/web --to-revision=3
kubectl rollout restart deploy/web           # cycle pods
```

## Scale

```bash
kubectl scale deploy/web --replicas=10
kubectl autoscale deploy/web --min=2 --max=10 --cpu-percent=80
```

## Useful flags

```bash
--dry-run=client -o yaml      # show what would be applied (without sending)
--watch / -w                   # follow updates
--all-namespaces / -A
--namespace ns / -n ns
--selector / -l "key=value,key2=value2"
--field-selector "status.phase=Running"
```

## Plugins worth installing

- **k9s** — full-screen terminal UI.
- **stern** — multi-pod log tailing.
- **kubectx / kubens** — switch context / namespace fast.
- **kustomize** (built into kubectl).
- **helm** — package manager.

## Tip

`kubectl explain pod.spec.containers` documents any field of any resource. Built-in, no internet needed.
