# Dependency Injection in ASP.NET Core

Dependency Injection (DI) is built into ASP.NET Core — no third-party container needed. It wires up services, makes code testable, and keeps components loosely coupled.

## The three service lifetimes

| Lifetime    | New instance created…                  | Use for                           |
|-------------|----------------------------------------|-----------------------------------|
| `Transient` | Every time it is requested             | Lightweight, stateless services   |
| `Scoped`    | Once per HTTP request                  | DbContext, per-request state      |
| `Singleton` | Once for the entire application lifetime | Config, caches, HTTP clients   |

## Registering services

In `Program.cs` (Minimal API style):

```csharp
var builder = WebApplication.CreateBuilder(args);

// Register with lifetime
builder.Services.AddTransient<IEmailService, SmtpEmailService>();
builder.Services.AddScoped<IOrderRepository, SqlOrderRepository>();
builder.Services.AddSingleton<ICache, MemoryCache>();

// Convenience registrations
builder.Services.AddHttpClient<IGitHubClient, GitHubClient>();
builder.Services.AddDbContext<AppDbContext>(opts =>
    opts.UseSqlite(builder.Configuration.GetConnectionString("Default")));

var app = builder.Build();
```

## Constructor injection

The most common pattern — declare dependencies as constructor parameters:

```csharp
public class OrderService
{
    private readonly IOrderRepository _repo;
    private readonly IEmailService    _email;

    public OrderService(IOrderRepository repo, IEmailService email)
    {
        _repo  = repo;
        _email = email;
    }

    public async Task PlaceOrderAsync(Order order)
    {
        await _repo.AddAsync(order);
        await _email.SendConfirmationAsync(order.CustomerEmail);
    }
}
```

The DI container resolves `IOrderRepository` and `IEmailService` automatically — you never call `new OrderService(...)` yourself in application code.

## Injecting into Minimal API handlers

```csharp
app.MapPost("/orders", async (Order order, OrderService svc) =>
{
    await svc.PlaceOrderAsync(order);
    return Results.Created($"/orders/{order.Id}", order);
});
```

Parameters in Minimal API route handlers are resolved from DI if they are registered services.

## IOptions\<T\> — injecting configuration

```csharp
// In appsettings.json
// { "Email": { "SmtpHost": "smtp.example.com", "Port": 587 } }

public class EmailOptions
{
    public string SmtpHost { get; set; } = "";
    public int    Port     { get; set; } = 587;
}

// Register
builder.Services.Configure<EmailOptions>(
    builder.Configuration.GetSection("Email"));

// Consume
public class SmtpEmailService
{
    private readonly EmailOptions _opts;

    public SmtpEmailService(IOptions<EmailOptions> opts)
        => _opts = opts.Value;
}
```

## Testing with DI

DI makes unit testing trivial — swap real dependencies with fakes or mocks:

```csharp
// Using Moq (or any mock library)
var repoMock  = new Mock<IOrderRepository>();
var emailMock = new Mock<IEmailService>();

repoMock.Setup(r => r.AddAsync(It.IsAny<Order>())).Returns(Task.CompletedTask);

var svc = new OrderService(repoMock.Object, emailMock.Object);
await svc.PlaceOrderAsync(new Order { CustomerEmail = "a@b.com" });

emailMock.Verify(e => e.SendConfirmationAsync("a@b.com"), Times.Once);
```

## Key takeaways

- Register services with the appropriate lifetime — misusing `Singleton` with `Scoped` dependencies causes runtime errors.
- Prefer constructor injection for mandatory dependencies.
- `IOptions<T>` binds typed configuration sections cleanly.
- DI makes unit testing easy by letting you inject mocks instead of real services.
