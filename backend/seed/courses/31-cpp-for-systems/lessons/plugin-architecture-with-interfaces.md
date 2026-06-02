# A Plugin Architecture Using Abstract Interfaces

A **plugin architecture** lets you extend an application's behaviour at runtime by loading new implementations without recompiling the host. Abstract interfaces are the foundation: the host depends only on a stable base-class pointer, and plugins ship as shared libraries that return concrete subclass instances.

## The Three-Layer Model

```
Host application
    |
    |  depends on
    v
IPlugin interface (abstract, stable, header-only)
    ^
    |  implements
Plugin shared library (.so / .dll)
```

The host never includes the plugin's headers. The plugin never includes the host's headers. Both depend on the shared interface header.

## Step 1: Define the Interface

```cpp
// iplugin.h — shipped to both host and plugin authors
#pragma once
#include <cstdint>

class IPlugin {
public:
    virtual const char* name()        const = 0;
    virtual const char* version()     const = 0;
    virtual int         on_load()           = 0;   // called once at load time
    virtual int         on_unload()         = 0;   // called before unload
    virtual int         execute(const char* cmd, char* out, uint32_t out_len) = 0;

    virtual ~IPlugin() = default;
};

// C-linkage factory functions (exported from the .so/.dll)
extern "C" {
    IPlugin* create_plugin();
    void     destroy_plugin(IPlugin*);
}
```

C linkage on the factory functions avoids C++ name mangling issues between compilers and avoids ABI incompatibilities.

## Step 2: Implement a Plugin

```cpp
// hash_plugin.cpp — compiled into hash_plugin.so
#include "iplugin.h"
#include <cstring>
#include <cstdio>

class HashPlugin : public IPlugin {
public:
    const char* name()    const override { return "HashPlugin"; }
    const char* version() const override { return "1.0.0"; }

    int on_load()   override { return 0; }
    int on_unload() override { return 0; }

    int execute(const char* cmd, char* out, uint32_t out_len) override {
        // Trivial FNV-1a hash as a demo
        uint32_t h = 2166136261u;
        for (const char* p = cmd; *p; ++p)
            h = (h ^ (uint8_t)*p) * 16777619u;
        std::snprintf(out, out_len, "%08x", h);
        return 0;
    }
};

extern "C" IPlugin* create_plugin()          { return new HashPlugin(); }
extern "C" void     destroy_plugin(IPlugin* p) { delete p; }
```

## Step 3: Load the Plugin in the Host

```cpp
// host.cpp (Linux — uses dlopen; Windows equivalent: LoadLibrary)
#include "iplugin.h"
#include <dlfcn.h>
#include <memory>
#include <stdexcept>

struct PluginHandle {
    void*    lib;
    IPlugin* plugin;
    using DestroyFn = void(*)(IPlugin*);
    DestroyFn destroy_fn;

    ~PluginHandle() {
        if (plugin)  destroy_fn(plugin);
        if (lib)     dlclose(lib);
    }
};

PluginHandle load_plugin(const char* path) {
    void* lib = dlopen(path, RTLD_LAZY | RTLD_LOCAL);
    if (!lib) throw std::runtime_error(dlerror());

    auto create  = reinterpret_cast<IPlugin*(*)()>(dlsym(lib, "create_plugin"));
    auto destroy = reinterpret_cast<void(*)(IPlugin*)>(dlsym(lib, "destroy_plugin"));
    if (!create || !destroy) throw std::runtime_error("symbol not found");

    IPlugin* p = create();
    p->on_load();
    return {lib, p, destroy};
}

int main() {
    auto h = load_plugin("./hash_plugin.so");
    char result[64];
    h.plugin->execute("hello", result, sizeof(result));
    std::printf("Hash: %s\n", result);
    h.plugin->on_unload();
}
```

## Key Design Rules

| Rule | Reason |
|------|--------|
| Keep the interface header pure C++ with no implementation | Ensures ABI stability |
| Use C-linkage factory functions | Avoids name mangling and vtable ABI differences |
| Never `delete` through a raw `IPlugin*` from a different .so | Use the `destroy_plugin` function from the same library |
| Version the interface carefully | Changing pure virtual signatures breaks all existing plugins |

## Versioning the Interface

When you must evolve the interface, options include:

- Add new pure virtual functions and bump the version — existing plugins recompile.
- Introduce `IPlugin2 : public IPlugin` — additive, older plugins still work.
- Embed a `virtual uint32_t abi_version() const = 0` and reject mismatches at load time.

> **Interview answer:** A plugin architecture uses abstract interfaces with C-linkage factory functions so the host loads concrete implementations at runtime via `dlopen`/`LoadLibrary` without knowing their types — the stable pure-virtual interface is the only shared contract, and `destroy_plugin` ensures objects are deleted by the same allocator that created them.
