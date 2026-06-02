# Writing Your Own RAII Wrapper Class

The standard library covers the most common resources, but system code routinely encounters domain-specific handles: GPU contexts, database cursors, custom allocator blocks, vendor SDK handles. Writing a correct RAII wrapper is a small, repeatable task once you know the checklist.

## The Five-Part Checklist

1. Store the resource handle as a private member.
2. Acquire in the constructor; throw on failure.
3. Release in the destructor; mark it `noexcept`.
4. Delete or implement copy.
5. Implement move to enable ownership transfer.

## Worked Example: Wrapping a Vendor SDK Handle

Suppose a hardware SDK provides:

```c
typedef void* cam_handle_t;
cam_handle_t cam_open(int device_id);   // returns NULL on failure
void         cam_close(cam_handle_t h);
int          cam_capture(cam_handle_t h, uint8_t* buf, size_t len);
```

Here is a correct RAII wrapper:

```cpp
#include <stdexcept>
#include <utility>    // std::exchange
#include <cstdint>

extern "C" {
    typedef void* cam_handle_t;
    cam_handle_t cam_open(int device_id);
    void         cam_close(cam_handle_t h);
    int          cam_capture(cam_handle_t h, uint8_t* buf, size_t len);
}

class Camera {
public:
    // (1) Constructor acquires the resource
    explicit Camera(int device_id)
        : handle_(cam_open(device_id))
    {
        if (!handle_)
            throw std::runtime_error("cam_open failed for device " + std::to_string(device_id));
    }

    // (2) Destructor releases — noexcept, never throws
    ~Camera() noexcept {
        if (handle_)
            cam_close(handle_);
    }

    // (3) Delete copy — two Cameras must not share one handle
    Camera(const Camera&) = delete;
    Camera& operator=(const Camera&) = delete;

    // (4) Move constructor — transfer ownership, null out source
    Camera(Camera&& other) noexcept
        : handle_(std::exchange(other.handle_, nullptr))
    {}

    // (5) Move assignment — release current, take ownership of other
    Camera& operator=(Camera&& other) noexcept {
        if (this != &other) {
            if (handle_) cam_close(handle_);
            handle_ = std::exchange(other.handle_, nullptr);
        }
        return *this;
    }

    // (6) Non-owning accessor
    cam_handle_t get() const noexcept { return handle_; }

    // (7) Check validity
    explicit operator bool() const noexcept { return handle_ != nullptr; }

    // (8) Explicit release — caller takes ownership
    cam_handle_t release() noexcept {
        return std::exchange(handle_, nullptr);
    }

    // (9) Domain methods — delegates to C API
    int capture(uint8_t* buf, size_t len) {
        return cam_capture(handle_, buf, len);
    }

private:
    cam_handle_t handle_;
};
```

Usage:

```cpp
void record_frame(int device) {
    Camera cam(device);              // throws if device unavailable
    std::vector<uint8_t> frame(1920 * 1080 * 3);
    if (cam.capture(frame.data(), frame.size()) < 0)
        throw std::runtime_error("capture failed");
    // cam closed automatically
}

// Move into a container
std::vector<Camera> open_all_cameras(int count) {
    std::vector<Camera> cams;
    for (int i = 0; i < count; ++i)
        cams.emplace_back(i);   // constructed in-place
    return cams;                // moved out (NRVO)
}
```

## Using `std::unique_ptr` with a Custom Deleter

For simpler cases, skip the wrapper class entirely:

```cpp
struct CamDeleter {
    void operator()(cam_handle_t h) const noexcept {
        if (h) cam_close(h);
    }
};

using CameraPtr = std::unique_ptr<void, CamDeleter>;

CameraPtr make_camera(int id) {
    cam_handle_t h = cam_open(id);
    if (!h) throw std::runtime_error("cam_open failed");
    return CameraPtr(h);
}
```

This is shorter but provides no domain methods and exposes the `void*` type. Use the full wrapper class when you want to add domain behavior or a safer type.

## Generalized RAII via Template

For truly ad hoc one-off handles:

```cpp
template<typename Handle, typename Deleter>
class UniqueResource {
public:
    UniqueResource(Handle h, Deleter d) : h_(h), d_(std::move(d)) {}
    ~UniqueResource() noexcept { if (valid_) d_(h_); }
    UniqueResource(UniqueResource&&) = default;
    UniqueResource(const UniqueResource&) = delete;
    Handle get() const noexcept { return h_; }
    void dismiss() noexcept { valid_ = false; }
private:
    Handle h_;
    Deleter d_;
    bool valid_ = true;
};
```

## Common Mistakes and How to Avoid Them

| Mistake | Fix |
|---|---|
| Not checking for invalid handle in destructor | Always check for sentinel before calling release |
| Using `0` as sentinel for a fd | Use `-1`; fd 0 is stdin |
| Forgetting `std::exchange` in move | Nulling `other.handle_` manually is error-prone; `exchange` is atomic |
| Providing `operator=` but not `operator=(&&)` | If you write one, write both — or delete both |
| Throwing from destructor | Catch internally and log; never propagate |

**Interview answer:** A correct RAII wrapper deletes copy, implements move using `std::exchange` to null the source, acquires in the constructor (throwing on failure), and releases in a `noexcept` destructor that guards against the invalid-handle sentinel.
