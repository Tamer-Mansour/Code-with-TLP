# Quiz: ASP.NET Core

**Q1. Which attribute automatically returns HTTP 400 when model validation fails?**
- [ ] `[ValidateModel]`
- [ ] `[FromBody]`
- [x] `[ApiController]`
- [ ] `[AutoValidate]`

**Q2. What does `app.UseAuthentication()` do if placed AFTER `app.UseAuthorization()`?**
- [ ] Works correctly — order does not matter for these two
- [ ] Throws an exception at startup
- [x] Authorization runs before identity is populated, so all authenticated routes will be denied
- [ ] Silently swaps the order internally

**Q3. Which DI lifetime creates a new instance for every HTTP request?**
- [ ] Transient
- [x] Scoped
- [ ] Singleton
- [ ] Contextual

**Q4. In Minimal APIs, how do you return a 404 Not Found response?**
- [ ] `return 404;`
- [ ] `return new NotFoundResult();`
- [x] `return Results.NotFound();`
- [ ] `throw new NotFoundException();`

**Q5. What does `app.Run(...)` do differently from `app.Use(...)`?**
- [ ] It adds middleware at the start of the pipeline
- [ ] It adds conditional middleware
- [x] It adds terminal middleware that never calls `next`
- [ ] It configures the web host

**Q6. `CreatedAtAction(nameof(GetById), new { id = product.Id }, product)` returns:**
- [ ] HTTP 200 with a Location header
- [ ] HTTP 204 with the product body
- [x] HTTP 201 with a Location header and the product body
- [ ] HTTP 202 with no body

**Q7. Which route template matches `/files/folder/sub/file.txt`?**
- [ ] `/files/{name}`
- [ ] `/files/{path:regex(.*\\..*)}`
- [x] `/files/{**path}`
- [ ] `/files/{path?}`
