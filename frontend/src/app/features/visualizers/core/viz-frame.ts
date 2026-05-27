/**
 * VizFrame — one snapshot in an algorithm animation.
 *
 * Every module produces an array of VizFrames.  The VizPlayer service
 * advances through them one at a time; each module's component reads
 * the current frame and applies it to its view.
 */
export interface VizFrame {
  /** Human-readable explanation shown under the canvas for this step. */
  note: string;

  /**
   * 0-based line index to highlight in the pseudocode panel.
   * Omit (or set to -1) when no pseudocode line should be highlighted.
   */
  pseudoLine?: number;

  /**
   * Map from element ID (string) to a visual state token.
   * State tokens are module-defined — e.g. 'compare' | 'swap' | 'active'
   * | 'sorted' | 'found' | 'visit' | 'miss' | 'dim' | 'range'.
   */
  states?: Record<string, string>;

  /**
   * Module-specific payload — anything the module needs to reconstruct
   * the full visual (array order, tree revealed set, graph adjacency, …).
   * Type is unknown here; each module casts it to its own interface.
   */
  data?: unknown;
}
