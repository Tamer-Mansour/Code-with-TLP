// ── data model ────────────────────────────────────────────────────────────

/**
 * Payload stored in VizFrame.data for every union-find frame.
 * parent[i] = parent of node i (parent[i] === i means root).
 * rank[i]   = rank (upper-bound on height) of the subtree rooted at i.
 */
export interface UfFrameData {
  parent: number[];
  rank:   number[];
}

// ── view model ────────────────────────────────────────────────────────────

export interface RenderedUfNode {
  id:    number;
  x:     number;
  y:     number;
  state: string;
  rank:  number;
}

export interface RenderedUfEdge {
  x1: number; y1: number;
  x2: number; y2: number;
  /** child node — used as track key */
  childId: number;
  /** pre-computed CSS class string */
  cls: string;
  /** pre-computed marker-end URL fragment */
  markerEnd: string;
}
