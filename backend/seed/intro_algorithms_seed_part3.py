"""
Seed part 3: modules 9–12 (Graph Traversal, Shortest Paths, DP, Greedy/MST).
Run from backend/ directory after parts 1 and 2:
    python seed/intro_algorithms_seed_part3.py
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import (
    Base, Course, Difficulty, Exercise, Lesson, LessonType,
    Module, Subject, TestCase,
)

LANGS = ["python", "javascript", "typescript", "java", "csharp"]


def _module(db, course, title, order, summary=""):
    obj = db.scalar(select(Module).where(Module.course_id == course.id, Module.title == title))
    if not obj:
        obj = Module(course_id=course.id, title=title, order_index=order, summary=summary)
        db.add(obj); db.flush()
    return obj

def _lesson(db, mod, slug, **kw):
    obj = db.scalar(select(Lesson).where(Lesson.module_id == mod.id, Lesson.slug == slug))
    if not obj:
        obj = Lesson(module_id=mod.id, slug=slug, **kw); db.add(obj); db.flush()
    return obj

def _exercise(db, lesson, slug, **kw):
    obj = db.scalar(select(Exercise).where(Exercise.slug == slug))
    if not obj:
        obj = Exercise(lesson_id=lesson.id, slug=slug, **kw); db.add(obj); db.flush()
        return obj, True
    return obj, False

def _cases(db, ex, cases):
    if ex.test_cases: return
    for i, (name, stdin, expected, hidden, weight) in enumerate(cases):
        db.add(TestCase(exercise_id=ex.id, name=name, stdin=stdin,
                        expected_stdout=expected, is_hidden=hidden,
                        weight=weight, order_index=i))


# ════════════════════════════════════════════════════════════════
#  MODULE 9 — Graph Algorithms: BFS and DFS
# ════════════════════════════════════════════════════════════════

M9_BFS_MD = """\
# Breadth-First Search (BFS)

BFS explores all vertices at distance d before any vertex at distance d+1.

## Algorithm
```
BFS(G, s):
    for each vertex u: d[u] = ∞, π[u] = NIL
    d[s] = 0
    Q = queue containing s
    while Q not empty:
        u = DEQUEUE(Q)
        for each neighbour v of u:
            if d[v] == ∞:
                d[v] = d[u] + 1
                π[v] = u
                ENQUEUE(Q, v)
```

## Properties
- **Time:** O(V + E) — each vertex and edge processed once.
- **Space:** O(V) for the queue and distance array.
- **Shortest path (unweighted):** d[v] = minimum number of edges from s to v.
- BFS tree spans all reachable vertices from s.

## Applications
- Shortest path in unweighted graphs
- Level-order tree traversal
- Finding connected components
- Web crawling / social network distance
- Bipartiteness check (2-colouring)

# Depth-First Search (DFS)

DFS explores as far as possible before backtracking.

## Algorithm (recursive)
```
DFS(G):
    for each vertex u: colour[u] = WHITE
    time = 0
    for each vertex u:
        if colour[u] == WHITE: DFS-VISIT(u)

DFS-VISIT(u):
    colour[u] = GRAY; d[u] = ++time
    for each neighbour v of u:
        if colour[v] == WHITE:
            π[v] = u; DFS-VISIT(v)
    colour[u] = BLACK; f[u] = ++time
```

## DFS edge classification (directed graphs)
| Edge type | Condition |
|-----------|-----------|
| Tree edge | v WHITE when discovered from u |
| Back edge | v GRAY — indicates a **cycle** |
| Forward edge | v BLACK, d[u] < d[v] |
| Cross edge | v BLACK, d[u] > d[v] |

## Topological Sort (DAGs only)
Run DFS; prepend each vertex to output list when it **finishes** (turns BLACK).
Result is a valid topological order.  Time: O(V + E).

## Strongly Connected Components (Kosaraju)
1. DFS on G — record finish times.
2. DFS on G^T (reversed) in decreasing finish time order.
3. Each DFS tree in step 2 is one SCC.
"""

M9_EXERCISE_MD = "BFS shortest paths, connected components, topological sort."


def seed_module9(db: Session, course: Course) -> None:
    mod = _module(db, course, "Graph Algorithms: BFS and DFS", 9,
                  "BFS shortest paths, DFS timestamps, topological sort, SCCs.")

    _lesson(db, mod, "bfs-and-dfs",
            title="Breadth-First and Depth-First Search",
            lesson_type=LessonType.reading,
            content_md=M9_BFS_MD,
            duration_minutes=20,
            order_index=1)

    ex_lesson = _lesson(db, mod, "graph-traversal-exercises",
                        title="Graph Traversal — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M9_EXERCISE_MD,
                        duration_minutes=40,
                        order_index=2)

    # ── Exercise 9.1: BFS Shortest Path ──────────────────────────
    ex, _ = _exercise(db, ex_lesson, "bfs-shortest-path",
        title="BFS Shortest Path (Unweighted)",
        prompt_md=(
            "# BFS Shortest Path\n\n"
            "Given an **undirected unweighted** graph, find the shortest path "
            "(minimum edges) from vertex **s** to vertex **t**.\n\n"
            "**Input:**\n```\nn m\nu₁ v₁\n…\nuₘ vₘ\ns t\n```\n"
            "Vertices are 1-indexed.\n\n"
            "**Output:** shortest distance (number of edges), or `-1` if unreachable\n\n"
            "**Example**\n```\nInput:\n6 7\n1 2\n1 3\n2 4\n2 5\n3 6\n4 6\n5 6\n1 6\n\nOutput:\n2\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n"
                "from collections import deque\n\n"
                "def bfs(adj, n, s, t):\n"
                "    dist = [-1] * (n + 1)\n"
                "    dist[s] = 0\n"
                "    q = deque([s])\n"
                "    while q:\n"
                "        u = q.popleft()\n"
                "        for v in adj[u]:\n"
                "            if dist[v] == -1:\n"
                "                dist[v] = dist[u] + 1\n"
                "                if v == t:\n"
                "                    return dist[v]\n"
                "                q.append(v)\n"
                "    return dist[t]\n\n"
                "data = sys.stdin.read().split()\n"
                "idx = 0\n"
                "n, m = int(data[idx]), int(data[idx+1]); idx += 2\n"
                "adj = [[] for _ in range(n + 1)]\n"
                "for _ in range(m):\n"
                "    u, v = int(data[idx]), int(data[idx+1]); idx += 2\n"
                "    adj[u].append(v); adj[v].append(u)\n"
                "s, t = int(data[idx]), int(data[idx+1])\n"
                "print(bfs(adj, n, s, t))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;\n"
                "const n=d[i++],m=d[i++];\n"
                "const adj=Array.from({length:n+1},()=>[]);\n"
                "for(let j=0;j<m;j++){const u=d[i++],v=d[i++];adj[u].push(v);adj[v].push(u);}\n"
                "const s=d[i++],t=d[i++];\n"
                "const dist=new Array(n+1).fill(-1);dist[s]=0;\n"
                "const q=[s];\n"
                "for(let qi=0;qi<q.length;qi++){\n"
                "    const u=q[qi];\n"
                "    for(const v of adj[u])if(dist[v]===-1){dist[v]=dist[u]+1;q.push(v);}\n"
                "}\n"
                "console.log(dist[t]);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;\n"
                "const n=d[i++],m=d[i++];\n"
                "const adj:number[][]=Array.from({length:n+1},()=>[]);\n"
                "for(let j=0;j<m;j++){const u=d[i++],v=d[i++];adj[u].push(v);adj[v].push(u);}\n"
                "const s=d[i++],t=d[i++];\n"
                "const dist=new Array(n+1).fill(-1);dist[s]=0;\n"
                "const q=[s];\n"
                "for(let qi=0;qi<q.length;qi++){\n"
                "    const u=q[qi];\n"
                "    for(const v of adj[u])if(dist[v]===-1){dist[v]=dist[u]+1;q.push(v);}\n"
                "}\n"
                "console.log(dist[t]);\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),m=sc.nextInt();\n"
                "        List<List<Integer>> adj=new ArrayList<>();\n"
                "        for(int i=0;i<=n;i++) adj.add(new ArrayList<>());\n"
                "        for(int i=0;i<m;i++){int u=sc.nextInt(),v=sc.nextInt();adj.get(u).add(v);adj.get(v).add(u);}\n"
                "        int s=sc.nextInt(),t=sc.nextInt();\n"
                "        int[] dist=new int[n+1];Arrays.fill(dist,-1);dist[s]=0;\n"
                "        Queue<Integer> q=new LinkedList<>();q.add(s);\n"
                "        while(!q.isEmpty()){\n"
                "            int u=q.poll();\n"
                "            for(int v:adj.get(u))if(dist[v]==-1){dist[v]=dist[u]+1;q.add(v);}\n"
                "        }\n"
                "        System.out.println(dist[t]);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),m=int.Parse(first[1]);\n"
                "        var adj=new List<int>[n+1];\n"
                "        for(int i=0;i<=n;i++) adj[i]=new List<int>();\n"
                "        for(int i=0;i<m;i++){\n"
                "            var e=Console.ReadLine().Trim().Split();\n"
                "            int u=int.Parse(e[0]),v=int.Parse(e[1]);\n"
                "            adj[u].Add(v);adj[v].Add(u);\n"
                "        }\n"
                "        var st=Console.ReadLine().Trim().Split();\n"
                "        int s=int.Parse(st[0]),t=int.Parse(st[1]);\n"
                "        var dist=new int[n+1];Array.Fill(dist,-1);dist[s]=0;\n"
                "        var q=new Queue<int>();q.Enqueue(s);\n"
                "        while(q.Count>0){\n"
                "            int u=q.Dequeue();\n"
                "            foreach(var v in adj[u])if(dist[v]==-1){dist[v]=dist[u]+1;q.Enqueue(v);}\n"
                "        }\n"
                "        Console.WriteLine(dist[t]);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys;from collections import deque\n"
                "d=sys.stdin.read().split();i=0\n"
                "n,m=int(d[i]),int(d[i+1]);i+=2\n"
                "adj=[[] for _ in range(n+1)]\n"
                "for _ in range(m):\n"
                "    u,v=int(d[i]),int(d[i+1]);i+=2\n"
                "    adj[u].append(v);adj[v].append(u)\n"
                "s,t=int(d[i]),int(d[i+1])\n"
                "dist=[-1]*(n+1);dist[s]=0;q=deque([s])\n"
                "while q:\n"
                "    u=q.popleft()\n"
                "    for v in adj[u]:\n"
                "        if dist[v]==-1: dist[v]=dist[u]+1;q.append(v)\n"
                "print(dist[t])\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=20,
    )
    _cases(db, ex, [
        ("basic",       "6 7\n1 2\n1 3\n2 4\n2 5\n3 6\n4 6\n5 6\n1 6\n", "2",  False, 1),
        ("linear",      "4 3\n1 2\n2 3\n3 4\n1 4\n",                       "3",  False, 1),
        ("unreachable", "3 1\n1 2\n1 3\n",                                  "-1", False, 1),
        ("same-node",   "3 2\n1 2\n2 3\n2 2\n",                             "0",  True,  2),
        ("direct-edge", "5 4\n1 2\n2 3\n3 4\n4 5\n1 5\n",                  "4",  True,  2),
    ])

    # ── Exercise 9.2: Count Connected Components ──────────────────
    ex, _ = _exercise(db, ex_lesson, "count-connected-components",
        title="Count Connected Components",
        prompt_md=(
            "# Count Connected Components\n\n"
            "Given an **undirected** graph, count the number of connected components.\n\n"
            "**Input:**\n```\nn m\nu₁ v₁\n…\nuₘ vₘ\n```\n\n"
            "**Output:** number of connected components\n\n"
            "**Example**\n```\nInput:\n7 4\n1 2\n2 3\n4 5\n6 7\n\nOutput:\n3\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n"
                "from collections import deque\n\n"
                "data = sys.stdin.read().split()\n"
                "idx = 0\n"
                "n, m = int(data[idx]), int(data[idx+1]); idx += 2\n"
                "adj = [[] for _ in range(n + 1)]\n"
                "for _ in range(m):\n"
                "    u, v = int(data[idx]), int(data[idx+1]); idx += 2\n"
                "    adj[u].append(v); adj[v].append(u)\n\n"
                "visited = [False] * (n + 1)\n"
                "components = 0\n"
                "for start in range(1, n + 1):\n"
                "    if not visited[start]:\n"
                "        components += 1\n"
                "        # TODO: BFS/DFS from start, mark all reachable as visited\n"
                "print(components)\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++];\n"
                "const adj=Array.from({length:n+1},()=>[]);\n"
                "for(let j=0;j<m;j++){const u=d[i++],v=d[i++];adj[u].push(v);adj[v].push(u);}\n"
                "const vis=new Array(n+1).fill(false);\n"
                "let comp=0;\n"
                "for(let s=1;s<=n;s++){\n"
                "    if(!vis[s]){\n"
                "        comp++;const q=[s];vis[s]=true;\n"
                "        for(let qi=0;qi<q.length;qi++){\n"
                "            for(const v of adj[q[qi]])if(!vis[v]){vis[v]=true;q.push(v);}\n"
                "        }\n"
                "    }\n"
                "}\n"
                "console.log(comp);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++];\n"
                "const adj:number[][]=Array.from({length:n+1},()=>[]);\n"
                "for(let j=0;j<m;j++){const u=d[i++],v=d[i++];adj[u].push(v);adj[v].push(u);}\n"
                "const vis=new Array(n+1).fill(false);let comp=0;\n"
                "for(let s=1;s<=n;s++){\n"
                "    if(!vis[s]){\n"
                "        comp++;const q=[s];vis[s]=true;\n"
                "        for(let qi=0;qi<q.length;qi++)\n"
                "            for(const v of adj[q[qi]])if(!vis[v]){vis[v]=true;q.push(v);}\n"
                "    }\n"
                "}\n"
                "console.log(comp);\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),m=sc.nextInt();\n"
                "        List<List<Integer>> adj=new ArrayList<>();\n"
                "        for(int i=0;i<=n;i++) adj.add(new ArrayList<>());\n"
                "        for(int i=0;i<m;i++){int u=sc.nextInt(),v=sc.nextInt();adj.get(u).add(v);adj.get(v).add(u);}\n"
                "        boolean[] vis=new boolean[n+1];int comp=0;\n"
                "        for(int s=1;s<=n;s++){\n"
                "            if(!vis[s]){\n"
                "                comp++;Queue<Integer> q=new LinkedList<>();q.add(s);vis[s]=true;\n"
                "                while(!q.isEmpty()){\n"
                "                    for(int v:adj.get(q.poll()))if(!vis[v]){vis[v]=true;q.add(v);}\n"
                "                }\n"
                "            }\n"
                "        }\n"
                "        System.out.println(comp);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),m=int.Parse(first[1]);\n"
                "        var adj=new List<int>[n+1];\n"
                "        for(int i=0;i<=n;i++) adj[i]=new List<int>();\n"
                "        for(int i=0;i<m;i++){\n"
                "            var e=Console.ReadLine().Trim().Split();\n"
                "            int u=int.Parse(e[0]),v=int.Parse(e[1]);\n"
                "            adj[u].Add(v);adj[v].Add(u);\n"
                "        }\n"
                "        var vis=new bool[n+1];int comp=0;\n"
                "        for(int s=1;s<=n;s++){\n"
                "            if(!vis[s]){\n"
                "                comp++;var q=new Queue<int>();q.Enqueue(s);vis[s]=true;\n"
                "                while(q.Count>0){foreach(var v in adj[q.Dequeue()])if(!vis[v]){vis[v]=true;q.Enqueue(v);}}\n"
                "            }\n"
                "        }\n"
                "        Console.WriteLine(comp);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys;from collections import deque\n"
                "d=sys.stdin.read().split();i=0\n"
                "n,m=int(d[i]),int(d[i+1]);i+=2\n"
                "adj=[[] for _ in range(n+1)]\n"
                "for _ in range(m):\n"
                "    u,v=int(d[i]),int(d[i+1]);i+=2\n"
                "    adj[u].append(v);adj[v].append(u)\n"
                "vis=[False]*(n+1);comp=0\n"
                "for s in range(1,n+1):\n"
                "    if not vis[s]:\n"
                "        comp+=1;q=deque([s]);vis[s]=True\n"
                "        while q:\n"
                "            for v in adj[q.popleft()]:\n"
                "                if not vis[v]: vis[v]=True;q.append(v)\n"
                "print(comp)\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=15,
    )
    _cases(db, ex, [
        ("three-comps", "7 4\n1 2\n2 3\n4 5\n6 7\n",       "3", False, 1),
        ("one-comp",    "5 4\n1 2\n2 3\n3 4\n4 5\n",       "1", False, 1),
        ("isolated",    "4 0\n",                             "4", False, 1),
        ("all-conn",    "6 5\n1 2\n1 3\n1 4\n4 5\n5 6\n",  "1", True,  2),
    ])

    # ── Exercise 9.3: Topological Sort ───────────────────────────
    ex, _ = _exercise(db, ex_lesson, "topological-sort",
        title="Topological Sort",
        prompt_md=(
            "# Topological Sort\n\n"
            "Given a **directed acyclic graph (DAG)**, output a valid topological ordering "
            "of vertices using **Kahn's algorithm** (BFS-based):\n"
            "always pick the smallest available vertex with in-degree 0.\n\n"
            "If the graph contains a **cycle**, print `CYCLE`.\n\n"
            "**Input:**\n```\nn m\nu₁ v₁\n…\n```\nVertices 0-indexed.\n\n"
            "**Output:** space-separated topological order, or `CYCLE`\n\n"
            "**Example**\n```\nInput:\n6 6\n5 2\n5 0\n4 0\n4 1\n2 3\n3 1\n\nOutput:\n4 5 0 2 3 1\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n"
                "from collections import deque\n\n"
                "data = sys.stdin.read().split()\n"
                "idx = 0\n"
                "n, m = int(data[idx]), int(data[idx+1]); idx += 2\n"
                "adj = [[] for _ in range(n)]\n"
                "indegree = [0] * n\n"
                "for _ in range(m):\n"
                "    u, v = int(data[idx]), int(data[idx+1]); idx += 2\n"
                "    adj[u].append(v)\n"
                "    indegree[v] += 1\n\n"
                "# Kahn's: start with all vertices of in-degree 0\n"
                "# Use a min-heap (priority queue) to always pick smallest\n"
                "import heapq\n"
                "heap = [i for i in range(n) if indegree[i] == 0]\n"
                "heapq.heapify(heap)\n"
                "result = []\n"
                "while heap:\n"
                "    u = heapq.heappop(heap)\n"
                "    result.append(u)\n"
                "    for v in adj[u]:\n"
                "        indegree[v] -= 1\n"
                "        if indegree[v] == 0:\n"
                "            heapq.heappush(heap, v)\n\n"
                "if len(result) == n:\n"
                "    print(*result)\n"
                "else:\n"
                "    print('CYCLE')\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++];\n"
                "const adj=Array.from({length:n},()=>[]);\n"
                "const ind=new Array(n).fill(0);\n"
                "for(let j=0;j<m;j++){const u=d[i++],v=d[i++];adj[u].push(v);ind[v]++;}\n"
                "// Simple O(n^2) approach for determinism (pick min each time)\n"
                "const inq=new Array(n).fill(false);\n"
                "const res=[];\n"
                "for(let step=0;step<n;step++){\n"
                "    let pick=-1;\n"
                "    for(let u=0;u<n;u++) if(ind[u]===0&&!inq[u]&&(pick===-1||u<pick)) pick=u;\n"
                "    if(pick===-1){console.log('CYCLE');process.exit();}\n"
                "    inq[pick]=true;res.push(pick);\n"
                "    for(const v of adj[pick]) ind[v]--;\n"
                "}\n"
                "console.log(res.join(' '));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++];\n"
                "const adj:number[][]=Array.from({length:n},()=>[]);\n"
                "const ind=new Array(n).fill(0);\n"
                "for(let j=0;j<m;j++){const u=d[i++],v=d[i++];adj[u].push(v);ind[v]++;}\n"
                "const inq=new Array(n).fill(false);const res:number[]=[];\n"
                "for(let step=0;step<n;step++){\n"
                "    let pick=-1;\n"
                "    for(let u=0;u<n;u++) if(ind[u]===0&&!inq[u]&&(pick===-1||u<pick)) pick=u;\n"
                "    if(pick===-1){console.log('CYCLE');process.exit();}\n"
                "    inq[pick]=true;res.push(pick);\n"
                "    for(const v of adj[pick]) ind[v]--;\n"
                "}\n"
                "console.log(res.join(' '));\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),m=sc.nextInt();\n"
                "        List<List<Integer>> adj=new ArrayList<>();\n"
                "        for(int i=0;i<n;i++) adj.add(new ArrayList<>());\n"
                "        int[] ind=new int[n];\n"
                "        for(int i=0;i<m;i++){int u=sc.nextInt(),v=sc.nextInt();adj.get(u).add(v);ind[v]++;}\n"
                "        PriorityQueue<Integer> pq=new PriorityQueue<>();\n"
                "        for(int i=0;i<n;i++) if(ind[i]==0) pq.add(i);\n"
                "        StringBuilder sb=new StringBuilder();\n"
                "        int cnt=0;\n"
                "        while(!pq.isEmpty()){\n"
                "            int u=pq.poll();if(sb.length()>0)sb.append(' ');sb.append(u);cnt++;\n"
                "            for(int v:adj.get(u)){ind[v]--;if(ind[v]==0)pq.add(v);}\n"
                "        }\n"
                "        System.out.println(cnt==n?sb:\"CYCLE\");\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\nusing System.Text;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),m=int.Parse(first[1]);\n"
                "        var adj=new List<int>[n];\n"
                "        for(int i=0;i<n;i++) adj[i]=new List<int>();\n"
                "        var ind=new int[n];\n"
                "        for(int i=0;i<m;i++){\n"
                "            var e=Console.ReadLine().Trim().Split();\n"
                "            int u=int.Parse(e[0]),v=int.Parse(e[1]);adj[u].Add(v);ind[v]++;\n"
                "        }\n"
                "        var pq=new SortedSet<int>();\n"
                "        for(int i=0;i<n;i++) if(ind[i]==0) pq.Add(i);\n"
                "        var sb=new StringBuilder();int cnt=0;\n"
                "        while(pq.Count>0){\n"
                "            int u=pq.Min;pq.Remove(u);\n"
                "            if(sb.Length>0)sb.Append(' ');sb.Append(u);cnt++;\n"
                "            foreach(var v in adj[u]){ind[v]--;if(ind[v]==0)pq.Add(v);}\n"
                "        }\n"
                "        Console.WriteLine(cnt==n?sb.ToString():\"CYCLE\");\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys,heapq;from collections import deque\n"
                "d=sys.stdin.read().split();i=0\n"
                "n,m=int(d[i]),int(d[i+1]);i+=2\n"
                "adj=[[] for _ in range(n)];ind=[0]*n\n"
                "for _ in range(m):\n"
                "    u,v=int(d[i]),int(d[i+1]);i+=2\n"
                "    adj[u].append(v);ind[v]+=1\n"
                "h=[i for i in range(n) if ind[i]==0];heapq.heapify(h)\n"
                "res=[]\n"
                "while h:\n"
                "    u=heapq.heappop(h);res.append(u)\n"
                "    for v in adj[u]:\n"
                "        ind[v]-=1\n"
                "        if ind[v]==0: heapq.heappush(h,v)\n"
                "print(*res) if len(res)==n else print('CYCLE')\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=25,
    )
    _cases(db, ex, [
        ("classic", "6 6\n5 2\n5 0\n4 0\n4 1\n2 3\n3 1\n", "4 5 0 2 3 1", False, 1),
        ("cycle",   "4 4\n0 1\n1 2\n2 3\n3 0\n",            "CYCLE",        False, 1),
        ("linear",  "4 3\n0 1\n1 2\n2 3\n",                 "0 1 2 3",      True,  2),
        ("dag2",    "4 3\n0 1\n0 2\n1 3\n",                 "0 1 2 3",      True,  2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 10 — Shortest Path Algorithms
# ════════════════════════════════════════════════════════════════

M10_DIJKSTRA_MD = """\
# Dijkstra's Algorithm

**Input:** directed graph, non-negative edge weights, source s.
**Output:** shortest distances d[v] from s to every vertex v.

## Algorithm (with min-heap)
```
d[s] = 0; d[v] = ∞ for v ≠ s
PQ = min-heap containing (0, s)
while PQ not empty:
    (dist_u, u) = EXTRACT-MIN(PQ)
    if dist_u > d[u]: continue  # stale entry
    for each edge (u, v, w):
        if d[u] + w < d[v]:
            d[v] = d[u] + w
            INSERT(PQ, (d[v], v))
```

**Time:** O((V + E) log V) with binary heap;  O(V log V + E) with Fibonacci heap.

**Why non-negative weights only?**  Once a vertex is finalised (extracted from PQ),
its distance is assumed optimal.  A negative edge could provide a shorter path
through an already-finalised vertex — violating the greedy invariant.

# Bellman-Ford Algorithm

Handles **negative edge weights**.  Detects **negative cycles**.

```
d[s] = 0; d[v] = ∞ for v ≠ s
repeat V-1 times:
    for each edge (u, v, w):
        if d[u] + w < d[v]: d[v] = d[u] + w
# Detect negative cycle:
for each edge (u, v, w):
    if d[u] + w < d[v]: NEGATIVE CYCLE
```

**Time:** O(VE).  After k rounds, all shortest paths using ≤ k edges are correct.

# Floyd-Warshall (All-Pairs Shortest Paths)

**Time:** O(V³).  Handles negative weights, detects negative cycles via diagonal.

Recurrence:
```
dp[i][j][k] = min(dp[i][j][k-1],  dp[i][k][k-1] + dp[k][j][k-1])
```
"Shortest path from i to j using only {1..k} as intermediates."
"""

M10_EXERCISE_MD = "Implement Dijkstra and Bellman-Ford on directed weighted graphs."


def seed_module10(db: Session, course: Course) -> None:
    mod = _module(db, course, "Shortest Path Algorithms", 10,
                  "Dijkstra, Bellman-Ford, Floyd-Warshall — single and all-pairs shortest paths.")

    _lesson(db, mod, "dijkstra-bellman-ford",
            title="Dijkstra, Bellman-Ford, and Floyd-Warshall",
            lesson_type=LessonType.reading,
            content_md=M10_DIJKSTRA_MD,
            duration_minutes=25,
            order_index=1)

    ex_lesson = _lesson(db, mod, "shortest-path-exercises",
                        title="Shortest Paths — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M10_EXERCISE_MD,
                        duration_minutes=45,
                        order_index=2)

    # ── Exercise 10.1: Dijkstra's SSSP ───────────────────────────
    ex, _ = _exercise(db, ex_lesson, "dijkstra-sssp",
        title="Dijkstra's Single-Source Shortest Path",
        prompt_md=(
            "# Dijkstra's SSSP\n\n"
            "Find shortest distances from source **s** to all vertices in a "
            "directed graph with **non-negative** edge weights.\n\n"
            "**Input:**\n```\nn m s\nu₁ v₁ w₁\n…\n```\nVertices 1-indexed.\n\n"
            "**Output:** n space-separated distances d[1] d[2] … d[n].  "
            "Use `-1` for unreachable vertices.\n\n"
            "**Example**\n```\nInput:\n5 7 1\n1 2 4\n1 3 2\n2 3 1\n2 4 5\n3 4 8\n"
            "3 5 10\n4 5 2\n\nOutput:\n0 4 2 9 11\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n"
                "import heapq\n\n"
                "def dijkstra(n, adj, s):\n"
                "    INF = float('inf')\n"
                "    dist = [INF] * (n + 1)\n"
                "    dist[s] = 0\n"
                "    pq = [(0, s)]\n"
                "    while pq:\n"
                "        d, u = heapq.heappop(pq)\n"
                "        if d > dist[u]:\n"
                "            continue\n"
                "        for v, w in adj[u]:\n"
                "            # TODO: relax edge (u, v, w)\n"
                "            pass\n"
                "    return dist\n\n"
                "data = sys.stdin.read().split()\n"
                "idx = 0\n"
                "n, m, s = int(data[idx]), int(data[idx+1]), int(data[idx+2]); idx += 3\n"
                "adj = [[] for _ in range(n + 1)]\n"
                "for _ in range(m):\n"
                "    u, v, w = int(data[idx]), int(data[idx+1]), int(data[idx+2]); idx += 3\n"
                "    adj[u].append((v, w))\n"
                "dist = dijkstra(n, adj, s)\n"
                "print(*[-1 if dist[i] == float('inf') else dist[i] for i in range(1, n+1)])\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++],s=d[i++];\n"
                "const adj=Array.from({length:n+1},()=>[]);\n"
                "for(let j=0;j<m;j++){const u=d[i++],v=d[i++],w=d[i++];adj[u].push([v,w]);}\n"
                "const INF=1e15,dist=new Array(n+1).fill(INF);dist[s]=0;\n"
                "// Simple O(n^2) Dijkstra (no heap in plain JS)\n"
                "const vis=new Array(n+1).fill(false);\n"
                "for(let step=0;step<n;step++){\n"
                "    let u=-1;\n"
                "    for(let v=1;v<=n;v++) if(!vis[v]&&(u===-1||dist[v]<dist[u])) u=v;\n"
                "    if(dist[u]===INF) break;\n"
                "    vis[u]=true;\n"
                "    for(const [v,w] of adj[u]) if(dist[u]+w<dist[v]) dist[v]=dist[u]+w;\n"
                "}\n"
                "console.log(Array.from({length:n},(_,i)=>dist[i+1]===INF?-1:dist[i+1]).join(' '));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++],s=d[i++];\n"
                "const adj:number[][][]=Array.from({length:n+1},()=>[]);\n"
                "for(let j=0;j<m;j++){const u=d[i++],v=d[i++],w=d[i++];adj[u].push([v,w]);}\n"
                "const INF=1e15,dist=new Array(n+1).fill(INF);dist[s]=0;\n"
                "const vis=new Array(n+1).fill(false);\n"
                "for(let step=0;step<n;step++){\n"
                "    let u=-1;\n"
                "    for(let v=1;v<=n;v++) if(!vis[v]&&(u===-1||dist[v]<dist[u])) u=v;\n"
                "    if(dist[u]===INF) break;\n"
                "    vis[u]=true;\n"
                "    for(const [v,w] of adj[u]) if(dist[u]+w<dist[v]) dist[v]=dist[u]+w;\n"
                "}\n"
                "console.log(Array.from({length:n},(_,i)=>dist[i+1]===INF?-1:dist[i+1]).join(' '));\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),m=sc.nextInt(),s=sc.nextInt();\n"
                "        List<int[]>[] adj=new List[n+1];\n"
                "        for(int i=0;i<=n;i++) adj[i]=new ArrayList<>();\n"
                "        for(int i=0;i<m;i++){int u=sc.nextInt(),v=sc.nextInt(),w=sc.nextInt();adj[u].add(new int[]{v,w});}\n"
                "        long[] dist=new long[n+1];Arrays.fill(dist,Long.MAX_VALUE/2);dist[s]=0;\n"
                "        PriorityQueue<long[]> pq=new PriorityQueue<>(Comparator.comparingLong(a->a[0]));\n"
                "        pq.offer(new long[]{0,s});\n"
                "        while(!pq.isEmpty()){\n"
                "            long[] cur=pq.poll();long dd=cur[0];int u=(int)cur[1];\n"
                "            if(dd>dist[u]) continue;\n"
                "            for(int[] e:adj[u]) if(dist[u]+e[1]<dist[e[0]]){dist[e[0]]=dist[u]+e[1];pq.offer(new long[]{dist[e[0]],e[0]});}\n"
                "        }\n"
                "        StringBuilder sb=new StringBuilder();\n"
                "        for(int i=1;i<=n;i++){if(i>1)sb.append(' ');sb.append(dist[i]>=Long.MAX_VALUE/2?-1:dist[i]);}\n"
                "        System.out.println(sb);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\nusing System.Text;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),m=int.Parse(first[1]),s=int.Parse(first[2]);\n"
                "        var adj=new List<(int v,int w)>[n+1];\n"
                "        for(int i=0;i<=n;i++) adj[i]=new List<(int,int)>();\n"
                "        for(int i=0;i<m;i++){\n"
                "            var e=Console.ReadLine().Trim().Split();\n"
                "            adj[int.Parse(e[0])].Add((int.Parse(e[1]),int.Parse(e[2])));\n"
                "        }\n"
                "        var dist=new long[n+1];Array.Fill(dist,long.MaxValue/2);dist[s]=0;\n"
                "        var pq=new SortedSet<(long d,int u)>{(0,s)};\n"
                "        while(pq.Count>0){\n"
                "            var (dd,u)=pq.Min;pq.Remove(pq.Min);\n"
                "            if(dd>dist[u]) continue;\n"
                "            foreach(var (v,w) in adj[u]) if(dist[u]+w<dist[v]){pq.Remove((dist[v],v));dist[v]=dist[u]+w;pq.Add((dist[v],v));}\n"
                "        }\n"
                "        var sb=new StringBuilder();\n"
                "        for(int i=1;i<=n;i++){if(i>1)sb.Append(' ');sb.Append(dist[i]>=long.MaxValue/2?-1:dist[i]);}\n"
                "        Console.WriteLine(sb);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys,heapq\n"
                "d=sys.stdin.read().split();i=0\n"
                "n,m,s=int(d[i]),int(d[i+1]),int(d[i+2]);i+=3\n"
                "adj=[[] for _ in range(n+1)]\n"
                "for _ in range(m):\n"
                "    u,v,w=int(d[i]),int(d[i+1]),int(d[i+2]);i+=3\n"
                "    adj[u].append((v,w))\n"
                "INF=float('inf');dist=[INF]*(n+1);dist[s]=0\n"
                "pq=[(0,s)]\n"
                "while pq:\n"
                "    dd,u=heapq.heappop(pq)\n"
                "    if dd>dist[u]: continue\n"
                "    for v,w in adj[u]:\n"
                "        if dist[u]+w<dist[v]: dist[v]=dist[u]+w;heapq.heappush(pq,(dist[v],v))\n"
                "print(*[-1 if dist[i]==INF else dist[i] for i in range(1,n+1)])\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=25,
    )
    _cases(db, ex, [
        ("basic",    "5 7 1\n1 2 4\n1 3 2\n2 3 1\n2 4 5\n3 4 8\n3 5 10\n4 5 2\n", "0 4 2 9 11",    False, 1),
        ("linear",   "4 4 1\n1 2 1\n2 3 2\n3 4 3\n1 4 10\n",                        "0 1 3 6",       False, 1),
        ("unreachable","3 1 1\n1 2 5\n",                                              "0 5 -1",        True,  2),
        ("selfloop", "5 4 1\n1 2 3\n1 3 5\n3 4 2\n1 5 100\n",                       "0 3 5 7 100",   True,  2),
    ])

    # ── Exercise 10.2: Bellman-Ford ───────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "bellman-ford",
        title="Bellman-Ford Shortest Paths",
        prompt_md=(
            "# Bellman-Ford\n\n"
            "Find shortest distances from source **s** allowing **negative edge weights**.\n"
            "If a negative cycle is reachable from **s**, print `NEGATIVE CYCLE`.\n\n"
            "**Input:**\n```\nn m s\nu₁ v₁ w₁\n…\n```\nVertices 1-indexed.\n\n"
            "**Output:** n space-separated distances, or `NEGATIVE CYCLE`\n\n"
            "**Example**\n```\nInput:\n5 8 1\n1 2 -1\n1 3 4\n2 3 3\n2 4 2\n"
            "2 5 2\n3 4 5\n4 2 1\n5 4 -3\n\nOutput:\n0 -1 2 -2 1\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def bellman_ford(n, edges, s):\n"
                "    INF = float('inf')\n"
                "    dist = [INF] * (n + 1)\n"
                "    dist[s] = 0\n"
                "    for _ in range(n - 1):\n"
                "        for u, v, w in edges:\n"
                "            if dist[u] != INF and dist[u] + w < dist[v]:\n"
                "                dist[v] = dist[u] + w\n"
                "    # Check for negative cycles\n"
                "    for u, v, w in edges:\n"
                "        if dist[u] != INF and dist[u] + w < dist[v]:\n"
                "            return None  # negative cycle\n"
                "    return dist\n\n"
                "data = sys.stdin.read().split()\n"
                "idx = 0\n"
                "n, m, s = int(data[idx]), int(data[idx+1]), int(data[idx+2]); idx += 3\n"
                "edges = []\n"
                "for _ in range(m):\n"
                "    u, v, w = int(data[idx]), int(data[idx+1]), int(data[idx+2]); idx += 3\n"
                "    edges.append((u, v, w))\n"
                "result = bellman_ford(n, edges, s)\n"
                "if result is None:\n"
                "    print('NEGATIVE CYCLE')\n"
                "else:\n"
                "    print(*[-1 if result[i] == float('inf') else result[i] for i in range(1, n+1)])\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++],s=d[i++];\n"
                "const edges=[];\n"
                "for(let j=0;j<m;j++){edges.push([d[i++],d[i++],d[i++]]);}\n"
                "const INF=1e15,dist=new Array(n+1).fill(INF);dist[s]=0;\n"
                "for(let iter=0;iter<n-1;iter++)\n"
                "    for(const [u,v,w] of edges) if(dist[u]<INF&&dist[u]+w<dist[v]) dist[v]=dist[u]+w;\n"
                "let neg=false;\n"
                "for(const [u,v,w] of edges) if(dist[u]<INF&&dist[u]+w<dist[v]){neg=true;break;}\n"
                "if(neg) console.log('NEGATIVE CYCLE');\n"
                "else console.log(Array.from({length:n},(_,i)=>dist[i+1]>=INF?-1:dist[i+1]).join(' '));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++],s=d[i++];\n"
                "const edges:number[][]=[];\n"
                "for(let j=0;j<m;j++){edges.push([d[i++],d[i++],d[i++]]);}\n"
                "const INF=1e15,dist=new Array(n+1).fill(INF);dist[s]=0;\n"
                "for(let iter=0;iter<n-1;iter++)\n"
                "    for(const [u,v,w] of edges) if(dist[u]<INF&&dist[u]+w<dist[v]) dist[v]=dist[u]+w;\n"
                "let neg=false;\n"
                "for(const [u,v,w] of edges) if(dist[u]<INF&&dist[u]+w<dist[v]){neg=true;break;}\n"
                "if(neg) console.log('NEGATIVE CYCLE');\n"
                "else console.log(Array.from({length:n},(_,i)=>dist[i+1]>=INF?-1:dist[i+1]).join(' '));\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),m=sc.nextInt(),s=sc.nextInt();\n"
                "        int[][] edges=new int[m][3];\n"
                "        for(int i=0;i<m;i++){edges[i][0]=sc.nextInt();edges[i][1]=sc.nextInt();edges[i][2]=sc.nextInt();}\n"
                "        long[] dist=new long[n+1];Arrays.fill(dist,Long.MAX_VALUE/2);dist[s]=0;\n"
                "        for(int iter=0;iter<n-1;iter++)\n"
                "            for(int[] e:edges) if(dist[e[0]]<Long.MAX_VALUE/2&&dist[e[0]]+e[2]<dist[e[1]]) dist[e[1]]=dist[e[0]]+e[2];\n"
                "        boolean neg=false;\n"
                "        for(int[] e:edges) if(dist[e[0]]<Long.MAX_VALUE/2&&dist[e[0]]+e[2]<dist[e[1]]){neg=true;break;}\n"
                "        if(neg){System.out.println(\"NEGATIVE CYCLE\");return;}\n"
                "        StringBuilder sb=new StringBuilder();\n"
                "        for(int i=1;i<=n;i++){if(i>1)sb.append(' ');sb.append(dist[i]>=Long.MAX_VALUE/2?-1:dist[i]);}\n"
                "        System.out.println(sb);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Text;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),m=int.Parse(first[1]),s=int.Parse(first[2]);\n"
                "        var edges=new int[m][];\n"
                "        for(int i=0;i<m;i++){var e=Console.ReadLine().Trim().Split();edges[i]=new[]{int.Parse(e[0]),int.Parse(e[1]),int.Parse(e[2])};}\n"
                "        var dist=new long[n+1];Array.Fill(dist,long.MaxValue/2);dist[s]=0;\n"
                "        for(int it=0;it<n-1;it++) foreach(var e in edges) if(dist[e[0]]<long.MaxValue/2&&dist[e[0]]+e[2]<dist[e[1]]) dist[e[1]]=dist[e[0]]+e[2];\n"
                "        bool neg=false;\n"
                "        foreach(var e in edges) if(dist[e[0]]<long.MaxValue/2&&dist[e[0]]+e[2]<dist[e[1]]){neg=true;break;}\n"
                "        if(neg){Console.WriteLine(\"NEGATIVE CYCLE\");return;}\n"
                "        var sb=new StringBuilder();\n"
                "        for(int i=1;i<=n;i++){if(i>1)sb.Append(' ');sb.Append(dist[i]>=long.MaxValue/2?-1:dist[i]);}\n"
                "        Console.WriteLine(sb);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "d=sys.stdin.read().split();i=0\n"
                "n,m,s=int(d[i]),int(d[i+1]),int(d[i+2]);i+=3\n"
                "edges=[]\n"
                "for _ in range(m):\n"
                "    edges.append((int(d[i]),int(d[i+1]),int(d[i+2])));i+=3\n"
                "INF=float('inf');dist=[INF]*(n+1);dist[s]=0\n"
                "for _ in range(n-1):\n"
                "    for u,v,w in edges:\n"
                "        if dist[u]<INF and dist[u]+w<dist[v]: dist[v]=dist[u]+w\n"
                "for u,v,w in edges:\n"
                "    if dist[u]<INF and dist[u]+w<dist[v]: print('NEGATIVE CYCLE');exit()\n"
                "print(*[-1 if dist[i]==INF else dist[i] for i in range(1,n+1)])\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=10000,
        memory_limit_mb=256,
        points=25,
    )
    _cases(db, ex, [
        ("neg-weights", "5 8 1\n1 2 -1\n1 3 4\n2 3 3\n2 4 2\n2 5 2\n3 4 5\n4 2 1\n5 4 -3\n", "0 -1 2 -2 1", False, 1),
        ("neg-cycle",   "4 5 1\n1 2 1\n2 3 -1\n3 4 -1\n4 2 -1\n1 4 10\n",                      "NEGATIVE CYCLE", False, 1),
        ("simple-neg",  "3 3 1\n1 2 2\n2 3 -1\n1 3 4\n",                                        "0 2 1",          True,  2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 11 — Dynamic Programming
# ════════════════════════════════════════════════════════════════

M11_DP_MD = """\
# Dynamic Programming

DP applies when a problem has:
1. **Optimal substructure** — optimal solution uses optimal sub-solutions.
2. **Overlapping subproblems** — same sub-problems recur.

## Two implementations
- **Memoisation (top-down):** recursive + cache. Only solves needed sub-problems.
- **Tabulation (bottom-up):** fill a DP table iteratively. Easier to optimise space.

## Recipe
1. Define **state** — what parameters uniquely describe a sub-problem.
2. Write **recurrence** — how state(i) depends on smaller states.
3. Identify **base cases**.
4. Determine **evaluation order** (ensure sub-problems solved before use).
5. Read off the **answer** from the table.

## Classic problems

### Fibonacci
dp[0]=0, dp[1]=1, dp[n]=dp[n-1]+dp[n-2].  O(n) time, O(1) space with rolling vars.

### Coin Change (minimum coins)
dp[0]=0, dp[a] = min over coins c of (dp[a-c]+1).  O(A·k) time.

### Longest Common Subsequence (LCS)
dp[i][j] = LCS length of s1[:i] and s2[:j].
Recurrence: if s1[i-1]==s2[j-1]: dp[i][j]=dp[i-1][j-1]+1, else max(dp[i-1][j],dp[i][j-1]).

### 0-1 Knapsack
dp[j] = max value achievable with capacity j.
Process items: for j from W down to w_i: dp[j]=max(dp[j], dp[j-w_i]+v_i).

### Edit Distance (Levenshtein)
dp[i][j] = min edits to transform s1[:i] into s2[:j].
If s1[i-1]==s2[j-1]: dp[i][j]=dp[i-1][j-1], else 1+min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1]).
"""

M11_EXERCISE_MD = "Five DP problems spanning easy to hard."


def seed_module11(db: Session, course: Course) -> None:
    mod = _module(db, course, "Dynamic Programming", 11,
                  "Optimal substructure, overlapping subproblems, and five classic DP problems.")

    _lesson(db, mod, "dynamic-programming-intro",
            title="Introduction to Dynamic Programming",
            lesson_type=LessonType.reading,
            content_md=M11_DP_MD,
            duration_minutes=22,
            order_index=1)

    ex_lesson = _lesson(db, mod, "dp-exercises",
                        title="Dynamic Programming — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M11_EXERCISE_MD,
                        duration_minutes=55,
                        order_index=2)

    # ── Exercise 11.1: Coin Change ────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "coin-change",
        title="Coin Change (Minimum Coins)",
        prompt_md=(
            "# Coin Change\n\n"
            "Given coin denominations and a target **amount**, find the **minimum number "
            "of coins** needed to make that amount.  Each coin may be used unlimited times.\n"
            "If impossible, print `-1`.\n\n"
            "**Input:**\n```\nn amount\nc₁ c₂ … cₙ\n```\n\n"
            "**Output:** minimum coins or `-1`\n\n"
            "**Example**\n```\nInput:\n3 11\n1 5 6\n\nOutput:\n2\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def coin_change(coins, amount):\n"
                "    dp = [float('inf')] * (amount + 1)\n"
                "    dp[0] = 0\n"
                "    for a in range(1, amount + 1):\n"
                "        for c in coins:\n"
                "            if c <= a and dp[a - c] + 1 < dp[a]:\n"
                "                dp[a] = dp[a - c] + 1\n"
                "    return dp[amount] if dp[amount] != float('inf') else -1\n\n"
                "data = sys.stdin.read().split()\n"
                "n, amount = int(data[0]), int(data[1])\n"
                "coins = list(map(int, data[2:n+2]))\n"
                "print(coin_change(coins, amount))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],amount=d[1],coins=d.slice(2,n+2);\n"
                "const dp=new Array(amount+1).fill(Infinity);dp[0]=0;\n"
                "for(let a=1;a<=amount;a++)\n"
                "    for(const c of coins) if(c<=a&&dp[a-c]+1<dp[a]) dp[a]=dp[a-c]+1;\n"
                "console.log(dp[amount]===Infinity?-1:dp[amount]);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],amount=d[1],coins=d.slice(2,n+2);\n"
                "const dp=new Array(amount+1).fill(Infinity);dp[0]=0;\n"
                "for(let a=1;a<=amount;a++)\n"
                "    for(const c of coins) if(c<=a&&dp[a-c]+1<dp[a]) dp[a]=dp[a-c]+1;\n"
                "console.log(dp[amount]===Infinity?-1:dp[amount]);\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),amount=sc.nextInt();\n"
                "        int[] coins=new int[n];\n"
                "        for(int i=0;i<n;i++) coins[i]=sc.nextInt();\n"
                "        int[] dp=new int[amount+1];Arrays.fill(dp,Integer.MAX_VALUE);dp[0]=0;\n"
                "        for(int a=1;a<=amount;a++)\n"
                "            for(int c:coins) if(c<=a&&dp[a-c]!=Integer.MAX_VALUE&&dp[a-c]+1<dp[a]) dp[a]=dp[a-c]+1;\n"
                "        System.out.println(dp[amount]==Integer.MAX_VALUE?-1:dp[amount]);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),amount=int.Parse(first[1]);\n"
                "        var coins=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        var dp=new int[amount+1];Array.Fill(dp,int.MaxValue);dp[0]=0;\n"
                "        for(int a=1;a<=amount;a++)\n"
                "            foreach(var c in coins) if(c<=a&&dp[a-c]!=int.MaxValue&&dp[a-c]+1<dp[a]) dp[a]=dp[a-c]+1;\n"
                "        Console.WriteLine(dp[amount]==int.MaxValue?-1:dp[amount]);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={"python": "import sys\nd=sys.stdin.read().split();n,amt=int(d[0]),int(d[1]);coins=list(map(int,d[2:n+2]))\ndp=[float('inf')]*(amt+1);dp[0]=0\nfor a in range(1,amt+1):\n    for c in coins:\n        if c<=a and dp[a-c]+1<dp[a]: dp[a]=dp[a-c]+1\nprint(-1 if dp[amt]==float('inf') else dp[amt])\n"},
        supported_languages=LANGS, time_limit_ms=5000, memory_limit_mb=256, points=20,
    )
    _cases(db, ex, [
        ("basic",      "3 11\n1 5 6\n",   "2",  False, 1),
        ("one-coin",   "2 3\n2 3\n",      "1",  False, 1),
        ("impossible", "3 7\n2 4 8\n",    "-1", False, 1),
        ("many-coins", "4 6\n1 2 3 4\n",  "2",  True,  2),
        ("large",      "2 100\n1 99\n",   "2",  True,  2),
    ])

    # ── Exercise 11.2: Longest Common Subsequence ─────────────────
    ex, _ = _exercise(db, ex_lesson, "longest-common-subsequence",
        title="Longest Common Subsequence",
        prompt_md=(
            "# Longest Common Subsequence (LCS)\n\n"
            "Find the **length** of the longest common subsequence of two strings.\n"
            "A subsequence preserves order but need not be contiguous.\n\n"
            "**Input:** two lines, one string each\n\n"
            "**Output:** LCS length\n\n"
            "**Example**\n```\nInput:\nABCBDAB\nBDCAB\n\nOutput:\n4\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def lcs(s1, s2):\n"
                "    m, n = len(s1), len(s2)\n"
                "    dp = [[0] * (n + 1) for _ in range(m + 1)]\n"
                "    for i in range(1, m + 1):\n"
                "        for j in range(1, n + 1):\n"
                "            if s1[i-1] == s2[j-1]:\n"
                "                dp[i][j] = dp[i-1][j-1] + 1\n"
                "            else:\n"
                "                dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n"
                "    return dp[m][n]\n\n"
                "lines = sys.stdin.read().strip().split('\\n')\n"
                "print(lcs(lines[0].strip(), lines[1].strip()))\n"
            ),
            "javascript": (
                "const lines=require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
                "const s1=lines[0].trim(),s2=lines[1].trim();\n"
                "const m=s1.length,n=s2.length;\n"
                "const dp=Array.from({length:m+1},()=>new Array(n+1).fill(0));\n"
                "for(let i=1;i<=m;i++)\n"
                "    for(let j=1;j<=n;j++)\n"
                "        dp[i][j]=s1[i-1]===s2[j-1]?dp[i-1][j-1]+1:Math.max(dp[i-1][j],dp[i][j-1]);\n"
                "console.log(dp[m][n]);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const lines=fs.readFileSync(0,'utf8').trim().split('\\n');\n"
                "const s1=lines[0].trim(),s2=lines[1].trim();\n"
                "const m=s1.length,n=s2.length;\n"
                "const dp=Array.from({length:m+1},()=>new Array(n+1).fill(0));\n"
                "for(let i=1;i<=m;i++)\n"
                "    for(let j=1;j<=n;j++)\n"
                "        dp[i][j]=s1[i-1]===s2[j-1]?dp[i-1][j-1]+1:Math.max(dp[i-1][j],dp[i][j-1]);\n"
                "console.log(dp[m][n]);\n"
            ),
            "java": (
                "import java.util.Scanner;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        String s1=sc.nextLine().trim(),s2=sc.nextLine().trim();\n"
                "        int m=s1.length(),n=s2.length();\n"
                "        int[][] dp=new int[m+1][n+1];\n"
                "        for(int i=1;i<=m;i++)\n"
                "            for(int j=1;j<=n;j++)\n"
                "                dp[i][j]=s1.charAt(i-1)==s2.charAt(j-1)?dp[i-1][j-1]+1:Math.max(dp[i-1][j],dp[i][j-1]);\n"
                "        System.out.println(dp[m][n]);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        string s1=Console.ReadLine()?.Trim()??\"\";\n"
                "        string s2=Console.ReadLine()?.Trim()??\"\";\n"
                "        int m=s1.Length,n=s2.Length;\n"
                "        var dp=new int[m+1,n+1];\n"
                "        for(int i=1;i<=m;i++)\n"
                "            for(int j=1;j<=n;j++)\n"
                "                dp[i,j]=s1[i-1]==s2[j-1]?dp[i-1,j-1]+1:Math.Max(dp[i-1,j],dp[i,j-1]);\n"
                "        Console.WriteLine(dp[m,n]);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={"python": "import sys\nlines=sys.stdin.read().strip().split('\\n')\ns1,s2=lines[0].strip(),lines[1].strip()\nm,n=len(s1),len(s2)\ndp=[[0]*(n+1) for _ in range(m+1)]\nfor i in range(1,m+1):\n    for j in range(1,n+1):\n        dp[i][j]=dp[i-1][j-1]+1 if s1[i-1]==s2[j-1] else max(dp[i-1][j],dp[i][j-1])\nprint(dp[m][n])\n"},
        supported_languages=LANGS, time_limit_ms=5000, memory_limit_mb=256, points=20,
    )
    _cases(db, ex, [
        ("classic",  "ABCBDAB\nBDCAB\n",   "4", False, 1),
        ("equal",    "ABAB\nBABA\n",        "3", False, 1),
        ("same-str", "ABC\nABC\n",          "3", False, 1),
        ("no-common","ABC\nDEF\n",          "0", True,  1),
        ("hidden",   "AGGTAB\nGXTXAYB\n",  "4", True,  2),
    ])

    # ── Exercise 11.3: 0-1 Knapsack ──────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "knapsack-01",
        title="0-1 Knapsack",
        prompt_md=(
            "# 0-1 Knapsack\n\n"
            "Given **n** items each with a weight and value, and a knapsack of capacity **W**, "
            "find the **maximum total value** achievable without exceeding the capacity.\n"
            "Each item can be taken **at most once**.\n\n"
            "**Input:**\n```\nn W\nw₁ v₁\n…\nwₙ vₙ\n```\n\n"
            "**Output:** maximum value\n\n"
            "**Example**\n```\nInput:\n4 6\n1 1\n2 6\n3 10\n5 16\n\nOutput:\n17\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def knapsack(items, W):\n"
                "    dp = [0] * (W + 1)\n"
                "    for w, v in items:\n"
                "        # Traverse backwards to avoid using item twice\n"
                "        for j in range(W, w - 1, -1):\n"
                "            dp[j] = max(dp[j], dp[j - w] + v)\n"
                "    return dp[W]\n\n"
                "data = sys.stdin.read().split()\n"
                "idx = 0\n"
                "n, W = int(data[idx]), int(data[idx+1]); idx += 2\n"
                "items = []\n"
                "for _ in range(n):\n"
                "    w, v = int(data[idx]), int(data[idx+1]); idx += 2\n"
                "    items.append((w, v))\n"
                "print(knapsack(items, W))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],W=d[i++];\n"
                "const items=[];for(let j=0;j<n;j++) items.push([d[i++],d[i++]]);\n"
                "const dp=new Array(W+1).fill(0);\n"
                "for(const [w,v] of items)\n"
                "    for(let j=W;j>=w;j--) dp[j]=Math.max(dp[j],dp[j-w]+v);\n"
                "console.log(dp[W]);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],W=d[i++];\n"
                "const items:number[][]=[];for(let j=0;j<n;j++) items.push([d[i++],d[i++]]);\n"
                "const dp=new Array(W+1).fill(0);\n"
                "for(const [w,v] of items)\n"
                "    for(let j=W;j>=w;j--) dp[j]=Math.max(dp[j],dp[j-w]+v);\n"
                "console.log(dp[W]);\n"
            ),
            "java": (
                "import java.util.Scanner;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),W=sc.nextInt();\n"
                "        int[] ws=new int[n],vs=new int[n];\n"
                "        for(int i=0;i<n;i++){ws[i]=sc.nextInt();vs[i]=sc.nextInt();}\n"
                "        int[] dp=new int[W+1];\n"
                "        for(int i=0;i<n;i++)\n"
                "            for(int j=W;j>=ws[i];j--) dp[j]=Math.max(dp[j],dp[j-ws[i]]+vs[i]);\n"
                "        System.out.println(dp[W]);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),W=int.Parse(first[1]);\n"
                "        var ws=new int[n];var vs=new int[n];\n"
                "        for(int i=0;i<n;i++){var row=Console.ReadLine().Trim().Split();ws[i]=int.Parse(row[0]);vs[i]=int.Parse(row[1]);}\n"
                "        var dp=new int[W+1];\n"
                "        for(int i=0;i<n;i++)\n"
                "            for(int j=W;j>=ws[i];j--) dp[j]=Math.Max(dp[j],dp[j-ws[i]]+vs[i]);\n"
                "        Console.WriteLine(dp[W]);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={"python": "import sys\nd=sys.stdin.read().split();i=0\nn,W=int(d[i]),int(d[i+1]);i+=2\nit=[]\nfor _ in range(n):\n    it.append((int(d[i]),int(d[i+1])));i+=2\ndp=[0]*(W+1)\nfor w,v in it:\n    for j in range(W,w-1,-1): dp[j]=max(dp[j],dp[j-w]+v)\nprint(dp[W])\n"},
        supported_languages=LANGS, time_limit_ms=5000, memory_limit_mb=256, points=20,
    )
    _cases(db, ex, [
        ("classic", "4 6\n1 1\n2 6\n3 10\n5 16\n", "17", False, 1),
        ("tight-cap","3 5\n2 3\n3 4\n4 5\n",        "7",  False, 1),
        ("single",  "1 5\n3 10\n",                  "10", False, 1),
        ("no-fit",  "2 1\n2 5\n3 8\n",              "0",  True,  1),
        ("hidden",  "5 10\n2 6\n2 10\n3 12\n5 15\n5 15\n", "37", True, 2),
    ])

    # ── Exercise 11.4: Edit Distance ──────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "edit-distance",
        title="Edit Distance (Levenshtein)",
        prompt_md=(
            "# Edit Distance\n\n"
            "Find the minimum number of single-character **insert**, **delete**, or **substitute** "
            "operations to transform string **s1** into string **s2**.\n\n"
            "**Input:** two lines, one string each\n\n"
            "**Output:** edit distance\n\n"
            "**Example**\n```\nInput:\nhorse\nros\n\nOutput:\n3\n```"
        ),
        difficulty=Difficulty.hard,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def edit_distance(s1, s2):\n"
                "    m, n = len(s1), len(s2)\n"
                "    dp = list(range(n + 1))  # base: transform empty → s2[:j]\n"
                "    for i in range(1, m + 1):\n"
                "        prev = dp[0]\n"
                "        dp[0] = i\n"
                "        for j in range(1, n + 1):\n"
                "            tmp = dp[j]\n"
                "            if s1[i-1] == s2[j-1]:\n"
                "                dp[j] = prev\n"
                "            else:\n"
                "                dp[j] = 1 + min(prev, dp[j], dp[j-1])\n"
                "            prev = tmp\n"
                "    return dp[n]\n\n"
                "lines = sys.stdin.read().strip().split('\\n')\n"
                "print(edit_distance(lines[0].strip(), lines[1].strip()))\n"
            ),
            "javascript": (
                "const lines=require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
                "const s1=lines[0].trim(),s2=lines[1].trim();\n"
                "const m=s1.length,n=s2.length;\n"
                "let dp=Array.from({length:n+1},(_,i)=>i);\n"
                "for(let i=1;i<=m;i++){\n"
                "    let prev=dp[0];dp[0]=i;\n"
                "    for(let j=1;j<=n;j++){\n"
                "        const tmp=dp[j];\n"
                "        dp[j]=s1[i-1]===s2[j-1]?prev:1+Math.min(prev,dp[j],dp[j-1]);\n"
                "        prev=tmp;\n"
                "    }\n"
                "}\n"
                "console.log(dp[n]);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const lines=fs.readFileSync(0,'utf8').trim().split('\\n');\n"
                "const s1=lines[0].trim(),s2=lines[1].trim();\n"
                "const m=s1.length,n=s2.length;\n"
                "let dp=Array.from({length:n+1},(_,i)=>i);\n"
                "for(let i=1;i<=m;i++){\n"
                "    let prev=dp[0];dp[0]=i;\n"
                "    for(let j=1;j<=n;j++){\n"
                "        const tmp=dp[j];\n"
                "        dp[j]=s1[i-1]===s2[j-1]?prev:1+Math.min(prev,dp[j],dp[j-1]);\n"
                "        prev=tmp;\n"
                "    }\n"
                "}\n"
                "console.log(dp[n]);\n"
            ),
            "java": (
                "import java.util.Scanner;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        String s1=sc.nextLine().trim(),s2=sc.nextLine().trim();\n"
                "        int m=s1.length(),n=s2.length();\n"
                "        int[] dp=new int[n+1];\n"
                "        for(int j=0;j<=n;j++) dp[j]=j;\n"
                "        for(int i=1;i<=m;i++){\n"
                "            int prev=dp[0];dp[0]=i;\n"
                "            for(int j=1;j<=n;j++){\n"
                "                int tmp=dp[j];\n"
                "                dp[j]=s1.charAt(i-1)==s2.charAt(j-1)?prev:1+Math.min(prev,Math.min(dp[j],dp[j-1]));\n"
                "                prev=tmp;\n"
                "            }\n"
                "        }\n"
                "        System.out.println(dp[n]);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        string s1=Console.ReadLine()?.Trim()??\"\";\n"
                "        string s2=Console.ReadLine()?.Trim()??\"\";\n"
                "        int m=s1.Length,n=s2.Length;\n"
                "        var dp=new int[n+1];\n"
                "        for(int j=0;j<=n;j++) dp[j]=j;\n"
                "        for(int i=1;i<=m;i++){\n"
                "            int prev=dp[0];dp[0]=i;\n"
                "            for(int j=1;j<=n;j++){\n"
                "                int tmp=dp[j];\n"
                "                dp[j]=s1[i-1]==s2[j-1]?prev:1+Math.Min(prev,Math.Min(dp[j],dp[j-1]));\n"
                "                prev=tmp;\n"
                "            }\n"
                "        }\n"
                "        Console.WriteLine(dp[n]);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={"python": "import sys\nlines=sys.stdin.read().strip().split('\\n')\ns1,s2=lines[0].strip(),lines[1].strip()\nm,n=len(s1),len(s2)\ndp=list(range(n+1))\nfor i in range(1,m+1):\n    prev=dp[0];dp[0]=i\n    for j in range(1,n+1):\n        tmp=dp[j]\n        dp[j]=prev if s1[i-1]==s2[j-1] else 1+min(prev,dp[j],dp[j-1])\n        prev=tmp\nprint(dp[n])\n"},
        supported_languages=LANGS, time_limit_ms=5000, memory_limit_mb=256, points=30,
    )
    _cases(db, ex, [
        ("horse-ros",  "horse\nros\n",         "3", False, 1),
        ("kitten-sit", "kitten\nsitting\n",    "3", False, 1),
        ("same",       "abc\nabc\n",           "0", False, 1),
        ("empty-to",   "\nabc\n",              "3", True,  1),
        ("hidden",     "intention\nexecution\n","5", True,  2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 12 — Greedy Algorithms and Minimum Spanning Trees
# ════════════════════════════════════════════════════════════════

M12_GREEDY_MD = """\
# Greedy Algorithms

A **greedy algorithm** makes the locally optimal choice at each step,
hoping to reach a global optimum.

**When does greedy work?**
The problem must have:
1. **Greedy-choice property** — a global optimum can be reached by always making the locally best choice.
2. **Optimal substructure** — an optimal solution contains optimal sub-solutions.

## Activity Selection Problem
Select the maximum number of non-overlapping activities.
**Greedy rule:** always pick the activity with the **earliest finish time** that is compatible with previous selections.

Proof: exchange argument — swapping a non-greedy choice for the greedy one never decreases the count.

## Huffman Coding
Build optimal prefix-free codes by repeatedly merging the two lowest-frequency nodes.
Result: shorter codes for more frequent symbols → minimum expected bits per symbol.

## Greedy ≠ DP
| | Greedy | DP |
|--|--------|-----|
| Makes | One irrevocable choice | All choices, picks best |
| Subproblems | One smaller subproblem | Overlapping subproblems |
| Speed | Usually faster | Usually slower |
| Correctness | Needs proof | Always optimal if recurrence correct |

# Minimum Spanning Trees

A **minimum spanning tree (MST)** of a weighted undirected graph is a spanning
tree with minimum total edge weight.

## Cut Property
The minimum-weight edge crossing any cut of the graph belongs to some MST.

## Kruskal's Algorithm — O(E log E)
Sort edges by weight; greedily add the cheapest edge that does not form a cycle.
Use **Union-Find** (with path compression + union by rank) for O(α(n)) ≈ O(1) cycle check.

## Prim's Algorithm — O(E log V) with binary heap
Grow the MST from a single vertex; always add the minimum-weight edge connecting
the current tree to a vertex outside it.  Use a priority queue.
"""

M12_EXERCISE_MD = "Activity selection and minimum spanning tree (Kruskal's)."


def seed_module12(db: Session, course: Course) -> None:
    mod = _module(db, course, "Greedy Algorithms and Minimum Spanning Trees", 12,
                  "Greedy correctness, activity selection, Huffman coding, Kruskal's MST.")

    _lesson(db, mod, "greedy-and-mst",
            title="Greedy Algorithms and Minimum Spanning Trees",
            lesson_type=LessonType.reading,
            content_md=M12_GREEDY_MD,
            duration_minutes=20,
            order_index=1)

    ex_lesson = _lesson(db, mod, "greedy-mst-exercises",
                        title="Greedy and MST — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M12_EXERCISE_MD,
                        duration_minutes=40,
                        order_index=2)

    # ── Exercise 12.1: Activity Selection ────────────────────────
    ex, _ = _exercise(db, ex_lesson, "activity-selection",
        title="Activity Selection",
        prompt_md=(
            "# Activity Selection\n\n"
            "Given **n** activities each with a start and end time, select the "
            "**maximum number** of non-overlapping activities.\n"
            "Two activities are compatible if the next starts **≥** the previous end.\n\n"
            "**Input:**\n```\nn\ns₁ e₁\n…\nsₙ eₙ\n```\n\n"
            "**Output:** maximum number of activities\n\n"
            "**Example**\n```\nInput:\n3\n1 2\n2 3\n3 4\n\nOutput:\n3\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def activity_selection(activities):\n"
                "    # Sort by finish time\n"
                "    activities.sort(key=lambda x: x[1])\n"
                "    count = 0\n"
                "    last_end = -1\n"
                "    for start, end in activities:\n"
                "        if start >= last_end:\n"
                "            count += 1\n"
                "            last_end = end\n"
                "    return count\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "activities = [(int(data[1 + 2*i]), int(data[2 + 2*i])) for i in range(n)]\n"
                "print(activity_selection(activities))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0];\n"
                "const acts=[];\n"
                "for(let i=0;i<n;i++) acts.push([d[1+2*i],d[2+2*i]]);\n"
                "acts.sort((a,b)=>a[1]-b[1]);\n"
                "let cnt=0,last=-1;\n"
                "for(const [s,e] of acts) if(s>=last){cnt++;last=e;}\n"
                "console.log(cnt);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0];\n"
                "const acts:number[][]=[];\n"
                "for(let i=0;i<n;i++) acts.push([d[1+2*i],d[2+2*i]]);\n"
                "acts.sort((a,b)=>a[1]-b[1]);\n"
                "let cnt=0,last=-1;\n"
                "for(const [s,e] of acts) if(s>=last){cnt++;last=e;}\n"
                "console.log(cnt);\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();\n"
                "        int[][] acts=new int[n][2];\n"
                "        for(int i=0;i<n;i++){acts[i][0]=sc.nextInt();acts[i][1]=sc.nextInt();}\n"
                "        Arrays.sort(acts,Comparator.comparingInt(a->a[1]));\n"
                "        int cnt=0,last=-1;\n"
                "        for(int[] a:acts) if(a[0]>=last){cnt++;last=a[1];}\n"
                "        System.out.println(cnt);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var acts=new List<(int s,int e)>();\n"
                "        for(int i=0;i<n;i++){var row=Console.ReadLine().Trim().Split();acts.Add((int.Parse(row[0]),int.Parse(row[1])));}\n"
                "        acts.Sort((a,b)=>a.e-b.e);\n"
                "        int cnt=0,last=-1;\n"
                "        foreach(var (s,e) in acts) if(s>=last){cnt++;last=e;}\n"
                "        Console.WriteLine(cnt);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={"python": "import sys\nd=sys.stdin.read().split();n=int(d[0])\nacts=[(int(d[1+2*i]),int(d[2+2*i])) for i in range(n)]\nacts.sort(key=lambda x:x[1])\ncnt=0;last=-1\nfor s,e in acts:\n    if s>=last: cnt+=1;last=e\nprint(cnt)\n"},
        supported_languages=LANGS, time_limit_ms=5000, memory_limit_mb=256, points=20,
    )
    _cases(db, ex, [
        ("adjacent",  "3\n1 2\n2 3\n3 4\n",                                                                  "3", False, 1),
        ("overlap",   "4\n1 3\n2 4\n3 5\n4 6\n",                                                             "2", False, 1),
        ("classic",   "11\n1 4\n3 5\n0 6\n5 7\n3 8\n5 9\n6 10\n8 11\n8 12\n2 13\n12 14\n",                 "4", False, 1),
        ("identical", "3\n1 4\n1 4\n1 4\n",                                                                  "1", True,  2),
        ("single",    "1\n0 10\n",                                                                            "1", True,  1),
    ])

    # ── Exercise 12.2: Minimum Spanning Tree (Kruskal's) ─────────
    ex, _ = _exercise(db, ex_lesson, "minimum-spanning-tree",
        title="Minimum Spanning Tree (Kruskal's)",
        prompt_md=(
            "# Minimum Spanning Tree\n\n"
            "Find the **total weight** of the Minimum Spanning Tree of an "
            "undirected weighted connected graph using **Kruskal's algorithm**.\n\n"
            "**Input:**\n```\nn m\nu₁ v₁ w₁\n…\n```\nVertices 1-indexed.\n\n"
            "**Output:** MST total weight\n\n"
            "**Example**\n```\nInput:\n4 5\n1 2 1\n1 3 4\n2 3 2\n2 4 5\n3 4 3\n\nOutput:\n6\n```"
        ),
        difficulty=Difficulty.hard,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def find(parent, x):\n"
                "    if parent[x] != x:\n"
                "        parent[x] = find(parent, parent[x])  # path compression\n"
                "    return parent[x]\n\n"
                "def union(parent, rank, x, y):\n"
                "    px, py = find(parent, x), find(parent, y)\n"
                "    if px == py:\n"
                "        return False\n"
                "    if rank[px] < rank[py]:\n"
                "        px, py = py, px\n"
                "    parent[py] = px\n"
                "    if rank[px] == rank[py]:\n"
                "        rank[px] += 1\n"
                "    return True\n\n"
                "data = sys.stdin.read().split()\n"
                "idx = 0\n"
                "n, m = int(data[idx]), int(data[idx+1]); idx += 2\n"
                "edges = []\n"
                "for _ in range(m):\n"
                "    u, v, w = int(data[idx]), int(data[idx+1]), int(data[idx+2]); idx += 3\n"
                "    edges.append((w, u, v))\n"
                "edges.sort()\n"
                "parent = list(range(n + 1))\n"
                "rank = [0] * (n + 1)\n"
                "mst_weight = 0\n"
                "for w, u, v in edges:\n"
                "    if union(parent, rank, u, v):\n"
                "        mst_weight += w\n"
                "print(mst_weight)\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++];\n"
                "const edges=[];\n"
                "for(let j=0;j<m;j++){edges.push([d[i++],d[i++],d[i++]]);}\n"
                "edges.sort((a,b)=>a[2]-b[2]);\n"
                "const par=Array.from({length:n+1},(_,i)=>i),rnk=new Array(n+1).fill(0);\n"
                "function find(x){if(par[x]!==x)par[x]=find(par[x]);return par[x];}\n"
                "function union(x,y){const px=find(x),py=find(y);if(px===py)return false;\n"
                "    if(rnk[px]<rnk[py])par[px]=py;else if(rnk[px]>rnk[py])par[py]=px;else{par[py]=px;rnk[px]++;}return true;}\n"
                "let total=0;\n"
                "for(const [u,v,w] of edges) if(union(u,v)) total+=w;\n"
                "console.log(total);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "let i=0;const n=d[i++],m=d[i++];\n"
                "const edges:number[][]=[];\n"
                "for(let j=0;j<m;j++){edges.push([d[i++],d[i++],d[i++]]);}\n"
                "edges.sort((a,b)=>a[2]-b[2]);\n"
                "const par=Array.from({length:n+1},(_,i)=>i),rnk=new Array(n+1).fill(0);\n"
                "function find(x:number):number{if(par[x]!==x)par[x]=find(par[x]);return par[x];}\n"
                "function union(x:number,y:number):boolean{const px=find(x),py=find(y);if(px===py)return false;\n"
                "    if(rnk[px]<rnk[py])par[px]=py;else if(rnk[px]>rnk[py])par[py]=px;else{par[py]=px;rnk[px]++;}return true;}\n"
                "let total=0;\n"
                "for(const [u,v,w] of edges) if(union(u,v)) total+=w;\n"
                "console.log(total);\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    static int[] par,rnk;\n"
                "    static int find(int x){if(par[x]!=x)par[x]=find(par[x]);return par[x];}\n"
                "    static boolean union(int x,int y){\n"
                "        int px=find(x),py=find(y);if(px==py)return false;\n"
                "        if(rnk[px]<rnk[py]){int t=px;px=py;py=t;}\n"
                "        par[py]=px;if(rnk[px]==rnk[py])rnk[px]++;return true;\n"
                "    }\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),m=sc.nextInt();\n"
                "        int[][] edges=new int[m][3];\n"
                "        for(int i=0;i<m;i++){edges[i][0]=sc.nextInt();edges[i][1]=sc.nextInt();edges[i][2]=sc.nextInt();}\n"
                "        Arrays.sort(edges,Comparator.comparingInt(e->e[2]));\n"
                "        par=new int[n+1];rnk=new int[n+1];\n"
                "        for(int i=1;i<=n;i++) par[i]=i;\n"
                "        long total=0;\n"
                "        for(int[] e:edges) if(union(e[0],e[1])) total+=e[2];\n"
                "        System.out.println(total);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Linq;\n"
                "class Solution {\n"
                "    static int[] par,rnk;\n"
                "    static int Find(int x){if(par[x]!=x)par[x]=Find(par[x]);return par[x];}\n"
                "    static bool Union(int x,int y){\n"
                "        int px=Find(x),py=Find(y);if(px==py)return false;\n"
                "        if(rnk[px]<rnk[py]){int t=px;px=py;py=t;}\n"
                "        par[py]=px;if(rnk[px]==rnk[py])rnk[px]++;return true;\n"
                "    }\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),m=int.Parse(first[1]);\n"
                "        var edges=new int[m][];\n"
                "        for(int i=0;i<m;i++){var e=Console.ReadLine().Trim().Split();edges[i]=new[]{int.Parse(e[0]),int.Parse(e[1]),int.Parse(e[2])};}\n"
                "        Array.Sort(edges,(a,b)=>a[2]-b[2]);\n"
                "        par=new int[n+1];rnk=new int[n+1];\n"
                "        for(int i=1;i<=n;i++) par[i]=i;\n"
                "        long total=0;\n"
                "        foreach(var e in edges) if(Union(e[0],e[1])) total+=e[2];\n"
                "        Console.WriteLine(total);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={"python": "import sys\nd=sys.stdin.read().split();i=0\nn,m=int(d[i]),int(d[i+1]);i+=2\nedges=[]\nfor _ in range(m):\n    edges.append((int(d[i+2]),int(d[i]),int(d[i+1])));i+=3\nedges.sort()\npar=list(range(n+1));rnk=[0]*(n+1)\ndef find(x):\n    if par[x]!=x: par[x]=find(par[x])\n    return par[x]\ndef union(x,y):\n    px,py=find(x),find(y)\n    if px==py: return False\n    if rnk[px]<rnk[py]: px,py=py,px\n    par[py]=px\n    if rnk[px]==rnk[py]: rnk[px]+=1\n    return True\ntotal=0\nfor w,u,v in edges:\n    if union(u,v): total+=w\nprint(total)\n"},
        supported_languages=LANGS, time_limit_ms=5000, memory_limit_mb=256, points=30,
    )
    _cases(db, ex, [
        ("basic",   "4 5\n1 2 1\n1 3 4\n2 3 2\n2 4 5\n3 4 3\n", "6",  False, 1),
        ("six-v",   "6 8\n1 3 1\n3 4 2\n1 2 3\n2 5 4\n2 4 5\n3 5 6\n4 6 7\n5 6 8\n", "17", False, 1),
        ("five-v",  "5 7\n1 2 2\n1 3 3\n2 3 1\n2 4 4\n3 4 5\n3 5 6\n4 5 7\n", "13", True, 2),
        ("linear",  "3 2\n1 2 5\n2 3 3\n", "8", True, 1),
    ])


# ════════════════════════════════════════════════════════════════
#  Main
# ════════════════════════════════════════════════════════════════

def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        course = db.scalar(select(Course).where(Course.slug == "intro-to-algorithms"))
        if not course:
            print("ERROR: run intro_algorithms_seed.py first.")
            return

        seed_module9(db, course)
        seed_module10(db, course)
        seed_module11(db, course)
        seed_module12(db, course)

        db.commit()
        print("✓ Modules 9–12 seeded (Graph Traversal, Shortest Paths, DP, Greedy/MST)")
        print("  All 12 modules complete!")


if __name__ == "__main__":
    seed()
