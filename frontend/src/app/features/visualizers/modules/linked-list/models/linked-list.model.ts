// ── data model ────────────────────────────────────────────────────────────────

export interface LLNode {
  id: number;
  value: number;
}

/** Payload stored in every VizFrame.data for linked-list frames. */
export interface LLFrameData {
  /** Ordered list of node ids representing the current list state. */
  order: number[];
  /** Node ids that have been visually removed (for fade-out on last frame). */
  removed?: number[];
}
