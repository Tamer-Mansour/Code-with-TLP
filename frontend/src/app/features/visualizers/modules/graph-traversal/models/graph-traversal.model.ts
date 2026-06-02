// ── Graph definition ──────────────────────────────────────────────────────

/** A fixed undirected graph node with pre-computed layout position. */
export interface GraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
}

/** An undirected edge between two node IDs. */
export interface GraphEdge {
  a: string;
  b: string;
}

/** Payload stored inside VizFrame.data for each traversal frame. */
export interface GraphFrameData {
  /** Ordered queue (BFS) or stack (DFS) contents at this moment. */
  buffer: string[];
  /** Set of node IDs already fully visited. */
  visited: string[];
}

// ── Rendered view-model types ──────────────────────────────────────────────

/** A node as seen by the template. */
export interface RenderedGraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
  /** State token: 'idle' | 'current' | 'visited' | 'frontier' */
  state: string;
}

/** An edge as seen by the template. */
export interface RenderedGraphEdge {
  key: string;
  x1: number; y1: number;
  x2: number; y2: number;
  /** Whether this edge is part of the spanning tree. */
  treeEdge: boolean;
}
