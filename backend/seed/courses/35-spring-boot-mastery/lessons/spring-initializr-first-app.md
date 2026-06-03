# Your First App with Spring Initializr

**Spring Initializr** (https://start.spring.io) is the official project generator for Spring Boot. In under two minutes it produces a fully wired Maven project — correct `pom.xml`, package structure, main class, and test stub — ready to import into any IDE.

## Generating the Project

Open https://start.spring.io and fill in the form:

| Field | Value to use |
|---|---|
| Project | Maven |
| Language | Java |
| Spring Boot | 3.x (latest stable) |
| Group | `com.example` |
| Artifact | `demo` |
| Packaging | Jar |
| Java | 17 |
| Dependencies | **Spring Web** |

Click **Generate** to download `demo.zip`, then extract it.

You can do the same thing from the terminal using the Initializr REST API:

```bash
curl -o demo.zip \
  "https://start.spring.io/starter.zip?type=maven-project&language=java&bootVersion=3.3.0&baseDir=demo&groupId=com.example&artifactId=demo&name=demo&packaging=jar&javaVersion=17&dependencies=web"
unzip demo.zip
cd demo
```

## Project Layout

After extraction the tree looks like this:

```
demo/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/com/example/demo/
    │   │   └── DemoApplication.java
    │   └── resources/
    │       └── application.properties
    └── test/
        └── java/com/example/demo/
            └── DemoApplicationTests.java
```

Everything under `src/main/java` is production code; `src/test/java` is for tests. `application.properties` is where you configure the app (port, datasource, etc.).

## The Generated Main Class

```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

`@SpringBootApplication` is a meta-annotation that combines three annotations:

- `@Configuration` — marks this class as a source of bean definitions
- `@EnableAutoConfiguration` — tells Spring Boot to wire beans based on the classpath
- `@ComponentScan` — scans the current package and sub-packages for components

Do not move this class out of its package root — `@ComponentScan` starts from wherever `DemoApplication` lives.

## Adding a REST Endpoint

Create a new file in the same package:

```java
package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello(@RequestParam(defaultValue = "World") String name) {
        return "Hello, " + name + "!";
    }
}
```

`@RestController` combines `@Controller` and `@ResponseBody`, so the return value is written directly to the HTTP response body as a string (or JSON for objects).

## Running the Application

```bash
./mvnw spring-boot:run          # macOS / Linux
mvnw.cmd spring-boot:run        # Windows
```

Spring Boot starts an embedded Tomcat server on port 8080 by default. Test it immediately:

```bash
curl http://localhost:8080/hello
# Hello, World!

curl "http://localhost:8080/hello?name=Spring"
# Hello, Spring!
```

To change the port, add one line to `src/main/resources/application.properties`:

```properties
server.port=9090
```

## Key Parts of the Generated pom.xml

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.0</version>
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

`spring-boot-starter-parent` manages all dependency versions, so you never specify a version tag for any official Spring Boot starter — the parent BOM keeps them consistent.

## Common Mistakes

- **Wrong Java version in the pom.xml** — the Initializr sets `<java.version>17</java.version>` inside `<properties>`. If your local `JAVA_HOME` points to Java 11 the build fails. Run `java -version` to verify.
- **Moving `DemoApplication` to a sub-package** — `@ComponentScan` will no longer find controllers or services in sibling packages. Keep the main class at the root of your group package.
- **Editing `pom.xml` dependency versions manually** — let `spring-boot-starter-parent` control versions. Overriding them independently risks incompatible combinations.
- **Forgetting to add a dependency** — if you need JPA or Security later, re-visit start.spring.io, generate with the new dependency, and copy the `<dependency>` block into your existing `pom.xml`.

## Summary

Spring Initializr generates a production-ready Maven project skeleton in seconds; the embedded Tomcat, auto-configuration, and the `@SpringBootApplication` entry point mean you can go from a blank machine to a running HTTP endpoint with a single `mvnw spring-boot:run` command.
