# Parse Docker Volume Mounts

You are given **N** volume mount strings (one per line), as used with `docker run -v <mount>`.

Classify each mount and count each type:

- **named**: the part before `:` (or the whole string if no colon) starts with a letter, digit, underscore, or dash — and contains **no** `/` before the first colon.  
  Example: `pgdata:/var/lib/postgresql/data`, `mydata`
- **bind**: starts with `/`, `./`, or `../`.  
  Example: `./src:/app/src`, `/etc/nginx/nginx.conf:/etc/nginx/nginx.conf`
- **anonymous**: starts with `/` but has **no** colon (bare container path, treated as anonymous volume).  
  Example: `/app/node_modules`

**Input format:**
```
N
mount_string_1
mount_string_2
...
```

**Output format** (exactly three lines):
```
named=<count>
bind=<count>
anonymous=<count>
```

## Example

Input:
```
4
pgdata:/var/lib/postgresql/data
./src:/app/src
/app/node_modules
myconfig:/etc/myapp
```

Output:
```
named=2
bind=1
anonymous=1
```
