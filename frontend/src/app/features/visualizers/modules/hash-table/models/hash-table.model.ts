// ── Types ─────────────────────────────────────────────────────────────────

/** A single node in a bucket's linked chain. */
export interface HtNode {
  key: number;
  /** State token: 'idle' | 'active' | 'compare' | 'found' | 'miss' | 'inserting' | 'deleting' */
  state?: string;
}

/** One bucket row (index + its chain). */
export interface HtBucket {
  index: number;
  /** State token for the bucket row itself: 'idle' | 'active' | 'found' | 'miss' */
  state?: string;
  chain: HtNode[];
}

/** Payload stored in VizFrame.data for each hash-table frame. */
export interface HtFrameData {
  buckets: HtBucket[];
  /** Total number of keys currently stored. */
  size: number;
}
