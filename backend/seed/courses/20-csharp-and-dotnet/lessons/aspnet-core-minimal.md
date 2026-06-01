# ASP.NET Core Minimal APIs

Minimal APIs let you build HTTP services with a few lines of code — no controllers required.

## Hello world

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => "Hello, world");
app.MapGet("/users/{id:int}", (int id) => new { Id = id, Name = $"User {id}" });

app.Run();
```

`dotnet run` starts the server, default on `:5000` / `:5001`.

## Routing and bindings

```csharp
app.MapGet("/users/{id:int}", (int id) => ...);
app.MapPost("/users", (User u) => ...);              // bound from JSON body
app.MapGet("/search", (string q, int? limit) => ...); // from query string
```

Parameter binding inspects the type and source:

- `[FromBody]`, `[FromQuery]`, `[FromRoute]`, `[FromHeader]`, `[FromServices]` make it explicit.
- Complex types default to body for POST/PUT, query for GET.

## Returning data and status codes

```csharp
app.MapGet("/users/{id}", (int id) =>
{
    var u = repo.Find(id);
    return u is null ? Results.NotFound() : Results.Ok(u);
});

app.MapPost("/users", (User input) =>
{
    var u = repo.Add(input);
    return Results.Created($"/users/{u.Id}", u);
});
```

`Results` provides typed responses for every HTTP status.

## Dependency Injection

```csharp
builder.Services.AddSingleton<IUserRepo, UserRepo>();
builder.Services.AddScoped<DbContext, AppDbContext>();
builder.Services.AddDbContext<AppDbContext>(opt =>
    opt.UseNpgsql(builder.Configuration.GetConnectionString("Default")));

app.MapGet("/users", (IUserRepo repo) => repo.GetAll());
```

Service lifetimes:

- `Singleton` — one instance per app.
- `Scoped` — one per HTTP request.
- `Transient` — new every time.

## Configuration

`appsettings.json`:

```json
{
  "ConnectionStrings": {
    "Default": "Host=db;Database=shop;Username=postgres;Password=secret"
  },
  "Logging": { "LogLevel": { "Default": "Information" } }
}
```

```csharp
var connStr = builder.Configuration.GetConnectionString("Default");
```

Env vars override (great for containers): `ConnectionStrings__Default=...`.

## Middleware pipeline

```csharp
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.UseCors();
app.UseSerilogRequestLogging();
```

Order matters — auth must be before authorization, etc. The pipeline runs in the order you call `app.UseX`.

## Validation

Use a library — **FluentValidation** is popular:

```csharp
public class CreateUserValidator : AbstractValidator<CreateUser>
{
    public CreateUserValidator()
    {
        RuleFor(x => x.Email).NotEmpty().EmailAddress();
        RuleFor(x => x.Age).InclusiveBetween(0, 120);
    }
}
```

Or the built-in `[Required]`/`[Range]` attributes for simple cases.

## Where to go next

For a bigger API surface, controllers (`AddControllers`) give you action filters, model binding attributes, and OpenAPI integration. The same DI container, the same routing — minimal APIs and controllers happily coexist in one project.
