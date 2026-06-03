# Dockerizing a Spring Boot App

Containerizing your Spring Boot service makes it portable and reproducible: the same image runs on your laptop, in CI, and in production. In this lesson you'll package a Spring Boot 3 / Java 17 app built with Maven into a lean, secure Docker image.

## The naive (and wrong) approach

A common first attempt copies the source and builds inside the container in one stage:

```dockerfile
FROM eclipse-temurin:17-jdk
COPY . /app
WORKDIR /app
RUN ./mvnw package
CMD ["java", "-jar", "target/app.jar"]
```

This works, but the image ships the full JDK, Maven, and your source code — often 600 MB+. Worse, any source change busts the dependency cache, forcing Maven to re-download everything on every build.

## Multi-stage builds

A multi-stage `Dockerfile` separates *building* from *running*. The build stage uses a JDK; the final stage keeps only a slim JRE plus the fat JAR.

```dockerfile
# ---- Build stage ----
FROM eclipse-temurin:17-jdk AS build
WORKDIR /app

# Copy only the files needed to resolve dependencies first
COPY .mvn/ .mvn/
COPY mvnw pom.xml ./
RUN ./mvnw dependency:go-offline -B

# Now copy sources and build (this layer rebuilds only on code change)
COPY src ./src
RUN ./mvnw clean package -DskipTests -B

# ---- Runtime stage ----
FROM eclipse-temurin:17-jre AS runtime
WORKDIR /app

# Run as a non-root user
RUN useradd -r -u 1001 appuser
USER appuser

COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

Copying `pom.xml` before `src` lets Docker cache the dependency layer, so subsequent builds are fast.

## Build and run

```bash
# Build the image (tag it)
docker build -t myorg/spring-app:1.0 .

# Run it, mapping container port 8080 to host 8080
docker run --rm -p 8080:8080 myorg/spring-app:1.0
```

Override config without rebuilding by passing environment variables — Spring Boot maps `SERVER_PORT` to `server.port`:

```bash
docker run --rm -p 9090:9090 \
  -e SERVER_PORT=9090 \
  -e SPRING_PROFILES_ACTIVE=prod \
  myorg/spring-app:1.0
```

## Base image comparison

| Base image | Contents | Typical size | Use for |
|---|---|---|---|
| `eclipse-temurin:17-jdk` | Full JDK + tools | ~450 MB | Build stage |
| `eclipse-temurin:17-jre` | JRE only | ~270 MB | Standard runtime |
| `eclipse-temurin:17-jre-alpine` | JRE on musl libc | ~170 MB | Smaller, watch for native-lib issues |

## Best practices

- **Use a `.dockerignore`** to keep `target/`, `.git/`, and IDE files out of the build context:

  ```
  target/
  .git/
  .idea/
  *.iml
  ```

- **Never run as root.** A non-root `USER` limits the blast radius of a compromise.
- **Pin tags** (`17-jre`, not `latest`) for reproducible builds.
- **Skip tests in the image build** (`-DskipTests`) and run them earlier in CI instead.
- **Add a health check** so orchestrators know the app is alive — pair it with `spring-boot-starter-actuator`:

  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8080/actuator/health || exit 1
  ```

### Common mistakes

- Copying `src` before `pom.xml`, which destroys dependency-layer caching.
- Shipping the JDK in production instead of a JRE.
- Hardcoding ports/profiles in the image rather than passing them as environment variables.

> **Tip:** Spring Boot's Maven plugin can build an optimized image without a Dockerfile via `./mvnw spring-boot:build-image`, which uses Cloud Native Buildpacks and layered JARs.

## Summary

Use a multi-stage Dockerfile to build with a JDK and run on a slim JRE as a non-root user, ordering layers so dependencies cache well. Configure the running container through environment variables, not rebuilds.
