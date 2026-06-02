# Unit Testing in C# with xUnit

Testing is a first-class citizen in the .NET ecosystem. The two most popular frameworks are **xUnit** (preferred for new projects) and **MSTest**. This lesson focuses on xUnit with the Moq mocking library.

## Setting up a test project

```bash
dotnet new xunit -o MyApp.Tests
cd MyApp.Tests
dotnet add reference ../MyApp/MyApp.csproj
dotnet add package Moq
dotnet add package FluentAssertions
```

## Your first test

```csharp
using Xunit;

public class CalculatorTests
{
    [Fact]
    public void Add_TwoPositiveNumbers_ReturnsSum()
    {
        // Arrange
        var calc = new Calculator();

        // Act
        int result = calc.Add(3, 4);

        // Assert
        Assert.Equal(7, result);
    }
}
```

The **Arrange-Act-Assert (AAA)** pattern keeps tests readable. Each test verifies one behavior.

## Parameterized tests with \[Theory\]

```csharp
public class CalculatorTests
{
    [Theory]
    [InlineData(0,  0,  0)]
    [InlineData(1,  2,  3)]
    [InlineData(-1, 1,  0)]
    [InlineData(5, -3,  2)]
    public void Add_VariousInputs_ReturnsCorrectSum(int a, int b, int expected)
    {
        var calc = new Calculator();
        Assert.Equal(expected, calc.Add(a, b));
    }
}
```

`[Theory]` with `[InlineData]` runs the same test body for each data row.

## Mocking dependencies with Moq

```csharp
using Moq;

public class OrderServiceTests
{
    [Fact]
    public async Task PlaceOrder_SendsConfirmationEmail()
    {
        // Arrange
        var repoMock  = new Mock<IOrderRepository>();
        var emailMock = new Mock<IEmailService>();

        repoMock.Setup(r => r.AddAsync(It.IsAny<Order>()))
                .Returns(Task.CompletedTask);

        var svc = new OrderService(repoMock.Object, emailMock.Object);
        var order = new Order { CustomerEmail = "alice@example.com" };

        // Act
        await svc.PlaceOrderAsync(order);

        // Assert — email was sent exactly once
        emailMock.Verify(
            e => e.SendConfirmationAsync("alice@example.com"),
            Times.Once);
    }
}
```

## FluentAssertions — readable expectations

```csharp
using FluentAssertions;

result.Should().Be(7);
list.Should().HaveCount(3).And.Contain("apple");
action.Should().Throw<ArgumentNullException>()
      .WithMessage("*name*");
```

FluentAssertions produces clear failure messages: `Expected 7, but found 5.`

## Testing exceptions

```csharp
[Fact]
public void Divide_ByZero_ThrowsArgumentException()
{
    var calc = new Calculator();
    Assert.Throws<DivideByZeroException>(() => calc.Divide(10, 0));
}
```

## Organizing tests

| Convention                             | Why                                       |
|----------------------------------------|-------------------------------------------|
| `<TypeUnderTest>Tests` class name      | Easy to find tests for a given class      |
| `Method_Scenario_ExpectedResult` names | Describes the test without reading the body |
| One assertion per test (ideally)       | Pinpoints what failed immediately         |
| Separate test project                  | Keeps production assemblies lean          |

## Running tests

```bash
dotnet test                          # run all
dotnet test --filter "Add"           # filter by name
dotnet test --collect:"XPlat Code Coverage"   # coverage
```

In VS / Rider, the Test Explorer shows a live tree of passing/failing tests.

## Key takeaways

- `[Fact]` for a single case; `[Theory]` + `[InlineData]` for multiple inputs.
- AAA (Arrange-Act-Assert) keeps tests structured and readable.
- Moq replaces real dependencies with controlled fakes — essential for unit testing services.
- FluentAssertions makes assertion failures descriptive and human-readable.
