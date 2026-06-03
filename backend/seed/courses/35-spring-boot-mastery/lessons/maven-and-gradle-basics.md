# Maven and Gradle Basics

Every Spring Boot project is managed by a **build tool**. The build tool handles three essential jobs: declaring dependencies (jars), compiling and testing your code, and packaging the final artifact. The two dominant choices in the Java ecosystem are **Maven** and **Gradle**. Spring Initializr supports both; this course uses Maven, but you will encounter Gradle in real projects, so understanding both is worthwhile.

## Maven

Maven is driven by a single XML file at the project root: `pom.xml` (Project Object Model). It follows a strict **convention-over-configuration** philosophy — put your code in `src/main/java`, your tests in `src/test/java`, and Maven knows exactly what to do without further instruction.

### Minimal Spring Boot pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
             https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- Inherit Spring Boot's managed dependency versions -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.0</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>jar</packaging>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <!-- Starter for building REST APIs -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Test slice: JUnit 5, Mockito, MockMvc -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <!-- Repackages jar into a self-contained executable -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

Notice there are **no explicit version numbers** on the starters. The `spring-boot-starter-parent` acts as a bill of materials (BOM), locking every managed dependency to a tested, compatible set. You only override a version if you have a specific reason.

### Common Maven commands

```bash
# Download dependencies, compile, test, package
mvn package

# Skip tests (useful during rapid iteration — not in CI)
mvn package -DskipTests

# Run the app directly without packaging first
mvn spring-boot:run

# Clean the target/ directory and rebuild from scratch
mvn clean package

# Show the full resolved dependency tree
mvn dependency:tree
```

## Gradle

Gradle replaces XML with a **Groovy** or **Kotlin** DSL script (`build.gradle` / `build.gradle.kts`). It evaluates only what changed, making incremental builds significantly faster on large projects.

### Equivalent Spring Boot build.gradle (Kotlin DSL)

```kotlin
plugins {
    id("org.springframework.boot") version "3.3.0"
    id("io.spring.dependency-management") version "1.1.5"
    kotlin("jvm") version "1.9.24"   // omit if using plain Java
    java
}

group = "com.example"
version = "0.0.1-SNAPSHOT"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

### Common Gradle commands

```bash
# Build and test (uses the Gradle wrapper)
./gradlew build          # Linux / macOS
gradlew.bat build        # Windows

# Run the app
./gradlew bootRun

# Skip tests
./gradlew build -x test

# Show dependency tree
./gradlew dependencies --configuration runtimeClasspath
```

Always commit the **Gradle wrapper** (`gradlew`, `gradlew.bat`, `gradle/wrapper/`) to version control so every developer and CI server uses the same Gradle version without a manual install.

## Maven vs Gradle at a glance

| Aspect | Maven | Gradle |
|---|---|---|
| Config format | XML (`pom.xml`) | Groovy or Kotlin DSL (`build.gradle`) |
| Build speed | Moderate | Faster (incremental + build cache) |
| Learning curve | Lower — very opinionated | Higher — more flexible |
| Spring Initializr default | Yes | Optional |
| Plugin ecosystem | Mature, very large | Growing rapidly |
| Wrapper | `mvnw` | `gradlew` |

For this course and for most beginner/intermediate Spring Boot projects, **Maven is the pragmatic choice** — documentation and Stack Overflow answers overwhelmingly target it.

## Dependency scopes

Both tools support scopes that control when a dependency is on the classpath:

- `compile` / `implementation` — always on the classpath (compile + runtime).
- `test` / `testImplementation` — only during test compilation and execution.
- `provided` / `compileOnly` — needed to compile but provided by the runtime (e.g., a servlet container).
- `runtime` / `runtimeOnly` — not needed for compilation but needed at runtime (e.g., a JDBC driver).

## Common mistakes

- **Forgetting `spring-boot-starter-parent`** — dependency versions become your responsibility and conflicts appear immediately.
- **Hardcoding versions on managed starters** — override only when there is a genuine need; otherwise you break the tested compatibility matrix.
- **Committing without the wrapper** — teammates get "Gradle not found" errors. Always include `mvnw`/`gradlew` in the repository.
- **Running `mvn install` habitually** — `install` copies the jar to your local `.m2` cache, which is only needed for multi-module inter-module references. Prefer `mvn package` or `mvn verify` for single-module apps.

## Summary

Maven and Gradle are the two build tools you will encounter throughout the Spring ecosystem. Maven's opinionated XML structure and Spring Boot's `starter-parent` make it the lowest-friction starting point; Gradle's incremental engine shines in larger codebases. Whichever you choose, the wrapper script is the right entry point — it guarantees a reproducible build on any machine.
