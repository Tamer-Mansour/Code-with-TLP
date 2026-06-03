// ── Claude-style chat rendering primitives ──────────────────────────────────
// Shared by the full-page chat (/chat) and the in-lesson tutor. A streamed
// assistant message is split into ordered "parts": prose segments rendered as
// markdown, and fenced code blocks lifted into a side "artifact" panel
// (Monaco) — mirroring Claude's artifacts UX.

/** A fenced code block extracted from an assistant message. */
export interface CodeArtifact {
  /** Stable id within a single message (`cb-0`, `cb-1`, …) so the panel/editor
   *  is reused as more tokens stream in rather than recreated. */
  id: string;
  /** Lowercased fence language (`python`, `ts`, …) or `'text'`. */
  language: string;
  /** Human label shown in the card / panel header (e.g. "Python"). */
  title: string;
  /** The code body, without the surrounding fences. */
  code: string;
  /** False while the closing fence has not streamed in yet. */
  complete: boolean;
  /** Number of non-empty-trimmed lines — drives auto-open + preview height. */
  lineCount: number;
}

/** One ordered piece of a rendered assistant message. */
export type MessagePart =
  | { kind: 'text'; markdown: string }
  | { kind: 'code'; artifact: CodeArtifact };
