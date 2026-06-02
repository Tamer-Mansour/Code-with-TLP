# Exercise: Commit Ancestry Distance

Given a directed acyclic graph (DAG) of commits where each node points to its parents, compute the minimum number of commits (hops) separating commit A from commit B, where A is guaranteed to be an ancestor of B.

Read the graph and the two commit names, then output the number of edges (parent hops) on the shortest path from A to B. If A == B, output 0.
