import { VizFrame } from './viz-frame';

/** Complexity info per operation. */
export interface VizComplexity {
  time: string;
  space: string;
}

/** Static metadata every module exposes. */
export interface VizMeta {
  slug: string;
  title: string;
  category: string;
  description: string;
  /** Available operation names (fed to buildFrames). */
  operations: string[];
  complexity?: Record<string, VizComplexity>;
}

/** Input a caller passes to buildFrames. */
export interface VizInput {
  /** Operation name (must be in meta.operations). */
  operation: string;
  /** Numeric array — primary input for array/sort/search visualizers. */
  array?: number[];
  /** Single target / value (search target, insert value, …). */
  value?: number;
  /** Any additional parameters keyed by name. */
  params?: Record<string, unknown>;
}

/**
 * Contract every visualizer module implements.
 * buildFrames is pure — it produces a frame list without touching the DOM.
 * The input type is intentionally loose (Record) so modules can extend it.
 */
export interface Visualizer {
  meta: VizMeta;
  buildFrames(input: Record<string, unknown>): VizFrame[];
}
