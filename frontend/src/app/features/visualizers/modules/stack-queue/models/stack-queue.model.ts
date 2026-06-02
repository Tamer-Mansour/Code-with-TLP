// ── types ────────────────────────────────────────────────────────────────────

/** A single element held in the stack or queue. */
export interface SQElement {
  /** Unique ID so @for tracking + states map works correctly. */
  id: number;
  value: number;
}

/** Payload stored in every VizFrame.data for this visualiser. */
export interface SQFrameData {
  /** Ordered list of element IDs (top-of-stack = last, front-of-queue = first). */
  order: number[];
  /** The element ID that was just pushed/popped/enqueued/dequeued (may be undefined). */
  activeId?: number;
  /** Current structure type being shown. */
  mode: 'stack' | 'queue';
}
