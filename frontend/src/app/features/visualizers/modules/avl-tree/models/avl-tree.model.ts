import type { VizFrame } from '../../../core/viz-frame';

// ── AVL data model ────────────────────────────────────────────────────────────

export interface AvlNode {
  id: number;
  value: number;
  height: number;   // height of subtree rooted here
  left: AvlNode | null;
  right: AvlNode | null;
}

/**
 * Payload inside VizFrame.data for AVL frames.
 * The full serialised tree is cloned into every frame so the renderer
 * can lay it out independently.
 */
export interface AvlFrameData {
  /** Serialised tree root (null when the tree is empty). */
  root: SerialNode | null;
  /** Node ID that was just born (gets pop animation), or -1. */
  born: number;
}

/**
 * A plain-object mirror of AvlNode used inside VizFrame.data.
 * We serialise to this so frames remain pure JSON (no circular refs).
 */
export interface SerialNode {
  id: number;
  value: number;
  height: number;
  bf: number;           // balance factor at snapshot time
  left: SerialNode | null;
  right: SerialNode | null;
}

export interface NodePos { x: number; y: number; }

// ── frame-recording insert ────────────────────────────────────────────────────

/**
 * Stateful recorder passed through the recursive insert so we can
 * push frames at each significant step without returning giant tuples.
 */
export interface Recorder {
  frames: VizFrame[];
  /** The id of the newly created node (set once, never changes). */
  createdId: number;
  /** All node IDs visible at the point of the last pushed frame. */
  rootAtFrame: () => SerialNode | null;
}

// ── view-model types ──────────────────────────────────────────────────────────

export interface RenderedNode {
  id: number;
  value: number;
  bf: number;
  height: number;
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
