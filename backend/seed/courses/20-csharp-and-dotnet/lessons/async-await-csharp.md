# async / await

C# popularized `async/await` years before JavaScript and Python adopted similar syntax. It lets you write straight-line code over asynchronous operations.

## The basics

```csharp
public async Task<User> FetchUserAsync(long id)
{
    using var client = new HttpClient();
    var response = await client.GetAsync($"/users/{id}");
    var json = await response.Content.ReadAsStringAsync();
    return JsonSerializer.Deserialize<User>(json)!;
}
```

- A method marked `async` must return `Task`, `Task<T>`, `ValueTask`, `ValueTask<T>`, or `void` (avoid void).
- `await` unwraps a `Task<T>` to `T`, pausing execution until completion.
- The method body still runs on the calling thread; the *continuation* after `await` may run on a different one.

## Calling async

```csharp
var user = await FetchUserAsync(42);
```

`await` is contagious — to call an `async` method synchronously you need `.Result` or `.Wait()`, which **deadlocks** in many contexts. Don't. Make the call site `async` too.

In Top-level statements (modern Program.cs):

```csharp
var user = await FetchUserAsync(42);   // top-level await works
```

## Parallel awaits

For independent work in parallel:

```csharp
Task<User> userTask = FetchUserAsync(1);
Task<Order[]> ordersTask = FetchOrdersAsync(1);

await Task.WhenAll(userTask, ordersTask);

var user = userTask.Result;
var orders = ordersTask.Result;
```

Or:

```csharp
var (user, orders) = (
    await FetchUserAsync(1),
    await FetchOrdersAsync(1));   // sequential — slow
```

Use `Task.WhenAll` for parallelism; pure `await` chains are sequential.

## Cancellation

Every async API in modern .NET takes a `CancellationToken`:

```csharp
public async Task<User> FetchUserAsync(long id, CancellationToken ct)
{
    using var client = new HttpClient();
    var r = await client.GetAsync($"/users/{id}", ct);
    return await JsonSerializer.DeserializeAsync<User>(r.Content.ReadAsStream(), cancellationToken: ct);
}

using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(3));
var u = await FetchUserAsync(42, cts.Token);
```

If the token is cancelled, awaited operations throw `OperationCanceledException`. Pass `ct` through; never swallow it.

## Don't `async void`

```csharp
public async void DoStuff() { ... }   // ❌ exception swallowing, untestable
```

Use `async Task` (or `async ValueTask`) so callers can `await` and observe failures.

## ConfigureAwait

In library code, append `.ConfigureAwait(false)`:

```csharp
var r = await client.GetAsync(url).ConfigureAwait(false);
```

This avoids capturing the synchronization context — important in older UI / ASP.NET (pre-Core) apps to prevent deadlocks. Modern .NET 6+ doesn't have the synchronization context that caused the trouble, but most library code still uses it for safety.

## A common mistake: not awaiting

```csharp
public async Task SaveAsync(User u)
{
    db.SaveAsync(u);              // ❌ fire-and-forget, errors silently lost
}
```

Always await or explicitly hand off (`Task.Run`).

## Cancelable timeouts

```csharp
var timeoutCts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
var combinedCts = CancellationTokenSource.CreateLinkedTokenSource(callerCt, timeoutCts.Token);
await SomethingAsync(combinedCts.Token);
```

## When sync is fine

For pure CPU work, `async` adds overhead. For I/O, async pays off — same number of threads handle 100× the connections.
