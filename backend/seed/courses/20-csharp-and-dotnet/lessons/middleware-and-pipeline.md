# Middleware and the ASP.NET Core Pipeline

Every HTTP request in ASP.NET Core flows through a **middleware pipeline** — a chain of components each of which can inspect, modify, or short-circuit the request and response. Understanding the pipeline is essential for cross-cutting concerns like authentication, logging, and error handling.

## How the pipeline works

```
Request →  MW1 → MW2 → MW3 → (endpoint)
Response ←  MW1 ← MW2 ← MW3 ←
```

Each middleware calls `await next(context)` to pass control to the next component. It can run logic before and/or after that call.

## Built-in middleware (registration order matters)

```csharp
var app = builder.Build();

app.UseExceptionHandler("/error");   // catch unhandled exceptions
app.UseHsts();                       // Strict-Transport-Security header
app.UseHttpsRedirection();           // redirect HTTP → HTTPS
app.UseStaticFiles();                // serve wwwroot files
app.UseRouting();                    // match routes
app.UseAuthentication();             // populate User identity
app.UseAuthorization();              // enforce policies
app.MapControllers();                // controller endpoints
```

Order is critical: `UseAuthentication` must precede `UseAuthorization`; both must follow `UseRouting`.

## Writing custom middleware

### Inline (simple)

```csharp
app.Use(async (context, next) =>
{
    var sw = Stopwatch.StartNew();
    await next(context);
    sw.Stop();
    Console.WriteLine($"{context.Request.Path} took {sw.ElapsedMilliseconds} ms");
});
```

### Class-based (reusable)

```csharp
public class RequestTimingMiddleware
{
    private readonly RequestDelegate _next;

    public RequestTimingMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context)
    {
        var sw = Stopwatch.StartNew();
        await _next(context);
        sw.Stop();
        context.Response.Headers["X-Elapsed-Ms"] = sw.ElapsedMilliseconds.ToString();
    }
}

// Register
app.UseMiddleware<RequestTimingMiddleware>();
```

## Short-circuiting

A middleware can respond directly without calling `next`, stopping the pipeline:

```csharp
app.Use(async (context, next) =>
{
    if (!context.Request.Headers.ContainsKey("X-API-Key"))
    {
        context.Response.StatusCode = 401;
        await context.Response.WriteAsync("Missing API key");
        return;   // pipeline stops here
    }
    await next(context);
});
```

## app.Map — branching the pipeline

```csharp
app.Map("/health", healthApp =>
{
    healthApp.Run(async ctx =>
    {
        await ctx.Response.WriteAsync("OK");
    });
});
```

Requests to `/health` take a completely separate branch.

## app.Run — terminal middleware

`app.Run` adds a terminal middleware (never calls `next`):

```csharp
app.Run(async context =>
{
    await context.Response.WriteAsync("Fallback response");
});
```

## Common use cases for custom middleware

| Use case              | What to do                                     |
|-----------------------|------------------------------------------------|
| Request logging       | Log method, path, status, duration             |
| Correlation IDs       | Add/read `X-Correlation-Id` header             |
| Rate limiting         | Count requests per IP; return 429              |
| Tenant resolution     | Parse subdomain, set tenant context            |
| Response compression  | Use built-in `UseResponseCompression()`        |

## Key takeaways

- Middleware is a chain — order matters, especially for security components.
- Use `app.Use` for two-way (before/after) middleware; `app.Run` for terminal.
- Class-based middleware is testable and DI-friendly.
- Short-circuit early for rejected requests to avoid unnecessary work.
