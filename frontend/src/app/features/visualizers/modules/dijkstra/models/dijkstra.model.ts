// ── Graph definition ──────────────────────────────────────────────────────

/** A weighted graph node with pre-computed SVG layout position. */
export interface GraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
}

/** A weighted undirected edge. */
export interface WeightedEdge {
  a: string;
  b: string;
  w: number;
}

/** Distance-table entry stored per frame. */
export interface DistEntry {
  node: string;
  dist: number;
  prev: string | null;
}

/** Priority-queue entry stored per frame. */
export interface PQEntry {
  node: string;
  dist: number;
}

/** Payload stored inside VizFrame.data for each Dijkstra frame. */
export interface DijkstraFrameData {
  distTable: DistEntry[];
  pq: PQEntry[];
  settled: string[];
}

// ── Rendered view-model types ─────────────────────────────────────────────

export interface RenderedNode {
  id: string;
  label: string;
  x: number;
  y: number;
  state: string;
  dist: string;
}

export interface RenderedEdge {
  key: string;
  x1: number; y1: number;
  x2: number; y2: number;
  /** Mid-point for weight label. */
  mx: number;
  my: number;
  weight: number;
  state: 'tree' | 'relaxed' | 'default';
}
