// ── Graph definition ──────────────────────────────────────────────────────

/** A fixed weighted undirected graph node with pre-computed SVG position. */
export interface MstNode {
  id: string;
  x: number;
  y: number;
}

/** A weighted undirected edge. */
export interface MstEdgeDef {
  a: string;
  b: string;
  weight: number;
}

/** Payload stored in VizFrame.data for each MST frame. */
export interface MstFrameData {
  /** Accumulated MST weight so far. */
  mstWeight: number;
  /** Kruskal-only: the sorted edge list with current scan index. */
  sortedEdges?: Array<{ a: string; b: string; weight: number; status: 'pending' | 'in-mst' | 'rejected' | 'considering' }>;
  /** Prim-only: nodes currently in the MST set. */
  primInMst?: string[];
  /** Prim-only: min-heap snapshot [{node, key, via}]. */
  primQueue?: Array<{ node: string; key: number; via: string }>;
}

// ── Rendered view-model types ─────────────────────────────────────────────

export interface RenderedMstNode {
  id: string;
  x: number;
  y: number;
  state: string;
}

export interface RenderedMstEdge {
  key: string;
  x1: number; y1: number;
  x2: number; y2: number;
  mx: number; my: number; // midpoint for weight label
  weight: number;
  state: string; // 'idle' | 'in-mst' | 'rejected' | 'considering'
}
