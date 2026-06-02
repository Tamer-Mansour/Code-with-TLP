# Quiz: Docker Compose and Networking

**Q1. By default, what network do services in a Compose file join?**
- [ ] The host network
- [x] A project-scoped bridge network created automatically by Compose
- [ ] The `none` network
- [ ] The global Docker `bridge` network

**Q2. If two services are defined in the same `docker-compose.yml`, how does service A reach service B?**
- [ ] Using the container ID as the hostname
- [ ] Using the IP address only (DNS is not available)
- [x] Using the service name as the hostname
- [ ] By publishing ports with `-p` to the host

**Q3. Which command removes containers AND their named volumes?**
- [ ] `docker compose down`
- [ ] `docker compose stop`
- [x] `docker compose down -v`
- [ ] `docker volume prune`

**Q4. What is the key difference between a named volume and a bind mount?**
- [ ] Named volumes are faster than bind mounts
- [ ] Bind mounts survive `docker compose down -v`; named volumes do not
- [x] Named volumes are managed by Docker; bind mounts reference a host path
- [ ] Only named volumes support databases

**Q5. In a Compose file with two custom networks (`frontend` and `backend`), a service only listed under `backend:` cannot be reached by services only in `frontend:`. True or false?**
- [x] True
- [ ] False

**Q6. What does `EXPOSE 8080` in a Dockerfile do?**
- [ ] Publishes port 8080 from the container to the host
- [ ] Opens port 8080 in the host firewall
- [x] Documents that the container listens on 8080 — does NOT publish it
- [ ] Forces Compose to map port 8080:8080 automatically
