# Permissions to Octal

Unix file permissions are 9 bits: read/write/execute for user/group/other. Each triple becomes one octal digit (`r=4`, `w=2`, `x=1`).

Given a permission string like `rwxr-xr-x`, convert it to its 3-digit octal form (`755`).

See the prompt for the exact contract.
