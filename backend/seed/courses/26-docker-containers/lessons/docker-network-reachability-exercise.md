# Exercise: Docker Network Reachability Simulator

Put your Docker networking knowledge to work by simulating container-to-container reachability across user-defined bridge networks.

## Background

Docker's networking model has one critical rule: **two containers can communicate if and only if they share at least one network**.

- Containers on the **default bridge** network can reach each other only by IP address.
- Containers on the **same user-defined bridge** network can reach each other by container name via Docker's embedded DNS.
- Containers on **different user-defined networks** with no overlap cannot communicate at all — they are fully isolated.
- A container can be connected to **multiple networks** simultaneously, making it a bridge between otherwise-isolated groups.

```bash
# Connect an existing container to an additional network
docker network connect backend api
```

After this command, `api` is reachable from both its original network and `backend`.

## What You'll Practice

- Modeling network topology as a set membership problem
- Understanding Docker's isolation-by-default principle
- Reasoning about which containers can talk to each other

## Further Reading

- **Docker Official Documentation — Networking overview**: [https://docs.docker.com/get-started/](https://docs.docker.com/get-started/)
- **Play with Docker Classroom**: [https://training.play-with-docker.com/](https://training.play-with-docker.com/) has interactive networking labs you can run in-browser.
