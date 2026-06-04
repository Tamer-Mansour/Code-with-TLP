# Quiz: Collections and Generics

**Q1. Which collection type should you use when you only need to check membership (no ordering, no duplicate values)?**
- [ ] `List<T>`
- [ ] `Queue<T>`
- [x] `HashSet<T>`
- [ ] `Dictionary<TKey, TValue>`

**Q2. What does this code print?**
```csharp
var d = new Dictionary<string, int>();
d["a"] = 1;
d["b"] = 2;
d["a"] = 5;
Console.WriteLine(d["a"]);
```
- [ ] `1`
- [x] `5`
- [ ] `ArgumentException`
- [ ] `2`

**Q3. Which generic constraint requires that `T` has a parameterless constructor?**
- [ ] `where T : struct`
- [ ] `where T : class`
- [x] `where T : new()`
- [ ] `where T : IEquatable<T>`

**Q4. `IEnumerable<T>` supports:**
- [x] Iteration with `foreach`
- [ ] Random access by index
- [ ] Adding elements
- [ ] Removing elements

**Q5. What is the average time complexity of `Dictionary<TKey, TValue>.ContainsKey`?**
- [ ] O(n)
- [ ] O(log n)
- [x] O(1)
- [ ] O(n log n)

**Q6. Which LINQ method returns elements sorted in ascending order?**
- [ ] `GroupBy`
- [ ] `Select`
- [x] `OrderBy`
- [ ] `Where`
