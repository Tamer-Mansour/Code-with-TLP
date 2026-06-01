# Docker CLI Essentials

## Run a container

```bash
docker run nginx                       # run, attach to logs
docker run -d nginx                    # detached
docker run -d -p 8080:80 nginx         # publish container :80 to host :8080
docker run --rm -it ubuntu bash        # interactive, remove on exit
docker run --name web -d -p 80:80 nginx
docker run -e MY_VAR=value alpine printenv
docker run -v $PWD:/app -w /app node:20 npm install
```

Flags:

- `-d` detach
- `-it` interactive + TTY
- `-p host:container` publish port
- `-v host:container` mount volume
- `-w` working directory
- `-e KEY=value` env var
- `--rm` remove on exit
- `--name` give it a name (default is random)

## Manage containers

```bash
docker ps                              # running
docker ps -a                           # all (including stopped)
docker logs <id|name>                  # last logs
docker logs -f web                     # follow
docker exec -it web bash               # shell into a running container
docker stop web
docker rm web
docker restart web
docker stats                           # live CPU/mem
```

## Images

```bash
docker images                          # list local
docker pull alpine:3.20
docker rmi alpine:3.20                 # remove image
docker build -t myapp:1.0 .            # build from Dockerfile
docker tag myapp:1.0 ghcr.io/me/myapp:1.0
docker push ghcr.io/me/myapp:1.0
```

## Cleanup

```bash
docker system df                       # disk usage
docker system prune                    # delete stopped + dangling
docker system prune -a --volumes       # delete EVERYTHING unused
docker container prune
docker image prune
docker volume prune
```

`prune` deletes only **stopped** containers and **dangling** images by default. `-a` is aggressive.

## Volumes vs bind mounts

```bash
# Named volume (Docker-managed)
docker run -v mydata:/var/lib/postgres postgres

# Bind mount (host path)
docker run -v /home/me/code:/app node:20
```

Bind mounts are great for development (live-edit code). Named volumes are right for persistent data (DB files) — they're managed by Docker and easy to back up.

## Networks

```bash
docker network ls
docker network create myapp
docker run -d --network myapp --name db postgres
docker run -d --network myapp --name web -e DB_HOST=db myapp
```

Containers on the same network can reach each other by name — `db:5432` works from `web`.

## Inspect

```bash
docker inspect web                     # full JSON metadata
docker inspect -f '{{.State.Status}}' web
docker top web                          # processes inside
docker port web
```

## Tips

- Tag your images. Pushing `:latest` is fine for development, fragile for production.
- Use `--init` to get a proper PID-1 init process — handles signal forwarding and zombie reaping.
- For local dev, run `docker compose up` instead of dozens of `docker run` flags.
