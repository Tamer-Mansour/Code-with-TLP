import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, Plus, Search, RotateCcw, GitBranch } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

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

// ── Trie state tokens (used in VizFrame.states) ───────────────────────────────
// 'current'  — node currently being examined
// 'path'     — node confirmed on the traversal path
// 'created'  — node just created (pop animation)
// 'word-end' — marks a complete-word terminal
// 'miss'     — traversal failed here (char not found)
// 'default'  — idle node

// ── Trie engine ───────────────────────────────────────────────────────────────

let _nodeCounter = 1;

function makeRoot(): TrieNode {
  return { id: 'root', char: '', isEnd: false, children: new Map() };
}

function makeNode(char: string, parentId: string): TrieNode {
  return { id: `${parentId}-${char}-${_nodeCounter++}`, char, isEnd: false, children: new Map() };
}

/** Deep-clone a trie so earlier frames hold immutable snapshots. */
function cloneTrie(node: TrieNode): TrieNode {
  const cloned: TrieNode = {
    id: node.id,
    char: node.char,
    isEnd: node.isEnd,
    children: new Map(),
  };
  for (const [ch, child] of node.children) {
    cloned.children.set(ch, cloneTrie(child));
  }
  return cloned;
}

/** Convert a live TrieNode tree into a JSON-safe snapshot. */
function toSnapshot(node: TrieNode): TrieNodeSnapshot {
  return {
    id: node.id,
    char: node.char,
    isEnd: node.isEnd,
    children: [...node.children.values()].map(toSnapshot),
  };
}

// ── Frame builders ────────────────────────────────────────────────────────────

function buildInsertFrames(root: TrieNode, word: string): VizFrame[] {
  const frames: VizFrame[] = [];
  if (!word) return frames;

  // Opening frame — announce intent
  frames.push({
    note: `Insert "<b>${word}</b>" — walk from root, creating missing nodes.`,
    states: { root: 'current' },
    data: { root: toSnapshot(cloneTrie(root)) } as TrieFrameData,
  });

  let cur = root;
  const pathStates: Record<string, string> = {};

  for (let i = 0; i < word.length; i++) {
    const ch = word[i];
    const remaining = word.slice(i + 1);
    const prefix = word.slice(0, i + 1);

    if (cur.children.has(ch)) {
      // Node already exists — just walk through it
      const child = cur.children.get(ch)!;
      pathStates[child.id] = 'path';
      frames.push({
        note: `'<b>${ch}</b>' already exists at depth ${i + 1} — follow it.` +
              (remaining ? ` Next: '<b>${remaining[0]}</b>'` : ''),
        states: { ...pathStates, [child.id]: 'current' },
        data: { root: toSnapshot(cloneTrie(root)) } as TrieFrameData,
      });
      cur = child;
    } else {
      // Must create a new node
      const newNode = makeNode(ch, cur.id);
      cur.children.set(ch, newNode);
      pathStates[newNode.id] = 'created';

      frames.push({
        note: `'<b>${ch}</b>' not found — create child node for prefix "<b>${prefix}</b>".`,
        states: { ...pathStates, [newNode.id]: 'created' },
        data: { root: toSnapshot(cloneTrie(root)) } as TrieFrameData,
      });
      cur = newNode;
    }
  }

  // Mark end-of-word
  cur.isEnd = true;
  const endStates: Record<string, string> = { ...pathStates, [cur.id]: 'word-end' };

  frames.push({
    note: `Mark <b>${cur.id === 'root' ? '(root)' : `'${cur.char}'`}</b> as end-of-word — "<b>${word}</b>" is now stored.`,
    states: endStates,
    data: { root: toSnapshot(cloneTrie(root)) } as TrieFrameData,
  });

  // Final settled frame
  const settledStates: Record<string, string> = {};
  for (const id of Object.keys(endStates)) {
    settledStates[id] = id === cur.id ? 'word-end' : 'path';
  }
  frames.push({
    note: `"<b>${word}</b>" inserted successfully.`,
    states: settledStates,
    data: { root: toSnapshot(cloneTrie(root)) } as TrieFrameData,
  });

  return frames;
}

function buildSearchFrames(root: TrieNode, word: string): VizFrame[] {
  const frames: VizFrame[] = [];
  if (!word) return frames;

  const snap = toSnapshot(cloneTrie(root));

  frames.push({
    note: `Search "<b>${word}</b>" — walk the trie character by character.`,
    states: { root: 'current' },
    data: { root: snap } as TrieFrameData,
  });

  let cur: TrieNode | undefined = root;
  const pathStates: Record<string, string> = {};

  for (let i = 0; i < word.length; i++) {
    const ch = word[i];
    const next: TrieNode | undefined = cur?.children.get(ch);

    if (!next) {
      frames.push({
        note: `'<b>${ch}</b>' not found — "<b>${word}</b>" is <b>not</b> in the trie.`,
        states: { ...pathStates, ...(cur ? { [cur.id]: 'miss' } : {}) },
        data: { root: snap } as TrieFrameData,
      });
      return frames;
    }

    pathStates[next.id] = 'path';
    frames.push({
      note: `'<b>${ch}</b>' found at depth ${i + 1}.${i < word.length - 1 ? ` Continue with '<b>${word[i + 1]}</b>'.` : ''}`,
      states: { ...pathStates, [next.id]: 'current' },
      data: { root: snap } as TrieFrameData,
    });
    cur = next;
  }

  if (cur?.isEnd) {
    const foundStates: Record<string, string> = {};
    for (const id of Object.keys(pathStates)) foundStates[id] = 'path';
    foundStates[cur.id] = 'word-end';
    frames.push({
      note: `All characters matched and end-of-word flag set — "<b>${word}</b>" <b>found</b>.`,
      states: foundStates,
      data: { root: snap } as TrieFrameData,
    });
  } else {
    frames.push({
      note: `All characters matched but no end-of-word flag — "<b>${word}</b>" is a prefix but not a stored word.`,
      states: { ...pathStates, ...(cur ? { [cur.id]: 'miss' } : {}) },
      data: { root: snap } as TrieFrameData,
    });
  }

  return frames;
}

function buildStartsWithFrames(root: TrieNode, prefix: string): VizFrame[] {
  const frames: VizFrame[] = [];
  if (!prefix) return frames;

  const snap = toSnapshot(cloneTrie(root));

  frames.push({
    note: `Starts-with "<b>${prefix}</b>" — walk the trie to verify this prefix exists.`,
    states: { root: 'current' },
    data: { root: snap } as TrieFrameData,
  });

  let cur: TrieNode | undefined = root;
  const pathStates: Record<string, string> = {};

  for (let i = 0; i < prefix.length; i++) {
    const ch = prefix[i];
    const next: TrieNode | undefined = cur?.children.get(ch);

    if (!next) {
      frames.push({
        note: `'<b>${ch}</b>' not found — no word starts with "<b>${prefix}</b>".`,
        states: { ...pathStates, ...(cur ? { [cur.id]: 'miss' } : {}) },
        data: { root: snap } as TrieFrameData,
      });
      return frames;
    }

    pathStates[next.id] = 'path';
    frames.push({
      note: `'<b>${ch}</b>' found at depth ${i + 1}.${i < prefix.length - 1 ? ` Continue with '<b>${prefix[i + 1]}</b>'.` : ''}`,
      states: { ...pathStates, [next.id]: 'current' },
      data: { root: snap } as TrieFrameData,
    });
    cur = next;
  }

  // Collect all words reachable from this node
  const words: string[] = [];
  function collectWords(n: TrieNode, acc: string) {
    if (n.isEnd) words.push(acc);
    for (const [ch, child] of n.children) collectWords(child, acc + ch);
  }
  if (cur) collectWords(cur, prefix);

  const resultNote = words.length
    ? `Prefix "<b>${prefix}</b>" exists. Words: <b>${words.join(', ')}</b>`
    : `Prefix "<b>${prefix}</b>" exists but no complete words extend it.`;

  const foundStates: Record<string, string> = {};
  for (const id of Object.keys(pathStates)) foundStates[id] = 'path';
  if (cur) foundStates[cur.id] = 'word-end';

  frames.push({
    note: resultNote,
    states: foundStates,
    data: { root: snap } as TrieFrameData,
  });

  return frames;
}

// ── Default trie ──────────────────────────────────────────────────────────────

function buildDefaultTrie(): TrieNode {
  _nodeCounter = 1;
  const root = makeRoot();
  const words = ['apple', 'app', 'apt', 'bat', 'ball', 'band', 'cat'];
  for (const w of words) {
    let cur = root;
    for (const ch of w) {
      if (!cur.children.has(ch)) cur.children.set(ch, makeNode(ch, cur.id));
      cur = cur.children.get(ch)!;
    }
    cur.isEnd = true;
  }
  return root;
}

// ── SVG layout ────────────────────────────────────────────────────────────────

const NODE_R   = 18;
const GAP_Y    = 72;
const PAD      = 24;
const MIN_H_GAP = 44;

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

interface LayoutNode {
  snap: TrieNodeSnapshot;
  cx: number;
  cy: number;
  depth: number;
}

/**
 * Computes (x, y) for every node using a simple left-to-right leaf-counting
 * algorithm: each leaf gets one horizontal slot; internal nodes are centred
 * over their children.
 */
function layoutTrie(root: TrieNodeSnapshot): {
  nodes: LayoutNode[];
  width: number;
  height: number;
} {
  const nodes: LayoutNode[] = [];
  let leafIndex = 0;
  let maxDepth = 0;

  function countLeaves(n: TrieNodeSnapshot): number {
    if (n.children.length === 0) return 1;
    return n.children.reduce((s, c) => s + countLeaves(c), 0);
  }

  function place(n: TrieNodeSnapshot, depth: number): number {
    maxDepth = Math.max(maxDepth, depth);
    if (n.children.length === 0) {
      const cx = leafIndex * MIN_H_GAP + PAD;
      leafIndex++;
      nodes.push({ snap: n, cx, cy: depth * GAP_Y + PAD, depth });
      return cx;
    }
    const childCenters: number[] = [];
    for (const child of n.children) {
      childCenters.push(place(child, depth + 1));
    }
    const cx = (childCenters[0] + childCenters[childCenters.length - 1]) / 2;
    nodes.push({ snap: n, cx, cy: depth * GAP_Y + PAD, depth });
    return cx;
  }

  const totalLeaves = countLeaves(root);
  const minWidth = Math.max(totalLeaves * MIN_H_GAP + PAD * 2, 240);

  place(root, 0);

  return {
    nodes,
    width: Math.max(leafIndex * MIN_H_GAP + PAD * 2, minWidth),
    height: (maxDepth + 1) * GAP_Y + PAD * 2,
  };
}

// ── Component ─────────────────────────────────────────────────────────────────

@Component({
  selector: 'app-viz-trie',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './trie.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TrieComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  // Lucide icons
  readonly Plus      = Plus;
  readonly Search    = Search;
  readonly RotateCcw = RotateCcw;
  readonly GitBranch = GitBranch;

  readonly NODE_R = NODE_R;

  readonly meta: VizMeta = {
    slug: 'trie',
    title: 'Trie (Prefix Tree)',
    category: 'Strings & Tries',
    description: 'Insert, search, and prefix-match words in a trie (prefix tree).',
    operations: ['Insert', 'Search', 'Starts-With'],
    complexity: {
      Insert:       { time: 'O(m)', space: 'O(m)' },
      Search:       { time: 'O(m)', space: 'O(1)' },
      'Starts-With': { time: 'O(m)', space: 'O(1)' },
    },
  };

  // ── mutable trie (lives in the component, frames hold snapshots) ──────────
  private trieRoot = signal<TrieNode>(makeRoot());

  // ── input signals ─────────────────────────────────────────────────────────
  readonly wordInput   = signal('');
  readonly activeOp    = signal<'Insert' | 'Search' | 'Starts-With'>('Insert');

  // ── lifecycle ─────────────────────────────────────────────────────────────

  ngOnInit(): void {
    const t = buildDefaultTrie();
    this.trieRoot.set(t);
    this.player.setFrames([{
      note: 'Sample trie loaded with: apple, app, apt, bat, ball, band, cat. Try Insert, Search, or Starts-With.',
      states: {},
      data: { root: toSnapshot(cloneTrie(t)) } as TrieFrameData,
    }]);
  }

  // ── user actions ──────────────────────────────────────────────────────────

  onRun(): void {
    const word = this.wordInput().trim().toLowerCase();
    if (!word) return;

    const op = this.activeOp();
    const root = this.trieRoot();
    let frames: VizFrame[];

    if (op === 'Insert') {
      frames = buildInsertFrames(root, word);
      // Root was mutated in place by buildInsertFrames; signal the change
      this.trieRoot.set(root);
    } else if (op === 'Search') {
      frames = buildSearchFrames(root, word);
    } else {
      frames = buildStartsWithFrames(root, word);
    }

    if (frames.length) {
      this.player.setFrames(frames);
      this.player.play();
    }
  }

  onKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') this.onRun();
  }

  onInput(e: Event): void {
    this.wordInput.set((e.target as HTMLInputElement).value);
  }

  onSetOp(op: 'Insert' | 'Search' | 'Starts-With'): void {
    this.activeOp.set(op);
  }

  onReset(): void {
    _nodeCounter = 1;
    const t = buildDefaultTrie();
    this.trieRoot.set(t);
    this.wordInput.set('');
    this.player.setFrames([{
      note: 'Trie reset. Sample words: apple, app, apt, bat, ball, band, cat.',
      states: {},
      data: { root: toSnapshot(cloneTrie(t)) } as TrieFrameData,
    }]);
  }

  // ── computed SVG layout ────────────────────────────────────────────────────

  readonly svgLayout = computed<{
    nodes: RenderedTrieNode[];
    edges: RenderedTrieEdge[];
    width: number;
    height: number;
  }>(() => {
    const frame = this.player.currentFrame();
    const frameData = frame?.data as TrieFrameData | undefined;
    const states    = frame?.states ?? {};

    // Fall back to the live trie when no frame is available
    const snapRoot = frameData?.root ?? toSnapshot(cloneTrie(this.trieRoot()));

    const { nodes: laid, width, height } = layoutTrie(snapRoot);
    const posById = new Map<string, { cx: number; cy: number }>();
    for (const ln of laid) posById.set(ln.snap.id, { cx: ln.cx, cy: ln.cy });

    const renderedNodes: RenderedTrieNode[] = laid.map(ln => ({
      id:    ln.snap.id,
      char:  ln.snap.char,
      isEnd: ln.snap.isEnd,
      cx:    ln.cx,
      cy:    ln.cy,
      state: states[ln.snap.id] ?? (ln.snap.isEnd ? 'word-end' : 'default'),
    }));

    // Build edges
    const renderedEdges: RenderedTrieEdge[] = [];

    function walkEdges(n: TrieNodeSnapshot) {
      const p = posById.get(n.id);
      if (!p) return;
      for (const child of n.children) {
        const cp = posById.get(child.id);
        if (!cp) { walkEdges(child); continue; }
        const edgeState = states[child.id] ?? 'default';
        renderedEdges.push({
          x1: p.cx,
          y1: p.cy + NODE_R,
          x2: cp.cx,
          y2: cp.cy - NODE_R,
          label: child.char,
          labelX: (p.cx + cp.cx) / 2,
          labelY: (p.cy + NODE_R + cp.cy - NODE_R) / 2,
          state: edgeState,
        });
        walkEdges(child);
      }
    }
    walkEdges(snapRoot);

    return { nodes: renderedNodes, edges: renderedEdges, width, height };
  });

  // ── style helpers ─────────────────────────────────────────────────────────

  nodeCircleClass(state: string): string {
    const base = 'transition-all duration-300';
    const map: Record<string, string> = {
      default:  'fill-trie-node stroke-trie-border',
      current:  'fill-amber-400 stroke-amber-500 animate-[trieGlow_0.5s_ease-in-out_infinite_alternate]',
      path:     'fill-blue-500 stroke-blue-400',
      created:  'fill-emerald-400 stroke-emerald-500 animate-[triePop_0.45s_cubic-bezier(.34,1.56,.64,1)]',
      'word-end': 'fill-violet-500 stroke-violet-400',
      miss:     'fill-red-500 stroke-red-400',
    };
    return `${base} ${map[state] ?? map['default']}`;
  }

  nodeTextClass(state: string): string {
    const colored = ['current', 'path', 'created', 'word-end', 'miss'];
    return colored.includes(state)
      ? 'fill-white font-semibold'
      : 'fill-app-text font-medium';
  }

  edgeClass(state: string): string {
    const map: Record<string, string> = {
      path:       'stroke-blue-400 stroke-[2.5]',
      current:    'stroke-amber-400 stroke-[2.5]',
      created:    'stroke-emerald-400 stroke-[2.5]',
      'word-end': 'stroke-violet-400 stroke-[2]',
      miss:       'stroke-red-400 stroke-[2]',
      default:    'stroke-app-border stroke-[1.5]',
    };
    return `transition-all duration-300 ${map[state] ?? map['default']}`;
  }

  edgeLabelClass(state: string): string {
    const map: Record<string, string> = {
      path:       'fill-blue-400',
      current:    'fill-amber-400',
      created:    'fill-emerald-400',
      'word-end': 'fill-violet-400',
      miss:       'fill-red-400',
      default:    'fill-app-text-muted',
    };
    return `text-[10px] font-mono select-none ${map[state] ?? map['default']}`;
  }

  // ── Visualizer contract ────────────────────────────────────────────────────

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const op   = (input['operation'] as string | undefined) ?? 'Insert';
    const word = ((input['word'] ?? input['value'] ?? '') as string).trim().toLowerCase();
    const root = this.trieRoot();

    if (op === 'Insert')      return buildInsertFrames(root, word);
    if (op === 'Search')      return buildSearchFrames(root, word);
    if (op === 'Starts-With') return buildStartsWithFrames(root, word);
    return [];
  }
}
