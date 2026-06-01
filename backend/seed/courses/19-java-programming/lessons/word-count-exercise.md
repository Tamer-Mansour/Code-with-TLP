# Word Count

A classic Streams-style task: count word frequencies and return the top-K.

In Java:

```java
Map<String, Long> counts = Arrays.stream(text.split("\\s+"))
    .collect(Collectors.groupingBy(w -> w, Collectors.counting()));

List<Map.Entry<String, Long>> top = counts.entrySet().stream()
    .sorted(Map.Entry.<String, Long>comparingByValue().reversed()
        .thenComparing(Map.Entry.comparingByKey()))
    .limit(K)
    .toList();
```

In this exercise you'll mirror that logic in Python.

See the prompt for the exact contract.
