# Driver Entry Points: open, read, write, ioctl

A character driver publishes a `file_operations` table — a vtable of function pointers the kernel calls when user space performs file operations on the device node. Mastering each entry point is the core skill of driver development.

## The `file_operations` Structure

```c
#include <linux/fs.h>

static const struct file_operations my_fops = {
    .owner   = THIS_MODULE,
    .open    = my_open,
    .release = my_release,
    .read    = my_read,
    .write   = my_write,
    .unlocked_ioctl = my_ioctl,
    .poll    = my_poll,
    .llseek  = my_llseek,
};
```

Each field is optional. If left NULL, the kernel provides a safe default (e.g., `default_llseek` or `-EINVAL`).

## `open` — Acquiring the Device

```c
int my_open(struct inode *inode, struct file *filp)
{
    struct my_dev *dev = container_of(inode->i_cdev,
                                      struct my_dev, cdev);
    filp->private_data = dev;   /* stash per-device state */
    /* initialize hardware if first open */
    if (atomic_inc_return(&dev->open_count) == 1)
        hw_power_on(dev);
    return 0;
}
```

Key responsibilities:
- Retrieve the device structure from the inode using `container_of`.
- Store it in `filp->private_data` for later entry points.
- Enforce single-open semantics if the hardware requires it.
- Return 0 on success, negative errno on failure.

## `read` — Transferring Data to User Space

```c
ssize_t my_read(struct file *filp, char __user *buf,
                size_t count, loff_t *f_pos)
{
    struct my_dev *dev = filp->private_data;
    char kbuf[64];
    int n;

    n = hw_receive(dev, kbuf, min(count, sizeof(kbuf)));
    if (n < 0)
        return n;   /* propagate hardware error */

    if (copy_to_user(buf, kbuf, n))
        return -EFAULT;

    *f_pos += n;
    return n;
}
```

Critical rule: **never dereference a user-space pointer directly**. Always use `copy_to_user()` / `copy_from_user()`. These functions validate the pointer and handle page faults safely.

## `write` — Receiving Data from User Space

```c
ssize_t my_write(struct file *filp, const char __user *buf,
                 size_t count, loff_t *f_pos)
{
    struct my_dev *dev = filp->private_data;
    char kbuf[64];
    size_t n = min(count, sizeof(kbuf));

    if (copy_from_user(kbuf, buf, n))
        return -EFAULT;

    return hw_transmit(dev, kbuf, n);
}
```

## `ioctl` — Out-of-Band Control

`ioctl` handles operations that don't fit the read/write model: setting baud rate, querying device capabilities, triggering a hardware reset.

```c
long my_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)
{
    struct my_dev *dev = filp->private_data;
    int val;

    switch (cmd) {
    case MY_IOC_RESET:
        hw_reset(dev);
        return 0;

    case MY_IOC_SET_BAUD:
        if (get_user(val, (int __user *)arg))
            return -EFAULT;
        return hw_set_baud(dev, val);

    case MY_IOC_GET_STATUS:
        val = hw_read_status(dev);
        return put_user(val, (int __user *)arg);

    default:
        return -ENOTTY;   /* "not a typewriter" = unknown ioctl */
    }
}
```

ioctl commands are composed with macros (`_IO`, `_IOR`, `_IOW`, `_IOWR`) that encode direction, type, number, and size into a 32-bit integer — preventing collisions between drivers.

```c
#define MY_IOC_MAGIC  'k'
#define MY_IOC_RESET  _IO(MY_IOC_MAGIC,  0)
#define MY_IOC_SET_BAUD _IOW(MY_IOC_MAGIC, 1, int)
#define MY_IOC_GET_STATUS _IOR(MY_IOC_MAGIC, 2, int)
```

## `release` — Cleanup

Called when the last file descriptor referencing the device is closed. Mirror everything done in `open`.

```c
int my_release(struct inode *inode, struct file *filp)
{
    struct my_dev *dev = filp->private_data;
    if (atomic_dec_and_test(&dev->open_count))
        hw_power_off(dev);
    return 0;
}
```

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---|---|---|
| Direct user pointer deref | Kernel oops / security hole | Use `copy_to/from_user` |
| Missing lock in read/write | Data corruption on SMP | Add mutex or spinlock |
| Returning wrong errno | Confuses callers | Use POSIX errno constants |
| `return -ENOTTY` omission | Unknown ioctls silently succeed | Always handle `default:` case |

## Interview Answer

> **Q: Why can't a driver dereference a user-space pointer directly?**
>
> **Interview answer:** User-space pointers may be invalid, unmapped, or point to memory the user is racing to unmap; `copy_to_user`/`copy_from_user` validate the pointer, handle page faults under a controlled exception table, and prevent kernel security vulnerabilities like arbitrary kernel memory reads.
