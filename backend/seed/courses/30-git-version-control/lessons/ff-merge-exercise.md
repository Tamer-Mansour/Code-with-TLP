# Fast-Forward Check

A **fast-forward merge** is possible when the base branch is a direct ancestor of the target branch — no diverging commits on base. Git just moves base's pointer forward; no merge commit is created.

Given a commit graph and two commit names, decide whether merging `target` into `base` would be a fast-forward.

See the prompt for the exact contract.
