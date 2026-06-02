// ── BST data model ────────────────────────────────────────────────────────

export interface BstNode {
  id: number;
  value: number;
  left: BstNode | null;
  right: BstNode | null;
}

/** Payload inside VizFrame.data for BST frames. */
export interface BstFrameData {
  /** IDs of nodes that should be visible in this frame. */
  revealed: number[];
  /** ID of the "born" node (gets pop animation), or -1. */
  born: number;
}

export interface NodePos { x: number; y: number; }

/** View-model for one rendered node. */
export interface RenderedNode {
  id: number;
  value: number;
  x: number;
  y: number;
  state: string;
  born: boolean;
  visible: boolean;
}

export interface RenderedEdge {
  x1: number; y1: number;
  x2: number; y2: number;
}
