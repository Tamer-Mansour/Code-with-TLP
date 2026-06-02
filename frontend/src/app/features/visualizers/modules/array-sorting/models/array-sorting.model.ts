// ── types ────────────────────────────────────────────────────────────────

/** Payload stored in VizFrame.data for each array frame. */
export interface ArrayFrameData {
  /** Display order: array of original IDs in the current visual positions. */
  order: number[];
}

/** A tracked bar item. */
export interface BarItem {
  id: number;
  value: number;
}
