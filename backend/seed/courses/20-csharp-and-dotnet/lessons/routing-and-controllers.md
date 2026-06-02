# Routing and Controllers in ASP.NET Core

ASP.NET Core supports two styles: **Minimal APIs** (lambdas registered directly) and **Controllers** (classes derived from `ControllerBase`). Controllers are better suited to larger APIs with many endpoints, complex validation, and filters.

## Minimal API recap

```csharp
app.MapGet("/products/{id:int}", async (int id, IProductService svc) =>
{
    var product = await svc.GetByIdAsync(id);
    return product is null ? Results.NotFound() : Results.Ok(product);
});
```

Route constraints like `:int`, `:guid`, `:minlength(3)` enforce types in the URL path.

## Controller-based API

```csharp
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    private readonly IProductService _svc;
    public ProductsController(IProductService svc) => _svc = svc;

    [HttpGet]
    public async Task<ActionResult<IList<Product>>> GetAll()
        => Ok(await _svc.GetAllAsync());

    [HttpGet("{id:int}")]
    public async Task<ActionResult<Product>> GetById(int id)
    {
        var p = await _svc.GetByIdAsync(id);
        return p is null ? NotFound() : Ok(p);
    }

    [HttpPost]
    public async Task<ActionResult<Product>> Create(Product product)
    {
        await _svc.AddAsync(product);
        return CreatedAtAction(nameof(GetById), new { id = product.Id }, product);
    }

    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(int id, Product product)
    {
        if (id != product.Id) return BadRequest();
        await _svc.UpdateAsync(product);
        return NoContent();
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        await _svc.DeleteAsync(id);
        return NoContent();
    }
}
```

`[ApiController]` enables automatic model validation, binding source inference, and 400 responses for invalid models.

## Route templates

| Template                 | Matches                      | Notes                          |
|--------------------------|------------------------------|--------------------------------|
| `/products`              | Exact path                   | —                              |
| `/products/{id}`         | Any value in segment         | `id` bound as string           |
| `/products/{id:int}`     | Integer only                 | Returns 404 for non-integers   |
| `/products/{id:guid}`    | GUID string                  | —                              |
| `/files/{**path}`        | Catch-all                    | Includes `/` characters        |
| `/search/{term?}`        | Optional segment             | `term` may be absent           |

## Model binding and validation

```csharp
public class CreateProductRequest
{
    [Required]
    [MaxLength(100)]
    public string Name { get; set; } = "";

    [Range(0.01, 1_000_000)]
    public decimal Price { get; set; }
}

[HttpPost]
public async Task<IActionResult> Create([FromBody] CreateProductRequest req)
{
    // [ApiController] already returns 400 if ModelState.IsValid == false
    ...
}
```

## Action results

| Helper method     | HTTP status     | Use when                             |
|-------------------|-----------------|--------------------------------------|
| `Ok(value)`       | 200             | Successful read                      |
| `Created(...)`    | 201             | Resource successfully created        |
| `NoContent()`     | 204             | Successful write with no body        |
| `BadRequest()`    | 400             | Client error (invalid input)         |
| `Unauthorized()`  | 401             | Not authenticated                    |
| `Forbid()`        | 403             | Authenticated but not authorized     |
| `NotFound()`      | 404             | Resource does not exist              |
| `Conflict()`      | 409             | Duplicate or version conflict        |

## Filters

Filters run at defined points around action execution:

```csharp
[ServiceFilter(typeof(AuditLogFilter))]   // applied to a controller
public class OrdersController : ControllerBase { ... }

// Or globally
builder.Services.AddControllers(opts =>
    opts.Filters.Add<GlobalExceptionFilter>());
```

## Key takeaways

- `[ApiController]` + `ControllerBase` give you automatic validation, consistent error formats, and structured action results.
- Route constraints keep URLs type-safe without manual parsing.
- Use `CreatedAtAction` for POST endpoints to return a proper `Location` header.
- Filters are the right hook for cross-cutting concerns like logging or exception formatting.
