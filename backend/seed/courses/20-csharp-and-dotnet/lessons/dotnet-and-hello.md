# dotnet CLI and Hello, C#

C# (pronounced "C sharp") runs on **.NET** — Microsoft's open-source, cross-platform runtime. The current .NET (just ".NET", formerly ".NET Core") ships ~yearly; even-numbered releases are LTS. .NET 8 and .NET 10 are LTS at the time of writing.

## Install

```bash
# macOS
brew install --cask dotnet-sdk
# Linux
sudo apt install -y dotnet-sdk-8.0
# Windows
winget install Microsoft.DotNet.SDK.8
```

Confirm: `dotnet --version`.

## Create a console project

```bash
dotnet new console -o hello
cd hello
dotnet run
```

`hello/Program.cs`:

```csharp
Console.WriteLine("Hello, C#");
```

That's the whole program — **top-level statements**, no class, no `Main` method required.

## Slightly bigger

```csharp
var name = args.Length > 0 ? args[0] : "world";
Console.WriteLine($"Hello, {name}");
```

`var` does type inference. `$"..."` is an interpolated string.

## Common project templates

```bash
dotnet new console        # CLI app
dotnet new classlib       # library
dotnet new web            # minimal API
dotnet new webapi         # full Web API
dotnet new blazorserver   # Blazor Server app
dotnet new mstest         # MSTest test project
dotnet new xunit          # xUnit test project
```

## Adding packages

```bash
dotnet add package Newtonsoft.Json
dotnet remove package Newtonsoft.Json
dotnet restore
```

NuGet packages get cached at `~/.nuget/packages`.

## Build and publish

```bash
dotnet build              # debug build
dotnet build -c Release
dotnet publish -c Release -r linux-x64 --self-contained
```

`--self-contained` bundles the runtime. With AOT compilation (`<PublishAot>true</PublishAot>` in `.csproj`), you get a native binary with fast startup — comparable to Go binaries.

## .csproj — the manifest

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
```

- **`Nullable: enable`** — opt into nullable reference type checking. **Always on for new code.**
- **`ImplicitUsings: enable`** — auto-imports common namespaces (`System`, `System.Collections.Generic`, etc.).

## Versions and conventions

- File names PascalCase, matching the contained type (`UserService.cs`).
- Namespaces mirror folders (`MyApp.Services.UserService`).
- Top-level statements only in one `.cs` file per project (the entry point).

## Editors

- **Visual Studio** — full IDE, Windows mostly.
- **JetBrains Rider** — cross-platform, premium experience.
- **VSCode + C# Dev Kit** — lightweight, official MS extension.

All three give you IntelliSense, debugging, and refactoring.
