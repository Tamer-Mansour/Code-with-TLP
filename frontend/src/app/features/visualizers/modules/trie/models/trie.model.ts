// ── Trie data model ───────────────────────────────────────────────────────────

export interface TrieNode {
  /** Unique stable ID (used as key in states map). */
  id: string;
  /** The character this node represents (empty string for root). */
  char: string;
  /** Whether this node marks the end of a complete word. */
  isEnd: boolean;
  /** Child nodes keyed by character. */
  children: Map<string, TrieNode>;
}

/** Payload stored in every VizFrame.data for trie frames. */
export interface TrieFrameData {
  /** A serialisable snapshot of the trie for layout / rendering. */
  root: TrieNodeSnapshot;
}

/** JSON-safe snapshot (Maps are not JSON-serialisable, so we use arrays). */
export interface TrieNodeSnapshot {
  id: string;
  char: string;
  isEnd: boolean;
  children: TrieNodeSnapshot[];
}

export interface RenderedTrieNode {
  id: string;
  char: string;
  isEnd: boolean;
  cx: number;
  cy: number;
  state: string;
}

export interface RenderedTrieEdge {
  x1: number; y1: number;
  x2: number; y2: number;
  label: string;
  labelX: number;
  labelY: number;
  state: string;
}

export interface LayoutNode {
  snap: TrieNodeSnapshot;
  cx: number;
  cy: number;
  depth: number;
}
