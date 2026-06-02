// ── types ────────────────────────────────────────────────────────────────────

/** State token for a single heap slot across one frame. */
export type HeapSlotState = 'default' | 'active' | 'compare' | 'swap' | 'done' | 'removed';

/** Payload carried in every VizFrame.data for this module. */
export interface HeapFrameData {
  /** Current heap array at this step (length is the live heap size). */
  heap: number[];
}

/** View-model for one SVG node. */
export interface RenderedNode {
  /** 0-based heap index. */
  idx: number;
  value: number;
  cx: number;
  cy: number;
  state: HeapSlotState;
}

/** View-model for one SVG edge (parent → child). */
export interface RenderedEdge {
  x1: number; y1: number;
  x2: number; y2: number;
}

/** View-model for one cell in the backing-array row. */
export interface ArrayCell {
  idx: number;
  value: number;
  state: HeapSlotState;
}
