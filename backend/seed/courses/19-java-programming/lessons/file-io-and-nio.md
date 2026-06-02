# File I/O and NIO.2

Java's modern file API lives in `java.nio.file` (NIO.2, Java 7+). Prefer it over the old `java.io.File`.

## Path and Files

```java
import java.nio.file.*;

Path p = Path.of("/home/user/data.txt");    // Java 11
Path p2 = Paths.get("/home/user/data.txt"); // Java 7+

System.out.println(p.getFileName());  // data.txt
System.out.println(p.getParent());    // /home/user
System.out.println(p.toAbsolutePath());
```

## Reading files

```java
// All lines at once (small files)
List<String> lines = Files.readAllLines(p);

// All bytes at once
byte[] bytes = Files.readAllBytes(p);

// As a string (Java 11)
String content = Files.readString(p);

// Stream of lines (lazy, for large files)
try (Stream<String> stream = Files.lines(p)) {
    stream.filter(line -> line.startsWith("ERROR"))
          .forEach(System.out::println);
}
```

## Writing files

```java
// Write a string (creates or overwrites)
Files.writeString(p, "Hello\n");

// Write a string and append
Files.writeString(p, "More\n", StandardOpenOption.APPEND);

// Write bytes
Files.write(p, "data".getBytes());

// Write a list of lines
Files.write(p, List.of("line1", "line2"));
```

## BufferedReader / BufferedWriter (character streams)

Use for large files or when you need line-by-line control:

```java
try (BufferedReader reader = Files.newBufferedReader(p)) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}

Path out = Path.of("/tmp/output.txt");
try (BufferedWriter writer = Files.newBufferedWriter(out)) {
    writer.write("Hello");
    writer.newLine();
    writer.write("World");
}
```

## Directory operations

```java
// Create a directory (fails if exists)
Files.createDirectory(Path.of("/tmp/mydir"));

// Create all missing directories
Files.createDirectories(Path.of("/tmp/a/b/c"));

// List directory contents (one level)
try (DirectoryStream<Path> ds = Files.newDirectoryStream(Path.of("/tmp"), "*.txt")) {
    for (Path entry : ds) {
        System.out.println(entry);
    }
}

// Walk the tree
Files.walk(Path.of("/tmp"))
     .filter(Files::isRegularFile)
     .forEach(System.out::println);

// Delete
Files.delete(p);               // throws if not found
Files.deleteIfExists(p);       // safe version

// Copy and move
Files.copy(src, dest, StandardCopyOption.REPLACE_EXISTING);
Files.move(src, dest, StandardCopyOption.ATOMIC_MOVE);
```

## Temporary files and directories

```java
Path tmp = Files.createTempFile("prefix-", ".txt");
Path tmpDir = Files.createTempDirectory("workdir-");
// Clean up with Files.delete or on JVM exit via toFile().deleteOnExit()
```

## File metadata

```java
System.out.println(Files.size(p));              // bytes
System.out.println(Files.isReadable(p));
System.out.println(Files.getLastModifiedTime(p));

BasicFileAttributes attrs = Files.readAttributes(p, BasicFileAttributes.class);
System.out.println(attrs.creationTime());
System.out.println(attrs.isDirectory());
```

## Encoding

Always specify the charset explicitly to avoid platform-dependent bugs:

```java
Files.readAllLines(p, StandardCharsets.UTF_8);
Files.writeString(p, text, StandardCharsets.UTF_8);
```

## Classic I/O vs NIO.2

| Task | Old `java.io` | Modern `java.nio.file` |
|------|--------------|------------------------|
| Represent a path | `File` | `Path` |
| Read all lines | Manual loop | `Files.readAllLines()` |
| Copy a file | Manual loop | `Files.copy()` |
| Walk a tree | Recursive `listFiles()` | `Files.walk()` |

Stick with `java.nio.file` for all new code.
