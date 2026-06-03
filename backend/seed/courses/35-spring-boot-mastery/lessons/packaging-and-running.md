# Packaging and Running the Executable JAR

One of Spring Boot's most practical features is its **executable "fat JAR"** (also called an uber-JAR). A single `java -jar` command starts the entire application — no application server, no WAR deployment, no classpath setup required. This lesson covers how the fat JAR is built, what it contains, and how to run and configure it in different environments.

## How the Fat JAR is Built

The `spring-boot-maven-plugin` declared in your `pom.xml` hooks into Maven's `package` phase and **repackages** the standard thin JAR into a self-contained artifact. It embeds:

- your compiled classes under `BOOT-INF/classes/`
- all runtime dependencies as nested JARs under `BOOT-INF/lib/`
- a custom class loader (`JarLauncher`) that knows how to load from nested JARs
- a `META-INF/MANIFEST.MF` that points to `JarLauncher` as the entry point

The plugin declaration (already present in every Spring Initializr project) is all you need:

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

## Building the JAR

```bash
# Clean any previous build output, then compile, test, and package
mvn clean package

# Skip tests when you only want the artifact quickly (not in CI)
mvn clean package -DskipTests
```

Maven writes the artifact to `target/` with the naming pattern `<artifactId>-<version>.jar`:

```
target/
  demo-0.0.1-SNAPSHOT.jar          ← fat JAR (executable)
  demo-0.0.1-SNAPSHOT.jar.original ← thin JAR before repackaging
```

The `.original` file is the plain thin JAR produced before the plugin runs — keep the fat JAR, ignore the other.

## Running the JAR

```bash
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

Spring Boot prints the familiar banner and the embedded Tomcat starts on port `8080` by default.

### Overriding Configuration at Runtime

Because Spring Boot externalises configuration, you can pass properties directly on the command line without rebuilding:

```bash
# Change the server port
java -jar target/demo-0.0.1-SNAPSHOT.jar --server.port=9090

# Activate a Spring profile
java -jar target/demo-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod

# Point to an external config file
java -jar target/demo-0.0.1-SNAPSHOT.jar \
  --spring.config.location=file:/opt/app/config/application-prod.properties
```

Environment variables work just as well, which is useful in Docker and CI pipelines:

```bash
export SERVER_PORT=9090
export SPRING_PROFILES_ACTIVE=prod
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

Spring Boot maps environment variable names to property keys by converting them to lowercase and replacing `_` with `.` (e.g., `SERVER_PORT` → `server.port`).

## Property Source Priority

Spring Boot evaluates multiple property sources in a fixed order. Higher items in the table win:

| Priority | Source |
|---|---|
| 1 (highest) | Command-line arguments (`--key=value`) |
| 2 | `SPRING_APPLICATION_JSON` environment variable |
| 3 | OS environment variables |
| 4 | `application-{profile}.properties` / `.yml` (outside jar) |
| 5 | `application.properties` / `.yml` (outside jar) |
| 6 | `application-{profile}.properties` / `.yml` (inside jar) |
| 7 | `application.properties` / `.yml` (inside jar) |
| 8 (lowest) | `@PropertySource` annotations |

This hierarchy means you can ship a jar with safe defaults baked in and override only the sensitive values (database passwords, API keys) via environment variables at deploy time — no rebuild required.

## Inspecting the JAR Contents

To verify what was packaged, use the standard `jar` tool (part of the JDK):

```bash
# List the top-level entries
jar tf target/demo-0.0.1-SNAPSHOT.jar | head -30

# Confirm the manifest entry point
unzip -p target/demo-0.0.1-SNAPSHOT.jar META-INF/MANIFEST.MF
```

The manifest should show:

```
Main-Class: org.springframework.boot.loader.JarLauncher
Start-Class: com.example.demo.DemoApplication
```

`JarLauncher` sets up the nested-JAR class loader and then delegates to your `Start-Class`.

## Running with a Specific JVM Flags

Pass JVM options before `-jar`:

```bash
# Set heap limits and enable garbage collection logging
java -Xms256m -Xmx512m -verbose:gc \
     -jar target/demo-0.0.1-SNAPSHOT.jar
```

For production it is common to also set the default file encoding and timezone explicitly:

```bash
java -Xms512m -Xmx1g \
     -Dfile.encoding=UTF-8 \
     -Duser.timezone=UTC \
     -jar target/demo-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod
```

## Common Mistakes and Best Practices

- **Forgetting `spring-boot-maven-plugin`** — without it `mvn package` produces a thin JAR that cannot run standalone because dependencies are missing.
- **Shipping `application-prod.properties` inside the JAR** — secrets end up in version control and in the artifact. Keep environment-specific config outside the JAR and inject via environment variables or `--spring.config.location`.
- **Running as root** — always run the application as a dedicated non-root OS user to limit the blast radius of a security vulnerability.
- **Using `mvn spring-boot:run` in production** — that command is for local development only; it compiles on the fly and does not represent the packaged artifact.
- **Ignoring the `.original` file** — it is not executable; always deploy the fat JAR (the one without the `.original` suffix).

## Summary

`mvn clean package` produces a single self-contained executable JAR that embeds Tomcat and all dependencies. Running it with `java -jar` is all that production needs, and Spring Boot's layered property sources let you override any setting at startup without touching the artifact.
