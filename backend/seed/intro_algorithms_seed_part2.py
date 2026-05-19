"""
Seed part 2: modules 5–8 (Hash Tables, Binary Trees/BSTs, Balanced BSTs, Heaps).
Run from backend/ directory after part 1:
    python seed/intro_algorithms_seed_part2.py
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import (
    Base, Course, Difficulty, Exercise, Lesson, LessonType,
    Module, Subject, Tag, TestCase,
)

LANGS = ["python", "javascript", "typescript", "java", "csharp"]


def _subject(db, slug, **kw):
    obj = db.scalar(select(Subject).where(Subject.slug == slug))
    if not obj:
        obj = Subject(slug=slug, **kw); db.add(obj); db.flush()
    return obj

def _course(db, subject, slug, **kw):
    obj = db.scalar(select(Course).where(Course.slug == slug))
    if not obj:
        obj = Course(subject_id=subject.id, slug=slug, **kw); db.add(obj); db.flush()
    return obj

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
#  MODULE 5 — Hash Tables
# ════════════════════════════════════════════════════════════════

M5_HASH_MD = """\
# Hash Tables

A **hash table** maps keys to values in expected **O(1)** time.

## Core idea
A **hash function** h(k) maps a key k to a slot index in [0, m−1].
Two keys that map to the same slot cause a **collision**.

## Collision resolution

### Chaining (separate chaining)
Each slot holds a linked list.  Insert/search walk the list at h(k).
Expected list length = load factor α = n/m.
Expected search time = O(1 + α).  Rehash when α > threshold (≈ 0.75).

### Open addressing (linear probing)
Store all elements in the table itself.  On collision, probe next slots:
h(k, i) = (h(k) + i) mod m.
*Primary clustering* degrades performance as α → 1.

## Universal hashing
Choose h randomly from a family to prevent adversarial worst cases.
Python uses randomised hash seeds since 3.3.

## Load factor and rehashing
When n/m exceeds threshold, allocate a new table (double size) and
re-insert every element.  Amortised cost: O(n) per rehash, spread over Θ(n) inserts.

## Python dict internals
- Open addressing with custom probing sequence
- Preserves insertion order (since Python 3.7)
- Resizes at load factor ≈ 2/3

## When to use hash tables vs BSTs
| Need | Use |
|------|-----|
| O(1) avg lookup / insert / delete | Hash table |
| Sorted iteration or range queries | Balanced BST |
| Worst-case O(log n) guarantee | Balanced BST |
"""

M5_EXERCISE_MD = "Apply hash tables to solve lookup, uniqueness, and subarray-sum problems."


def seed_module5(db: Session, course: Course) -> None:
    mod = _module(db, course, "Hash Tables", 5,
                  "Hash functions, collision resolution, and O(1) lookup applications.")

    _lesson(db, mod, "hash-functions-and-collisions",
            title="Hash Functions and Collision Resolution",
            lesson_type=LessonType.reading,
            content_md=M5_HASH_MD,
            duration_minutes=18,
            order_index=1)

    ex_lesson = _lesson(db, mod, "hash-table-exercises",
                        title="Hash Tables — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M5_EXERCISE_MD,
                        duration_minutes=30,
                        order_index=2)

    # ── Exercise 5.1: Two Sum ─────────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "two-sum",
        title="Two Sum",
        prompt_md=(
            "# Two Sum\n\n"
            "Given **n** integers and a **target**, find two distinct indices i < j "
            "such that a[i] + a[j] = target.\n\n"
            "Print `i j` (0-based).  If no such pair exists print `-1 -1`.\n"
            "If multiple pairs exist, print the one with the **smallest i** "
            "(break ties by smallest j).\n\n"
            "**Input:**\n```\nn\na₁ … aₙ\ntarget\n```\n\n"
            "**Example**\n```\nInput:\n4\n2 7 11 15\n9\n\nOutput:\n0 1\n```\n\n"
            "*Hint: use a hash map — O(n).*"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def two_sum(a, target):\n"
                "    seen = {}  # value -> index\n"
                "    for i, x in enumerate(a):\n"
                "        complement = target - x\n"
                "        # TODO: check if complement is in seen\n"
                "        seen[x] = i\n"
                "    return -1, -1\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n"
                "target = int(data[n+1])\n"
                "i, j = two_sum(a, target)\n"
                "print(i, j)\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1),t=d[n+1];\n\n"
                "function twoSum(a,t){\n"
                "    const seen=new Map();\n"
                "    for(let i=0;i<a.length;i++){\n"
                "        const c=t-a[i];\n"
                "        if(seen.has(c)) return [seen.get(c),i];\n"
                "        if(!seen.has(a[i])) seen.set(a[i],i);\n"
                "    }\n"
                "    return [-1,-1];\n"
                "}\n\n"
                "console.log(twoSum(a,t).join(' '));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1),t=d[n+1];\n\n"
                "function twoSum(a:number[],t:number):[number,number]{\n"
                "    const seen=new Map<number,number>();\n"
                "    for(let i=0;i<a.length;i++){\n"
                "        const c=t-a[i];\n"
                "        if(seen.has(c)) return [seen.get(c)!,i];\n"
                "        if(!seen.has(a[i])) seen.set(a[i],i);\n"
                "    }\n"
                "    return [-1,-1];\n"
                "}\n\n"
                "console.log(twoSum(a,t).join(' '));\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();\n"
                "        int[] a=new int[n];\n"
                "        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
                "        int t=sc.nextInt();\n"
                "        Map<Integer,Integer> seen=new HashMap<>();\n"
                "        int ri=-1,rj=-1;\n"
                "        for(int i=0;i<n;i++){\n"
                "            int c=t-a[i];\n"
                "            if(seen.containsKey(c)){ri=seen.get(c);rj=i;break;}\n"
                "            seen.putIfAbsent(a[i],i);\n"
                "        }\n"
                "        System.out.println(ri+\" \"+rj);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var a=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        int t=int.Parse(Console.ReadLine().Trim());\n"
                "        var seen=new Dictionary<int,int>();\n"
                "        int ri=-1,rj=-1;\n"
                "        for(int i=0;i<n;i++){\n"
                "            int c=t-a[i];\n"
                "            if(seen.TryGetValue(c,out int prev)){ri=prev;rj=i;break;}\n"
                "            if(!seen.ContainsKey(a[i])) seen[a[i]]=i;\n"
                "        }\n"
                "        Console.WriteLine(ri+\" \"+rj);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "d=sys.stdin.read().split();n=int(d[0]);a=list(map(int,d[1:n+1]));t=int(d[n+1])\n"
                "seen={};ri=rj=-1\n"
                "for i,x in enumerate(a):\n"
                "    c=t-x\n"
                "    if c in seen: ri=seen[c];rj=i;break\n"
                "    if x not in seen: seen[x]=i\n"
                "print(ri,rj)\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=3000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, ex, [
        ("found-start", "4\n2 7 11 15\n9\n",  "0 1",   False, 1),
        ("found-mid",   "4\n3 2 4 6\n6\n",    "1 2",   False, 1),
        ("same-value",  "3\n3 3 3\n6\n",      "0 1",   False, 1),
        ("not-found",   "3\n1 2 3\n7\n",      "-1 -1", False, 1),
        ("negatives",   "4\n-3 4 3 90\n1\n",  "0 2",   True,  2),
        ("large-target","3\n1000 2000 3000\n5000\n", "1 2", True, 2),
    ])

    # ── Exercise 5.2: First Non-Repeating Character ───────────────
    ex, _ = _exercise(db, ex_lesson, "first-non-repeating-char",
        title="First Non-Repeating Character",
        prompt_md=(
            "# First Non-Repeating Character\n\n"
            "Given a string of lowercase letters, print the **first character** "
            "that appears **exactly once**.  If all characters repeat, print `-1`.\n\n"
            "**Input:** one line — the string (1 ≤ length ≤ 10 000)\n\n"
            "**Output:** the character or `-1`\n\n"
            "**Examples**\n```\nInput: leetcode  → Output: l\n"
            "Input: aabb      → Output: -1\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n"
                "from collections import Counter\n\n"
                "s = sys.stdin.read().strip()\n"
                "count = Counter(s)\n"
                "# TODO: find the first character with count == 1\n"
                "print(-1)\n"
            ),
            "javascript": (
                "const s=require('fs').readFileSync(0,'utf8').trim();\n"
                "const cnt={};\n"
                "for(const c of s) cnt[c]=(cnt[c]||0)+1;\n"
                "const ans=[...s].find(c=>cnt[c]===1);\n"
                "console.log(ans??'-1');\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const s=fs.readFileSync(0,'utf8').trim();\n"
                "const cnt:Record<string,number>={};\n"
                "for(const c of s) cnt[c]=(cnt[c]||0)+1;\n"
                "const ans=[...s].find(c=>cnt[c]===1);\n"
                "console.log(ans??'-1');\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        String s=sc.nextLine().trim();\n"
                "        Map<Character,Integer> cnt=new LinkedHashMap<>();\n"
                "        for(char c:s.toCharArray()) cnt.merge(c,1,Integer::sum);\n"
                "        char ans=0;\n"
                "        for(char c:s.toCharArray()) if(cnt.get(c)==1){ans=c;break;}\n"
                "        System.out.println(ans==0?\"-1\":String.valueOf(ans));\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var s=Console.ReadLine()?.Trim()??\"\";\n"
                "        var cnt=new Dictionary<char,int>();\n"
                "        foreach(var c in s){cnt.TryGetValue(c,out int v);cnt[c]=v+1;}\n"
                "        char? ans=null;\n"
                "        foreach(var c in s) if(cnt[c]==1){ans=c;break;}\n"
                "        Console.WriteLine(ans.HasValue?ans.Value.ToString():\"-1\");\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys;from collections import Counter\n"
                "s=sys.stdin.read().strip();cnt=Counter(s)\n"
                "print(next((c for c in s if cnt[c]==1),-1))\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=3000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, ex, [
        ("has-unique",    "leetcode", "l",  False, 1),
        ("all-repeat",    "aabb",     "-1", False, 1),
        ("all-repeat-2",  "abcabc",   "-1", False, 1),
        ("first-unique",  "abcd",     "a",  False, 1),
        ("mid-unique",    "aab",      "b",  True,  2),
        ("single-char",   "z",        "z",  True,  1),
    ])

    # ── Exercise 5.3: Subarray Sum Equals K ──────────────────────
    ex, _ = _exercise(db, ex_lesson, "subarray-sum-equals-k",
        title="Subarray Sum Equals K",
        prompt_md=(
            "# Subarray Sum Equals K\n\n"
            "Count the number of **contiguous subarrays** whose elements sum to **k**.\n\n"
            "**Input:**\n```\nn\na₁ … aₙ  (may include negatives)\nk\n```\n\n"
            "**Output:** count of subarrays\n\n"
            "**Example**\n```\nInput:\n5\n1 1 1 1 1\n2\n\nOutput:\n4\n```\n\n"
            "*Hint: prefix-sum + hash map — O(n).  Count how many previous prefix "
            "sums equal current_sum − k.*"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n"
                "from collections import defaultdict\n\n"
                "def count_subarrays(a, k):\n"
                "    prefix_count = defaultdict(int)\n"
                "    prefix_count[0] = 1\n"
                "    total = current_sum = 0\n"
                "    for x in a:\n"
                "        current_sum += x\n"
                "        # TODO: add prefix_count[current_sum - k] to total\n"
                "        prefix_count[current_sum] += 1\n"
                "    return total\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n"
                "k = int(data[n+1])\n"
                "print(count_subarrays(a, k))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1),k=d[n+1];\n"
                "const cnt=new Map([[0,1]]);\n"
                "let total=0,sum=0;\n"
                "for(const x of a){\n"
                "    sum+=x;\n"
                "    total+=(cnt.get(sum-k)||0);\n"
                "    cnt.set(sum,(cnt.get(sum)||0)+1);\n"
                "}\n"
                "console.log(total);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1),k=d[n+1];\n"
                "const cnt=new Map<number,number>([[0,1]]);\n"
                "let total=0,sum=0;\n"
                "for(const x of a){\n"
                "    sum+=x;\n"
                "    total+=(cnt.get(sum-k)||0);\n"
                "    cnt.set(sum,(cnt.get(sum)||0)+1);\n"
                "}\n"
                "console.log(total);\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();\n"
                "        int[] a=new int[n];\n"
                "        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
                "        int k=sc.nextInt();\n"
                "        Map<Integer,Integer> cnt=new HashMap<>();cnt.put(0,1);\n"
                "        long total=0;int sum=0;\n"
                "        for(int x:a){\n"
                "            sum+=x;\n"
                "            total+=cnt.getOrDefault(sum-k,0);\n"
                "            cnt.merge(sum,1,Integer::sum);\n"
                "        }\n"
                "        System.out.println(total);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var a=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        int k=int.Parse(Console.ReadLine().Trim());\n"
                "        var cnt=new Dictionary<int,int>{{0,1}};\n"
                "        long total=0;int sum=0;\n"
                "        foreach(var x in a){\n"
                "            sum+=x;\n"
                "            cnt.TryGetValue(sum-k,out int prev);\n"
                "            total+=prev;\n"
                "            cnt.TryGetValue(sum,out int cur);\n"
                "            cnt[sum]=cur+1;\n"
                "        }\n"
                "        Console.WriteLine(total);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys;from collections import defaultdict\n"
                "d=sys.stdin.read().split();n=int(d[0]);a=list(map(int,d[1:n+1]));k=int(d[n+1])\n"
                "cnt=defaultdict(int);cnt[0]=1;total=s=0\n"
                "for x in a:\n"
                "    s+=x;total+=cnt[s-k];cnt[s]+=1\n"
                "print(total)\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=3000,
        memory_limit_mb=128,
        points=25,
    )
    _cases(db, ex, [
        ("basic",    "5\n1 1 1 1 1\n2\n",      "4",  False, 1),
        ("negatives","5\n1 2 3 -3 -2\n0\n",    "2",  False, 1),
        ("target-7", "4\n3 4 7 2\n7\n",        "2",  False, 1),
        ("none",     "3\n1 2 3\n10\n",          "0",  False, 1),
        ("k-zero",   "4\n1 -1 1 -1\n0\n",      "4",  True,  2),
        ("single",   "1\n5\n5\n",              "1",  True,  1),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 6 — Binary Trees and BSTs
# ════════════════════════════════════════════════════════════════

M6_TREES_MD = """\
# Binary Trees and Traversals

A **binary tree** is a rooted tree where each node has at most two children
(left and right).

## Terminology
- **Root**: node with no parent
- **Leaf**: node with no children
- **Height**: longest path (edges) from root to any leaf
- **Depth**: edges from root to a specific node
- **Balanced**: height = O(log n)

## Traversals (all O(n))

| Traversal | Order | Use |
|-----------|-------|-----|
| Inorder | left → root → right | Sorted output in BST |
| Preorder | root → left → right | Copy / serialise tree |
| Postorder | left → right → root | Delete tree, evaluate expr |
| Level-order (BFS) | level by level | Print levels, check balance |

## Binary Search Tree (BST) Property
For every node v:
- All keys in left subtree < v.key
- All keys in right subtree > v.key

This guarantees **inorder traversal yields sorted output**.

## BST Operations (height h, usually O(log n) if balanced)

| Operation | Time |
|-----------|------|
| Search | O(h) |
| Insert | O(h) |
| Delete | O(h) |
| Min / Max | O(h) |
| Successor / Predecessor | O(h) |

## BST Delete (3 cases)
1. **Node is a leaf** — remove directly.
2. **Node has one child** — replace node with its child.
3. **Node has two children** — replace with **inorder successor** (minimum of right subtree), then delete the successor.
"""

M6_EXERCISE_MD = "Build BSTs from scratch: insertions, inorder traversal, search, kth smallest."


def seed_module6(db: Session, course: Course) -> None:
    mod = _module(db, course, "Binary Trees and Binary Search Trees", 6,
                  "Tree traversals, BST properties, and BST operations.")

    _lesson(db, mod, "binary-trees-traversals",
            title="Binary Trees and Traversals",
            lesson_type=LessonType.reading,
            content_md=M6_TREES_MD,
            duration_minutes=18,
            order_index=1)

    ex_lesson = _lesson(db, mod, "bst-exercises",
                        title="BSTs — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M6_EXERCISE_MD,
                        duration_minutes=35,
                        order_index=2)

    # ── Exercise 6.1: BST Inorder Traversal ──────────────────────
    ex, _ = _exercise(db, ex_lesson, "bst-inorder-traversal",
        title="BST Inorder Traversal",
        prompt_md=(
            "# BST Inorder Traversal\n\n"
            "Insert **n** distinct integers into a Binary Search Tree (BST) "
            "in the given order, then print the **inorder traversal** "
            "(ascending sorted order).\n\n"
            "**Input:**\n```\nn\nv₁ v₂ … vₙ\n```\n\n"
            "**Output:** space-separated inorder sequence\n\n"
            "**Example**\n```\nInput:\n7\n50 30 70 20 40 60 80\n\nOutput:\n20 30 40 50 60 70 80\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "class Node:\n"
                "    def __init__(self, val):\n"
                "        self.val = val\n"
                "        self.left = self.right = None\n\n"
                "def insert(root, val):\n"
                "    if root is None:\n"
                "        return Node(val)\n"
                "    # TODO: recurse left or right\n"
                "    return root\n\n"
                "def inorder(root, result):\n"
                "    if root is None:\n"
                "        return\n"
                "    # TODO: left, visit, right\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "root = None\n"
                "for v in map(int, data[1:n+1]):\n"
                "    root = insert(root, v)\n"
                "result = []\n"
                "inorder(root, result)\n"
                "print(*result)\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0];\n"
                "class Node{constructor(v){this.v=v;this.l=this.r=null;}}\n"
                "function insert(root,v){\n"
                "    if(!root) return new Node(v);\n"
                "    if(v<root.v) root.l=insert(root.l,v);\n"
                "    else root.r=insert(root.r,v);\n"
                "    return root;\n"
                "}\n"
                "function inorder(root,res){\n"
                "    if(!root) return;\n"
                "    inorder(root.l,res);res.push(root.v);inorder(root.r,res);\n"
                "}\n"
                "let root=null;\n"
                "for(let i=1;i<=n;i++) root=insert(root,d[i]);\n"
                "const res=[];inorder(root,res);\n"
                "console.log(res.join(' '));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0];\n"
                "class Node{constructor(public v:number,public l:Node|null=null,public r:Node|null=null){}}\n"
                "function insert(root:Node|null,v:number):Node{\n"
                "    if(!root) return new Node(v);\n"
                "    if(v<root.v) root.l=insert(root.l,v);\n"
                "    else root.r=insert(root.r,v);\n"
                "    return root;\n"
                "}\n"
                "function inorder(root:Node|null,res:number[]):void{\n"
                "    if(!root) return;\n"
                "    inorder(root.l,res);res.push(root.v);inorder(root.r,res);\n"
                "}\n"
                "let root:Node|null=null;\n"
                "for(let i=1;i<=n;i++) root=insert(root,d[i]);\n"
                "const res:number[]=[];inorder(root,res);\n"
                "console.log(res.join(' '));\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    static int[] left,right,val;\n"
                "    static int sz=0;\n"
                "    static int newNode(int v){val[sz]=v;left[sz]=right[sz]=-1;return sz++;}\n"
                "    static int insert(int root,int v){\n"
                "        if(root==-1) return newNode(v);\n"
                "        if(v<val[root]) left[root]=insert(left[root],v);\n"
                "        else right[root]=insert(right[root],v);\n"
                "        return root;\n"
                "    }\n"
                "    static StringBuilder sb=new StringBuilder();\n"
                "    static void inorder(int root){\n"
                "        if(root==-1) return;\n"
                "        inorder(left[root]);\n"
                "        if(sb.length()>0) sb.append(' ');\n"
                "        sb.append(val[root]);\n"
                "        inorder(right[root]);\n"
                "    }\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();\n"
                "        val=new int[n];left=new int[n];right=new int[n];\n"
                "        int root=-1;\n"
                "        for(int i=0;i<n;i++) root=insert(root,sc.nextInt());\n"
                "        inorder(root);\n"
                "        System.out.println(sb);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    class Node{public int V;public Node L,R;}\n"
                "    static Node Insert(Node r,int v){\n"
                "        if(r==null) return new Node{V=v};\n"
                "        if(v<r.V) r.L=Insert(r.L,v);\n"
                "        else r.R=Insert(r.R,v);\n"
                "        return r;\n"
                "    }\n"
                "    static void Inorder(Node r,List<int> res){\n"
                "        if(r==null) return;\n"
                "        Inorder(r.L,res);res.Add(r.V);Inorder(r.R,res);\n"
                "    }\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var vals=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        Node root=null;\n"
                "        foreach(var v in vals) root=Insert(root,v);\n"
                "        var res=new List<int>();Inorder(root,res);\n"
                "        Console.WriteLine(string.Join(' ',res));\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "class N:\n"
                "    def __init__(self,v): self.v=v;self.l=self.r=None\n"
                "def ins(r,v):\n"
                "    if not r: return N(v)\n"
                "    if v<r.v: r.l=ins(r.l,v)\n"
                "    else: r.r=ins(r.r,v)\n"
                "    return r\n"
                "def io(r,res):\n"
                "    if not r: return\n"
                "    io(r.l,res);res.append(r.v);io(r.r,res)\n"
                "d=sys.stdin.read().split();n=int(d[0])\n"
                "root=None\n"
                "for v in map(int,d[1:n+1]): root=ins(root,v)\n"
                "res=[];io(root,res);print(*res)\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=15,
    )
    _cases(db, ex, [
        ("balanced",  "7\n50 30 70 20 40 60 80\n", "20 30 40 50 60 70 80", False, 1),
        ("linear",    "5\n1 2 3 4 5\n",             "1 2 3 4 5",           False, 1),
        ("single",    "1\n42\n",                     "42",                  False, 1),
        ("reverse",   "5\n5 4 3 2 1\n",             "1 2 3 4 5",           True,  2),
        ("mixed",     "5\n5 3 7 1 4\n",             "1 3 4 5 7",           True,  2),
    ])

    # ── Exercise 6.2: BST Search ──────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "bst-search",
        title="BST Search",
        prompt_md=(
            "# BST Search\n\n"
            "Insert **n** distinct integers into a BST in the given order, "
            "then answer **q** search queries.\n\n"
            "**Input:**\n```\nn\nv₁ … vₙ\nq\nq₁ q₂ … qₙ (one per line or space-sep)\n```\n\n"
            "**Output:** for each query: `YES` if found, `NO` otherwise\n\n"
            "**Example**\n```\nInput:\n7\n50 30 70 20 40 60 80\n3\n40\n55\n80\n\n"
            "Output:\nYES\nNO\nYES\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "class Node:\n"
                "    def __init__(self,v): self.v=v;self.l=self.r=None\n\n"
                "def insert(root, v):\n"
                "    if not root: return Node(v)\n"
                "    if v < root.v: root.l = insert(root.l, v)\n"
                "    else: root.r = insert(root.r, v)\n"
                "    return root\n\n"
                "def search(root, q):\n"
                "    # TODO: traverse left/right based on comparison\n"
                "    return False\n\n"
                "lines = sys.stdin.read().split()\n"
                "idx = 0\n"
                "n = int(lines[idx]); idx += 1\n"
                "root = None\n"
                "for _ in range(n):\n"
                "    root = insert(root, int(lines[idx])); idx += 1\n"
                "q = int(lines[idx]); idx += 1\n"
                "for _ in range(q):\n"
                "    print('YES' if search(root, int(lines[idx])) else 'NO'); idx += 1\n"
            ),
            "javascript": (
                "const lines=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/);\n"
                "let li=0;\n"
                "class N{constructor(v){this.v=v;this.l=this.r=null;}}\n"
                "function ins(r,v){if(!r)return new N(v);if(v<r.v)r.l=ins(r.l,v);else r.r=ins(r.r,v);return r;}\n"
                "function find(r,q){while(r){if(q===r.v)return true;r=q<r.v?r.l:r.r;}return false;}\n"
                "const n=+lines[li++];let root=null;\n"
                "for(let i=0;i<n;i++) root=ins(root,+lines[li++]);\n"
                "const q=+lines[li++];\n"
                "for(let i=0;i<q;i++) console.log(find(root,+lines[li++])?'YES':'NO');\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const lines=fs.readFileSync(0,'utf8').trim().split(/\\s+/);\n"
                "let li=0;\n"
                "class N{constructor(public v:number,public l:N|null=null,public r:N|null=null){}}\n"
                "function ins(r:N|null,v:number):N{if(!r)return new N(v);if(v<r.v)r.l=ins(r.l,v);else r.r=ins(r.r,v);return r;}\n"
                "function find(r:N|null,q:number):boolean{while(r){if(q===r.v)return true;r=q<r.v?r.l:r.r;}return false;}\n"
                "const n=+lines[li++];let root:N|null=null;\n"
                "for(let i=0;i<n;i++) root=ins(root,+lines[li++]);\n"
                "const q=+lines[li++];\n"
                "for(let i=0;i<q;i++) console.log(find(root,+lines[li++])?'YES':'NO');\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    static int[] lc,rc,val;static int sz=0;\n"
                "    static int ins(int r,int v){\n"
                "        if(r==-1){val[sz]=v;lc[sz]=rc[sz]=-1;return sz++;}\n"
                "        if(v<val[r])lc[r]=ins(lc[r],v);else rc[r]=ins(rc[r],v);return r;\n"
                "    }\n"
                "    static boolean find(int r,int q){\n"
                "        while(r!=-1){if(q==val[r])return true;r=q<val[r]?lc[r]:rc[r];}return false;\n"
                "    }\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();\n"
                "        val=new int[n+1];lc=new int[n+1];rc=new int[n+1];\n"
                "        int root=-1;\n"
                "        for(int i=0;i<n;i++) root=ins(root,sc.nextInt());\n"
                "        int q=sc.nextInt();\n"
                "        for(int i=0;i<q;i++) System.out.println(find(root,sc.nextInt())?\"YES\":\"NO\");\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    class N{public int V;public N L,R;}\n"
                "    static N Ins(N r,int v){if(r==null)return new N{V=v};if(v<r.V)r.L=Ins(r.L,v);else r.R=Ins(r.R,v);return r;}\n"
                "    static bool Find(N r,int q){while(r!=null){if(q==r.V)return true;r=q<r.V?r.L:r.R;}return false;}\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var vs=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        N root=null;foreach(var v in vs) root=Ins(root,v);\n"
                "        int q=int.Parse(Console.ReadLine().Trim());\n"
                "        for(int i=0;i<q;i++) Console.WriteLine(Find(root,int.Parse(Console.ReadLine().Trim()))?\"YES\":\"NO\");\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "class N:\n"
                "    def __init__(self,v): self.v=v;self.l=self.r=None\n"
                "def ins(r,v):\n"
                "    if not r: return N(v)\n"
                "    if v<r.v: r.l=ins(r.l,v)\n"
                "    else: r.r=ins(r.r,v)\n"
                "    return r\n"
                "def find(r,q):\n"
                "    while r:\n"
                "        if q==r.v: return True\n"
                "        r=r.l if q<r.v else r.r\n"
                "    return False\n"
                "tok=sys.stdin.read().split();i=0\n"
                "n=int(tok[i]);i+=1;root=None\n"
                "for _ in range(n): root=ins(root,int(tok[i]));i+=1\n"
                "q=int(tok[i]);i+=1\n"
                "for _ in range(q): print('YES' if find(root,int(tok[i])) else 'NO');i+=1\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=15,
    )
    _cases(db, ex, [
        ("basic", "7\n50 30 70 20 40 60 80\n3\n40\n55\n80\n", "YES\nNO\nYES", False, 1),
        ("miss",  "5\n1 2 3 4 5\n2\n6\n0\n",                   "NO\nNO",      False, 1),
        ("root",  "3\n10 5 15\n1\n10\n",                        "YES",         True,  2),
    ])

    # ── Exercise 6.3: Kth Smallest in BST ────────────────────────
    ex, _ = _exercise(db, ex_lesson, "kth-smallest-bst",
        title="Kth Smallest in BST",
        prompt_md=(
            "# Kth Smallest in BST\n\n"
            "Insert **n** distinct integers into a BST, then find the **kth smallest** "
            "element (1-indexed).\n\n"
            "**Input:**\n```\nn k\nv₁ v₂ … vₙ\n```\n\n"
            "**Output:** the kth smallest element\n\n"
            "**Example**\n```\nInput:\n7 3\n50 30 70 20 40 60 80\n\nOutput:\n40\n```\n\n"
            "*Hint: inorder traversal visits nodes in sorted order.*"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "class Node:\n"
                "    def __init__(self,v): self.v=v;self.l=self.r=None\n\n"
                "def insert(root,v):\n"
                "    if not root: return Node(v)\n"
                "    if v<root.v: root.l=insert(root.l,v)\n"
                "    else: root.r=insert(root.r,v)\n"
                "    return root\n\n"
                "def kth_smallest(root, k):\n"
                "    # TODO: iterative or recursive inorder, stop at kth\n"
                "    pass\n\n"
                "data = sys.stdin.read().split()\n"
                "n, k = int(data[0]), int(data[1])\n"
                "root = None\n"
                "for v in map(int, data[2:n+2]):\n"
                "    root = insert(root, v)\n"
                "print(kth_smallest(root, k))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],k=d[1];\n"
                "class N{constructor(v){this.v=v;this.l=this.r=null;}}\n"
                "function ins(r,v){if(!r)return new N(v);if(v<r.v)r.l=ins(r.l,v);else r.r=ins(r.r,v);return r;}\n"
                "let root=null;\n"
                "for(let i=2;i<n+2;i++) root=ins(root,d[i]);\n"
                "// Iterative inorder to find kth\n"
                "let cnt=0,ans=0,cur=root;\n"
                "const st=[];\n"
                "while(cur||st.length){\n"
                "    while(cur){st.push(cur);cur=cur.l;}\n"
                "    cur=st.pop();cnt++;\n"
                "    if(cnt===k){ans=cur.v;break;}\n"
                "    cur=cur.r;\n"
                "}\n"
                "console.log(ans);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],k=d[1];\n"
                "class N{constructor(public v:number,public l:N|null=null,public r:N|null=null){}}\n"
                "function ins(r:N|null,v:number):N{if(!r)return new N(v);if(v<r.v)r.l=ins(r.l,v);else r.r=ins(r.r,v);return r;}\n"
                "let root:N|null=null;\n"
                "for(let i=2;i<n+2;i++) root=ins(root,d[i]);\n"
                "let cnt=0,ans=0,cur:N|null=root;\n"
                "const st:N[]=[];\n"
                "outer:while(cur||st.length){\n"
                "    while(cur){st.push(cur);cur=cur.l;}\n"
                "    cur=st.pop()!;cnt++;\n"
                "    if(cnt===k){ans=cur.v;break outer;}\n"
                "    cur=cur.r;\n"
                "}\n"
                "console.log(ans);\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    static int[] lc,rc,val;static int sz=0;\n"
                "    static int ins(int r,int v){\n"
                "        if(r==-1){val[sz]=v;lc[sz]=rc[sz]=-1;return sz++;}\n"
                "        if(v<val[r])lc[r]=ins(lc[r],v);else rc[r]=ins(rc[r],v);return r;\n"
                "    }\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),k=sc.nextInt();\n"
                "        val=new int[n+1];lc=new int[n+1];rc=new int[n+1];\n"
                "        int root=-1;\n"
                "        for(int i=0;i<n;i++) root=ins(root,sc.nextInt());\n"
                "        Deque<Integer> st=new ArrayDeque<>();\n"
                "        int cur=root,cnt=0,ans=0;\n"
                "        while(cur!=-1||!st.isEmpty()){\n"
                "            while(cur!=-1){st.push(cur);cur=lc[cur];}\n"
                "            cur=st.pop();cnt++;\n"
                "            if(cnt==k){ans=val[cur];break;}\n"
                "            cur=rc[cur];\n"
                "        }\n"
                "        System.out.println(ans);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    class N{public int V;public N L,R;}\n"
                "    static N Ins(N r,int v){if(r==null)return new N{V=v};if(v<r.V)r.L=Ins(r.L,v);else r.R=Ins(r.R,v);return r;}\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),k=int.Parse(first[1]);\n"
                "        var vs=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        N root=null;foreach(var v in vs) root=Ins(root,v);\n"
                "        var st=new Stack<N>();N cur=root;int cnt=0,ans=0;\n"
                "        while(cur!=null||st.Count>0){\n"
                "            while(cur!=null){st.Push(cur);cur=cur.L;}\n"
                "            cur=st.Pop();cnt++;\n"
                "            if(cnt==k){ans=cur.V;break;}\n"
                "            cur=cur.R;\n"
                "        }\n"
                "        Console.WriteLine(ans);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "class N:\n"
                "    def __init__(self,v): self.v=v;self.l=self.r=None\n"
                "def ins(r,v):\n"
                "    if not r: return N(v)\n"
                "    if v<r.v: r.l=ins(r.l,v)\n"
                "    else: r.r=ins(r.r,v)\n"
                "    return r\n"
                "d=sys.stdin.read().split();n,k=int(d[0]),int(d[1])\n"
                "root=None\n"
                "for v in map(int,d[2:n+2]): root=ins(root,v)\n"
                "st=[];cur=root;cnt=0\n"
                "while cur or st:\n"
                "    while cur: st.append(cur);cur=cur.l\n"
                "    cur=st.pop();cnt+=1\n"
                "    if cnt==k: print(cur.v);break\n"
                "    cur=cur.r\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=20,
    )
    _cases(db, ex, [
        ("mid",   "7 3\n50 30 70 20 40 60 80\n", "40", False, 1),
        ("first", "5 1\n5 3 7 1 4\n",             "1",  False, 1),
        ("last",  "5 5\n5 3 7 1 4\n",             "7",  False, 1),
        ("deep",  "4 2\n10 5 15 3\n",             "5",  True,  2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 7 — Balanced BSTs (AVL & Red-Black Trees)
# ════════════════════════════════════════════════════════════════

M7_AVL_MD = """\
# AVL Trees

An **AVL tree** is a BST where for every node the heights of the two subtrees
differ by at most 1 (balance factor ∈ {−1, 0, +1}).

## Rotations
Rotations restore the AVL property in O(1) after insertion/deletion.

### Left rotation on node x (right subtree heavy)
```
    x                  y
   / \\                / \\
  A   y     →        x   C
     / \\            / \\
    B   C           A   B
```

### Right rotation on node y (left subtree heavy)
```
      y              x
     / \\            / \\
    x   C    →     A   y
   / \\                / \\
  A   B              B   C
```

### Double rotations
- **Left-Right (LR)**: left-rotate child, then right-rotate root.
- **Right-Left (RL)**: right-rotate child, then left-rotate root.

## Complexity
All operations O(log n) — guaranteed by balance condition.
Height ≤ 1.44 log₂(n+2) − 0.328.

# Red-Black Trees

A **Red-Black tree** is a BST where every node is coloured red or black,
satisfying:
1. Root is **black**.
2. Leaves (NIL sentinels) are **black**.
3. Both children of a **red** node are **black** (no two consecutive reds).
4. All paths from a node to its descendant leaves have the **same number of black nodes** (black-height).

## Why Red-Black Trees?
- Height ≤ 2 log₂(n+1) (looser than AVL).
- **Fewer rotations** on insert/delete (at most 3 vs O(log n) for AVL).
- Used in: Linux kernel, Java `TreeMap`, C++ `std::map`, Python's `sortedcontainers`.

## Comparison

| Property | AVL | Red-Black |
|----------|-----|-----------|
| Height bound | 1.44 log n | 2 log n |
| Lookup speed | Slightly faster | Slightly slower |
| Insert/delete | More rotations | Fewer rotations |
| Best for | Read-heavy | Write-heavy |
"""

M7_EXERCISE_MD = "Analyse BST height and determine if trees satisfy the balance property."


def seed_module7(db: Session, course: Course) -> None:
    mod = _module(db, course, "Balanced Binary Search Trees", 7,
                  "AVL trees, Red-Black trees, rotations, and self-balancing guarantees.")

    _lesson(db, mod, "avl-and-red-black-trees",
            title="AVL Trees and Red-Black Trees",
            lesson_type=LessonType.reading,
            content_md=M7_AVL_MD,
            duration_minutes=22,
            order_index=1)

    ex_lesson = _lesson(db, mod, "balanced-bst-exercises",
                        title="Balanced BSTs — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M7_EXERCISE_MD,
                        duration_minutes=25,
                        order_index=2)

    # ── Exercise 7.1: BST Height ──────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "bst-height",
        title="BST Height",
        prompt_md=(
            "# BST Height\n\n"
            "Insert **n** distinct integers into a BST in the given order.\n"
            "Compute the **height** of the resulting tree — defined as the number "
            "of edges on the longest root-to-leaf path.  An empty tree has height −1; "
            "a single-node tree has height 0.\n\n"
            "**Input:**\n```\nn\nv₁ v₂ … vₙ\n```\n\n"
            "**Output:** height\n\n"
            "**Example**\n```\nInput:\n7\n50 30 70 20 40 60 80\n\nOutput:\n2\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "class Node:\n"
                "    def __init__(self,v): self.v=v;self.l=self.r=None\n\n"
                "def insert(root,v):\n"
                "    if not root: return Node(v)\n"
                "    if v<root.v: root.l=insert(root.l,v)\n"
                "    else: root.r=insert(root.r,v)\n"
                "    return root\n\n"
                "def height(root):\n"
                "    if root is None:\n"
                "        return -1\n"
                "    # TODO: 1 + max(height(left), height(right))\n"
                "    return 0\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "root = None\n"
                "for v in map(int, data[1:n+1]):\n"
                "    root = insert(root, v)\n"
                "print(height(root))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0];\n"
                "class N{constructor(v){this.v=v;this.l=this.r=null;}}\n"
                "function ins(r,v){if(!r)return new N(v);if(v<r.v)r.l=ins(r.l,v);else r.r=ins(r.r,v);return r;}\n"
                "function h(r){if(!r)return -1;return 1+Math.max(h(r.l),h(r.r));}\n"
                "let root=null;\n"
                "for(let i=1;i<=n;i++) root=ins(root,d[i]);\n"
                "console.log(h(root));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0];\n"
                "class N{constructor(public v:number,public l:N|null=null,public r:N|null=null){}}\n"
                "function ins(r:N|null,v:number):N{if(!r)return new N(v);if(v<r.v)r.l=ins(r.l,v);else r.r=ins(r.r,v);return r;}\n"
                "function h(r:N|null):number{if(!r)return -1;return 1+Math.max(h(r.l),h(r.r));}\n"
                "let root:N|null=null;\n"
                "for(let i=1;i<=n;i++) root=ins(root,d[i]);\n"
                "console.log(h(root));\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    static int[] lc,rc,val;static int sz=0;\n"
                "    static int ins(int r,int v){\n"
                "        if(r==-1){val[sz]=v;lc[sz]=rc[sz]=-1;return sz++;}\n"
                "        if(v<val[r])lc[r]=ins(lc[r],v);else rc[r]=ins(rc[r],v);return r;\n"
                "    }\n"
                "    static int h(int r){if(r==-1)return -1;return 1+Math.max(h(lc[r]),h(rc[r]));}\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();\n"
                "        val=new int[n+1];lc=new int[n+1];rc=new int[n+1];\n"
                "        int root=-1;\n"
                "        for(int i=0;i<n;i++) root=ins(root,sc.nextInt());\n"
                "        System.out.println(h(root));\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    class N{public int V;public N L,R;}\n"
                "    static N Ins(N r,int v){if(r==null)return new N{V=v};if(v<r.V)r.L=Ins(r.L,v);else r.R=Ins(r.R,v);return r;}\n"
                "    static int H(N r){if(r==null)return -1;return 1+Math.Max(H(r.L),H(r.R));}\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var vs=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        N root=null;foreach(var v in vs) root=Ins(root,v);\n"
                "        Console.WriteLine(H(root));\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "class N:\n"
                "    def __init__(self,v): self.v=v;self.l=self.r=None\n"
                "def ins(r,v):\n"
                "    if not r: return N(v)\n"
                "    if v<r.v: r.l=ins(r.l,v)\n"
                "    else: r.r=ins(r.r,v)\n"
                "    return r\n"
                "def h(r): return -1 if not r else 1+max(h(r.l),h(r.r))\n"
                "d=sys.stdin.read().split();n=int(d[0]);root=None\n"
                "for v in map(int,d[1:n+1]): root=ins(root,v)\n"
                "print(h(root))\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=15,
    )
    _cases(db, ex, [
        ("balanced",  "7\n50 30 70 20 40 60 80\n", "2",  False, 1),
        ("linear",    "5\n1 2 3 4 5\n",             "4",  False, 1),
        ("single",    "1\n42\n",                     "0",  False, 1),
        ("two-level", "4\n10 5 15 3\n",             "2",  True,  2),
        ("root-only", "3\n5 3 7\n",                  "1",  True,  1),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 8 — Binary Heaps and Priority Queues
# ════════════════════════════════════════════════════════════════

M8_HEAP_MD = """\
# Binary Heaps

A **binary heap** is a nearly-complete binary tree satisfying the **heap property**.

- **Max-heap**: parent ≥ both children.  Root = maximum.
- **Min-heap**: parent ≤ both children.  Root = minimum.

## Array representation
Storing the heap in array `a` (1-indexed):
- `parent(i)  = i // 2`
- `left(i)    = 2 * i`
- `right(i)   = 2 * i + 1`

## Core operations

| Operation | Time | Description |
|-----------|------|-------------|
| MAX-HEAPIFY | O(log n) | Restore heap property at node i |
| BUILD-MAX-HEAP | **O(n)** | Heapify from n/2 down to 1 |
| INSERT | O(log n) | Add element, sift up |
| EXTRACT-MAX | O(log n) | Remove root, put last leaf at top, sift down |
| INCREASE-KEY | O(log n) | Increase key, sift up |
| MAXIMUM | O(1) | Peek at root |

## BUILD-MAX-HEAP is O(n) — why?
Nodes near the leaves (the majority) have small height.  Total sift-down work:
∑_{h=0}^{⌊log n⌋} ⌈n / 2^{h+1}⌉ · h ≤ n ∑_{h=0}^{∞} h/2^h = 2n = **O(n)**.

## Heapsort
1. BUILD-MAX-HEAP: O(n)
2. Repeat n−1 times: swap root with last element, shrink heap, HEAPIFY root: O(n log n)
Total: **O(n log n)**, in-place, not stable.

## Priority Queue applications
- Dijkstra's shortest path (min-heap on distance)
- Prim's MST (min-heap on edge weight)
- Huffman coding (min-heap on frequency)
- Task scheduling by priority
- Median maintenance (two heaps: max-heap left + min-heap right)
"""

M8_EXERCISE_MD = "Implement heap sort and solve priority-queue problems."


def seed_module8(db: Session, course: Course) -> None:
    mod = _module(db, course, "Binary Heaps and Priority Queues", 8,
                  "Heap structure, BUILD-HEAP in O(n), heapsort, and priority queue applications.")

    _lesson(db, mod, "binary-heaps",
            title="Binary Heaps",
            lesson_type=LessonType.reading,
            content_md=M8_HEAP_MD,
            duration_minutes=18,
            order_index=1)

    ex_lesson = _lesson(db, mod, "heap-exercises",
                        title="Binary Heaps — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M8_EXERCISE_MD,
                        duration_minutes=35,
                        order_index=2)

    # ── Exercise 8.1: Heap Sort ───────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "heap-sort",
        title="Heap Sort",
        prompt_md=(
            "# Heap Sort\n\n"
            "Sort **n** integers in ascending order using **Heap Sort** "
            "(build a max-heap, then repeatedly extract the max).\n\n"
            "**Input:**\n```\nn\na₁ a₂ … aₙ\n```\n\n"
            "**Output:** sorted integers separated by spaces\n\n"
            "**Example**\n```\nInput:\n8\n16 14 10 8 7 9 3 2\n\nOutput:\n2 3 7 8 9 10 14 16\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def heapify(a, n, i):\n"
                "    largest = i\n"
                "    l, r = 2*i+1, 2*i+2\n"
                "    if l < n and a[l] > a[largest]: largest = l\n"
                "    if r < n and a[r] > a[largest]: largest = r\n"
                "    if largest != i:\n"
                "        a[i], a[largest] = a[largest], a[i]\n"
                "        heapify(a, n, largest)\n\n"
                "def heap_sort(a):\n"
                "    n = len(a)\n"
                "    # Build max-heap\n"
                "    for i in range(n//2 - 1, -1, -1):\n"
                "        heapify(a, n, i)\n"
                "    # TODO: extract elements one by one\n"
                "    return a\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n"
                "print(*heap_sort(a))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1);\n\n"
                "function heapify(a,n,i){\n"
                "    let lg=i,l=2*i+1,r=2*i+2;\n"
                "    if(l<n&&a[l]>a[lg])lg=l;\n"
                "    if(r<n&&a[r]>a[lg])lg=r;\n"
                "    if(lg!==i){[a[i],a[lg]]=[a[lg],a[i]];heapify(a,n,lg);}\n"
                "}\n"
                "for(let i=Math.floor(n/2)-1;i>=0;i--) heapify(a,n,i);\n"
                "for(let i=n-1;i>0;i--){\n"
                "    [a[0],a[i]]=[a[i],a[0]];\n"
                "    heapify(a,i,0);\n"
                "}\n"
                "console.log(a.join(' '));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1);\n\n"
                "function heapify(a:number[],n:number,i:number):void{\n"
                "    let lg=i,l=2*i+1,r=2*i+2;\n"
                "    if(l<n&&a[l]>a[lg])lg=l;\n"
                "    if(r<n&&a[r]>a[lg])lg=r;\n"
                "    if(lg!==i){[a[i],a[lg]]=[a[lg],a[i]];heapify(a,n,lg);}\n"
                "}\n"
                "for(let i=Math.floor(n/2)-1;i>=0;i--) heapify(a,n,i);\n"
                "for(let i=n-1;i>0;i--){\n"
                "    [a[0],a[i]]=[a[i],a[0]];\n"
                "    heapify(a,i,0);\n"
                "}\n"
                "console.log(a.join(' '));\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    static void heapify(int[] a,int n,int i){\n"
                "        int lg=i,l=2*i+1,r=2*i+2;\n"
                "        if(l<n&&a[l]>a[lg])lg=l;\n"
                "        if(r<n&&a[r]>a[lg])lg=r;\n"
                "        if(lg!=i){int t=a[i];a[i]=a[lg];a[lg]=t;heapify(a,n,lg);}\n"
                "    }\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();int[] a=new int[n];\n"
                "        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
                "        for(int i=n/2-1;i>=0;i--) heapify(a,n,i);\n"
                "        for(int i=n-1;i>0;i--){\n"
                "            int t=a[0];a[0]=a[i];a[i]=t;\n"
                "            heapify(a,i,0);\n"
                "        }\n"
                "        StringBuilder sb=new StringBuilder();\n"
                "        for(int i=0;i<n;i++){if(i>0)sb.append(' ');sb.append(a[i]);}\n"
                "        System.out.println(sb);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    static void Heapify(int[] a,int n,int i){\n"
                "        int lg=i,l=2*i+1,r=2*i+2;\n"
                "        if(l<n&&a[l]>a[lg])lg=l;\n"
                "        if(r<n&&a[r]>a[lg])lg=r;\n"
                "        if(lg!=i){(a[i],a[lg])=(a[lg],a[i]);Heapify(a,n,lg);}\n"
                "    }\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var a=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        for(int i=n/2-1;i>=0;i--) Heapify(a,n,i);\n"
                "        for(int i=n-1;i>0;i--){\n"
                "            (a[0],a[i])=(a[i],a[0]);\n"
                "            Heapify(a,i,0);\n"
                "        }\n"
                "        Console.WriteLine(string.Join(' ',a));\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "def hfy(a,n,i):\n"
                "    lg=i;l=2*i+1;r=2*i+2\n"
                "    if l<n and a[l]>a[lg]: lg=l\n"
                "    if r<n and a[r]>a[lg]: lg=r\n"
                "    if lg!=i: a[i],a[lg]=a[lg],a[i];hfy(a,n,lg)\n"
                "d=sys.stdin.read().split();n=int(d[0]);a=list(map(int,d[1:n+1]))\n"
                "for i in range(n//2-1,-1,-1): hfy(a,n,i)\n"
                "for i in range(n-1,0,-1): a[0],a[i]=a[i],a[0];hfy(a,i,0)\n"
                "print(*a)\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=20,
    )
    _cases(db, ex, [
        ("classic",  "8\n16 14 10 8 7 9 3 2\n", "2 3 7 8 9 10 14 16", False, 1),
        ("reverse",  "5\n5 4 3 2 1\n",           "1 2 3 4 5",          False, 1),
        ("dups",     "6\n3 1 4 1 5 9\n",         "1 1 3 4 5 9",         False, 1),
        ("single",   "1\n7\n",                    "7",                   False, 1),
        ("negs",     "4\n-1 -3 -2 0\n",          "-3 -2 -1 0",          True,  2),
    ])

    # ── Exercise 8.2: Kth Largest Element ────────────────────────
    ex, _ = _exercise(db, ex_lesson, "kth-largest-element",
        title="Kth Largest Element",
        prompt_md=(
            "# Kth Largest Element\n\n"
            "Find the **kth largest** element in an unsorted array (1-indexed: "
            "k=1 means the maximum).\n\n"
            "**Input:**\n```\nn k\na₁ a₂ … aₙ\n```\n\n"
            "**Output:** kth largest element\n\n"
            "**Examples**\n```\nInput:\n5 2\n3 2 1 5 6\n\nOutput:\n5\n```\n\n"
            "*Hint: maintain a min-heap of size k — O(n log k).*"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n"
                "import heapq\n\n"
                "data = sys.stdin.read().split()\n"
                "n, k = int(data[0]), int(data[1])\n"
                "a = list(map(int, data[2:n+2]))\n\n"
                "# Maintain a min-heap of size k\n"
                "# The root will be the kth largest\n"
                "heap = []\n"
                "for x in a:\n"
                "    heapq.heappush(heap, x)\n"
                "    if len(heap) > k:\n"
                "        heapq.heappop(heap)  # remove smallest\n\n"
                "print(heap[0])\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],k=d[1],a=d.slice(2,n+2);\n"
                "// Simple O(n log n) approach: sort descending, take index k-1\n"
                "a.sort((x,y)=>y-x);\n"
                "console.log(a[k-1]);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],k=d[1],a=d.slice(2,n+2);\n"
                "a.sort((x,y)=>y-x);\n"
                "console.log(a[k-1]);\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt(),k=sc.nextInt();\n"
                "        PriorityQueue<Integer> pq=new PriorityQueue<>();\n"
                "        for(int i=0;i<n;i++){\n"
                "            pq.offer(sc.nextInt());\n"
                "            if(pq.size()>k) pq.poll();\n"
                "        }\n"
                "        System.out.println(pq.peek());\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\nusing System.Linq;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var first=Console.ReadLine().Trim().Split();\n"
                "        int n=int.Parse(first[0]),k=int.Parse(first[1]);\n"
                "        var a=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        Array.Sort(a,(x,y)=>y-x);\n"
                "        Console.WriteLine(a[k-1]);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys,heapq\n"
                "d=sys.stdin.read().split();n,k=int(d[0]),int(d[1]);a=list(map(int,d[2:n+2]))\n"
                "h=[]\n"
                "for x in a:\n"
                "    heapq.heappush(h,x)\n"
                "    if len(h)>k: heapq.heappop(h)\n"
                "print(h[0])\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=20,
    )
    _cases(db, ex, [
        ("k2",       "5 2\n3 2 1 5 6\n",   "5",  False, 1),
        ("k4",       "6 4\n3 2 3 1 2 4\n", "2",  False, 1),
        ("last",     "3 3\n7 10 4\n",       "4",  False, 1),
        ("first",    "4 1\n1 9 3 5\n",      "9",  True,  2),
        ("all-same", "4 2\n5 5 5 5\n",      "5",  True,  1),
    ])


# ════════════════════════════════════════════════════════════════
#  Main
# ════════════════════════════════════════════════════════════════

def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        algos = db.scalar(select(Subject).where(Subject.slug == "algorithms"))
        if not algos:
            print("ERROR: run intro_algorithms_seed.py first (creates the subject and course).")
            return

        course = db.scalar(select(Course).where(Course.slug == "intro-to-algorithms"))
        if not course:
            print("ERROR: run intro_algorithms_seed.py first.")
            return

        seed_module5(db, course)
        seed_module6(db, course)
        seed_module7(db, course)
        seed_module8(db, course)

        db.commit()
        print("✓ Modules 5–8 seeded (Hash Tables, BSTs, Balanced BSTs, Heaps)")


if __name__ == "__main__":
    seed()
