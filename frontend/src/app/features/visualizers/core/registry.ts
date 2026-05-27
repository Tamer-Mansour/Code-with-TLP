import { Type } from '@angular/core';
import { VizMeta } from './visualizer.base';

export interface VizRegistryEntry {
  meta: VizMeta;
  /** Lazy-loaded component factory for use in viz-page. */
  loadComponent: () => Promise<Type<unknown>>;
}

/** Central registry: slug → entry. Add new modules here. */
export const VIZ_REGISTRY: Record<string, VizRegistryEntry> = {
  'array-sorting': {
    meta: {
      slug: 'array-sorting',
      title: 'Array Sorting & Search',
      category: 'Sorting',
      description: 'Step through Bubble, Selection, and Insertion sort, plus Linear and Binary search — watch comparisons, swaps, and the sorted partition grow in real time.',
      operations: ['Bubble Sort', 'Selection Sort', 'Insertion Sort', 'Linear Search', 'Binary Search'],
      complexity: {
        'Bubble Sort':    { time: 'O(n²)',      space: 'O(1)' },
        'Selection Sort': { time: 'O(n²)',      space: 'O(1)' },
        'Insertion Sort': { time: 'O(n²)',      space: 'O(1)' },
        'Linear Search':  { time: 'O(n)',       space: 'O(1)' },
        'Binary Search':  { time: 'O(log n)',   space: 'O(1)' },
      },
    },
    loadComponent: () =>
      import('../modules/array-sorting/array-sorting.component').then(m => m.ArraySortingComponent),
  },

  'stack-queue': {
    meta: {
      slug: 'stack-queue',
      title: 'Stack & Queue',
      category: 'Linear',
      description: 'Push and pop on a LIFO stack, enqueue and dequeue on a FIFO queue — watch the active element animate in and out.',
      operations: ['Stack Push', 'Stack Pop', 'Queue Enqueue', 'Queue Dequeue'],
    },
    loadComponent: () =>
      import('../modules/stack-queue/stack-queue.component').then(m => m.StackQueueComponent),
  },

  'linked-list': {
    meta: {
      slug: 'linked-list',
      title: 'Linked List',
      category: 'Linear',
      description: 'Insert, delete, search, and reverse a singly linked list with an animated pointer walking node to node.',
      operations: ['Insert at Head', 'Insert at Tail', 'Delete Value', 'Search Value', 'Reverse'],
    },
    loadComponent: () =>
      import('../modules/linked-list/linked-list.component').then(m => m.LinkedListComponent),
  },

  'binary-heap': {
    meta: {
      slug: 'binary-heap',
      title: 'Binary Heap / Priority Queue',
      category: 'Trees',
      description: 'Insert with sift-up, extract-max with sift-down, and build-heap (Floyd) — shown as both a tree and its backing array.',
      operations: ['Insert', 'Extract-Max', 'Build-Heap'],
    },
    loadComponent: () =>
      import('../modules/binary-heap/binary-heap.component').then(m => m.BinaryHeapComponent),
  },

  'hash-table': {
    meta: {
      slug: 'hash-table',
      title: 'Hash Table (Chaining)',
      category: 'Hashing',
      description: 'Insert, search, and delete integer keys in a hash table with separate chaining — watch h(k) = k mod 8 route each key to its bucket.',
      operations: ['Insert', 'Search', 'Delete'],
    },
    loadComponent: () =>
      import('../modules/hash-table/hash-table.component').then(m => m.HashTableComponent),
  },

  'bst': {
    meta: {
      slug: 'bst',
      title: 'Binary Search Tree',
      category: 'Trees',
      description: 'Build a BST by inserting values, search for a key and watch the path highlight, then run In-order, Pre-order, or Post-order traversals.',
      operations: ['Insert', 'Search', 'In-order', 'Pre-order', 'Post-order'],
      complexity: {
        'Insert':    { time: 'O(h)',   space: 'O(1)' },
        'Search':    { time: 'O(h)',   space: 'O(1)' },
        'In-order':  { time: 'O(n)',   space: 'O(h)' },
        'Pre-order': { time: 'O(n)',   space: 'O(h)' },
        'Post-order':{ time: 'O(n)',   space: 'O(h)' },
      },
    },
    loadComponent: () =>
      import('../modules/bst/bst.component').then(m => m.BstComponent),
  },

  'graph-traversal': {
    meta: {
      slug: 'graph-traversal',
      title: 'Graph Traversal (BFS / DFS)',
      category: 'Graphs',
      description: 'Run Breadth-First and Depth-First Search on an undirected graph — watch the frontier expand and the queue/stack evolve.',
      operations: ['BFS', 'DFS'],
    },
    loadComponent: () =>
      import('../modules/graph-traversal/graph-traversal.component').then(m => m.GraphTraversalComponent),
  },

  'union-find': {
    meta: {
      slug: 'union-find',
      title: 'Union-Find (Disjoint Sets)',
      category: 'Graphs',
      description: 'Union by rank and Find with path compression — watch the disjoint-set forest merge and flatten.',
      operations: ['Union', 'Find'],
    },
    loadComponent: () =>
      import('../modules/union-find/union-find.component').then(m => m.UnionFindComponent),
  },

  'recursion-tree': {
    meta: {
      slug: 'recursion-tree',
      title: 'Recursion & DP Tree',
      category: 'Recursion & DP',
      description: 'Visualise recursive call trees for Factorial and Fibonacci — compare the naive exponential blow-up against memoization pruning whole subtrees.',
      operations: ['Factorial(n)', 'Fibonacci(n) — naive', 'Fibonacci(n) — memoized'],
    },
    loadComponent: () =>
      import('../modules/recursion-tree/recursion-tree.component').then(m => m.RecursionTreeComponent),
  },
};

/** Flat list for the catalog grid. */
export const VIZ_LIST: VizRegistryEntry[] = Object.values(VIZ_REGISTRY);

/** Group by category for the catalog grid. */
export function getVizByCategory(): Record<string, VizRegistryEntry[]> {
  const result: Record<string, VizRegistryEntry[]> = {};
  for (const entry of VIZ_LIST) {
    const cat = entry.meta.category;
    if (!result[cat]) result[cat] = [];
    result[cat].push(entry);
  }
  return result;
}
