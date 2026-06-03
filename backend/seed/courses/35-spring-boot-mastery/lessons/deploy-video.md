# Video: Deploying Spring Boot

This video walks through packaging a Spring Boot 3 application as an executable JAR and deploying it to a Linux server (or cloud VM), covering environment configuration, process management, and basic health verification.

## What you'll learn

- Building a production JAR with `mvn package -DskipTests` and the Spring Boot Maven plugin
- Externalising configuration via `application-prod.properties` and environment variables (`SPRING_DATASOURCE_URL`, `SERVER_PORT`)
- Running the JAR as a background service with `systemd` on Ubuntu/Debian
- Setting JVM memory flags (`-Xms256m -Xmx512m`) and enabling the Actuator health endpoint
- Verifying deployment with `curl http://localhost:8080/actuator/health`
- Rolling back by swapping the JAR symlink and restarting the service

## Key takeaways

- Always build with the `spring-boot-maven-plugin` — it produces a self-contained fat JAR
- Store secrets in environment variables, never in committed property files
- A `systemd` unit file ensures the app restarts automatically after a server reboot
- The `/actuator/health` endpoint is your first signal that the app started correctly

The link in this lesson opens a curated YouTube search surfacing free, full-length tutorials from channels such as freeCodeCamp and Amigoscode on deploying Spring Boot applications end to end.

## Follow-along checklist

- [ ] Run `mvn package -DskipTests` and confirm `target/*.jar` exists
- [ ] Set `SPRING_PROFILES_ACTIVE=prod` before launching
- [ ] Start the app: `java -jar target/app.jar` and check console output
- [ ] Hit `curl http://localhost:8080/actuator/health` — expect `{"status":"UP"}`
- [ ] Create a `/etc/systemd/system/myapp.service` unit file and enable it
