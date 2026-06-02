import type { VizFrame } from '../../../core/viz-frame';

// ── Data model ────────────────────────────────────────────────────────────

/** Visual state token for a recursion call node. */
export type NodeState = 'calling' | 'returning' | 'memo-hit' | 'done' | 'idle';

/** A node in the recursion call tree (used for layout + rendering). */
export interface CallNode {
  id: string;
  label: string;
  depth: number;
  parentId: string | null;
  childIds: string[];
  returnValue: number | null;
  x: number;
  y: number;
}

/** Payload stored in VizFrame.data. */
export interface RecursionFrameData {
  /** IDs revealed so far (call order). */
  revealed: string[];
  /** Return value labels known at this frame step. */
  returnLabels: Record<string, number>;
}

// ── Result bundle returned by every frame builder ─────────────────────────

export interface BuildResult {
  frames: VizFrame[];
  /** Stable node map for SVG rendering (covers the full final tree). */
  nodeMap: Map<string, CallNode>;
}

// ── Rendered view-model ───────────────────────────────────────────────────

/** Rendered node view-model. */
export interface RenderedNode {
  id: string; label: string;
  cx: number; cy: number;
  state: string; returnValue: number | null; visible: boolean;
}

/** Rendered edge view-model. */
export interface RenderedEdge {
  x1: number; y1: number; x2: number; y2: number;
}
