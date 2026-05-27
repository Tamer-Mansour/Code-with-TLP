import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, RefreshCw, GitMerge, Search } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── constants ─────────────────────────────────────────────────────────────

const N = 10; // elements 0..9
const NODE_R = 24;
const SVG_W  = 680;
const SVG_H  = 300;

// ── data model ────────────────────────────────────────────────────────────

/**
 * Payload stored in VizFrame.data for every union-find frame.
 * parent[i] = parent of node i (parent[i] === i means root).
 * rank[i]   = rank (upper-bound on height) of the subtree rooted at i.
 */
export interface UfFrameData {
  parent: number[];
  rank:   number[];
}

// node state tokens used in VizFrame.states
// 'default' | 'current' | 'root' | 'path' | 'merged' | 'dim'

// ── geometry helpers ──────────────────────────────────────────────────────

/**
 * Lay out nodes as a forest (one row per "tree level") derived from the
 * parent array.  Returns an (x, y) map per node index.
 *
 * Algorithm:
 *  1. Build children lists.
 *  2. Assign a depth to every node (0 = root).
 *  3. Within each depth-group sort by node index.
 *  4. Spread nodes evenly across SVG_W.
 */
function computeLayout(parent: number[]): Map<number, { x: number; y: number }> {
  const n = parent.length;
  const children: number[][] = Array.from({ length: n }, () => []);
  const depth = new Array<number>(n).fill(0);

  // build children lists and depth
  for (let i = 0; i < n; i++) {
    if (parent[i] !== i) {
      children[parent[i]].push(i);
    }
  }

  // BFS from each root to assign depths
  const queue: number[] = [];
  for (let i = 0; i < n; i++) {
    if (parent[i] === i) { queue.push(i); depth[i] = 0; }
  }
  let qi = 0;
  while (qi < queue.length) {
    const node = queue[qi++];
    for (const child of children[node]) {
      depth[child] = depth[node] + 1;
      queue.push(child);
    }
  }

  // group by depth
  const byDepth = new Map<number, number[]>();
  for (let i = 0; i < n; i++) {
    const d = depth[i];
    if (!byDepth.has(d)) byDepth.set(d, []);
    byDepth.get(d)!.push(i);
  }
  const maxDepth = Math.max(...byDepth.keys());

  const VERTICAL_GAP = maxDepth > 0
    ? Math.min(90, (SVG_H - NODE_R * 4) / maxDepth)
    : 0;

  const pos = new Map<number, { x: number; y: number }>();

  byDepth.forEach((nodes, d) => {
    const cnt = nodes.length;
    const sorted = [...nodes].sort((a, b) => a - b);
    sorted.forEach((nodeId, i) => {
      const x = ((i + 1) / (cnt + 1)) * SVG_W;
      const y = NODE_R * 2 + d * VERTICAL_GAP;
      pos.set(nodeId, { x, y });
    });
  });

  return pos;
}

// ── Union-Find data structure (pure, immutable-style) ─────────────────────

function makeUF(n: number): UfFrameData {
  return {
    parent: Array.from({ length: n }, (_, i) => i),
    rank:   new Array(n).fill(0),
  };
}

function cloneUF(uf: UfFrameData): UfFrameData {
  return { parent: [...uf.parent], rank: [...uf.rank] };
}

/** Returns the full path from x up to (and including) its root. */
function pathToRoot(parent: number[], x: number): number[] {
  const path: number[] = [];
  let cur = x;
  while (parent[cur] !== cur) {
    path.push(cur);
    cur = parent[cur];
  }
  path.push(cur); // include root
  return path;
}

// ── frame builders ────────────────────────────────────────────────────────

/** Build frames for Find(x) with path compression. */
function buildFind(uf: UfFrameData, x: number): { frames: VizFrame[]; uf: UfFrameData } {
  const frames: VizFrame[] = [];
  const work = cloneUF(uf);

  // ── phase 1: walk up to root ──────────────────────────────────────────
  const path = pathToRoot(work.parent, x);
  const root = path[path.length - 1];

  frames.push({
    note: `Find(<b>${x}</b>): starting walk up from node <b>${x}</b> to find the root.`,
    pseudoLine: 0,
    states: { [x]: 'current' },
    data: cloneUF(work),
  });

  for (let i = 0; i < path.length - 1; i++) {
    const cur = path[i];
    const par = path[i + 1];
    const pathStates: Record<string, string> = {};
    path.slice(0, i + 1).forEach(n => { pathStates[n] = 'path'; });
    pathStates[cur] = 'current';
    pathStates[root] = 'root';
    frames.push({
      note: `Find(<b>${x}</b>): node <b>${cur}</b> → parent <b>${par}</b>${par === root ? ' (root found)' : ''}`,
      pseudoLine: 1,
      states: pathStates,
      data: cloneUF(work),
    });
  }

  const pathStr = path.join(' → ');
  frames.push({
    note: `Find(<b>${x}</b>): root is <b>${root}</b>. Path: ${pathStr}. Applying path compression.`,
    pseudoLine: 2,
    states: { [root]: 'root', ...Object.fromEntries(path.slice(0, -1).map(n => [n, 'path'])) },
    data: cloneUF(work),
  });

  // ── phase 2: path compression ─────────────────────────────────────────
  if (path.length > 2) {
    // compress: point every node in path directly to root
    for (let i = 0; i < path.length - 1; i++) {
      work.parent[path[i]] = root;
    }
    const compressStates: Record<string, string> = { [root]: 'root' };
    path.slice(0, -1).forEach(n => { compressStates[n] = 'merged'; });
    frames.push({
      note: `Path compressed: nodes <b>${path.slice(0, -1).join(', ')}</b> now point directly to root <b>${root}</b>.`,
      pseudoLine: 3,
      states: compressStates,
      data: cloneUF(work),
    });
  } else {
    frames.push({
      note: `No compression needed — <b>${x}</b> is already ${x === root ? 'the root' : 'a direct child of root'}.`,
      pseudoLine: 3,
      states: { [root]: 'root', [x]: 'path' },
      data: cloneUF(work),
    });
  }

  frames.push({
    note: `Find(<b>${x}</b>) = <b>${root}</b>. Tree is now flat under root ${root}.`,
    pseudoLine: 4,
    states: { [root]: 'root' },
    data: cloneUF(work),
  });

  return { frames, uf: work };
}

/** Build frames for Union(a, b) by rank. */
function buildUnion(uf: UfFrameData, a: number, b: number): { frames: VizFrame[]; uf: UfFrameData } {
  const frames: VizFrame[] = [];
  const work = cloneUF(uf);

  frames.push({
    note: `Union(<b>${a}</b>, <b>${b}</b>): finding roots of both nodes.`,
    pseudoLine: 6,
    states: { [a]: 'current', [b]: 'current' },
    data: cloneUF(work),
  });

  // find root of a (with path compression frames)
  const pathA = pathToRoot(work.parent, a);
  const rootA = pathA[pathA.length - 1];
  frames.push({
    note: `Union: root of <b>${a}</b> is <b>${rootA}</b> (path: ${pathA.join(' → ')}).`,
    pseudoLine: 7,
    states: { [rootA]: 'root', ...Object.fromEntries(pathA.map(n => [n, n === rootA ? 'root' : 'path'])) },
    data: cloneUF(work),
  });

  // find root of b
  const pathB = pathToRoot(work.parent, b);
  const rootB = pathB[pathB.length - 1];
  frames.push({
    note: `Union: root of <b>${b}</b> is <b>${rootB}</b> (path: ${pathB.join(' → ')}).`,
    pseudoLine: 8,
    states: {
      [rootA]: 'root',
      [rootB]: 'root',
      ...Object.fromEntries(pathA.map(n => [n, n === rootA ? 'root' : 'path'])),
      ...Object.fromEntries(pathB.map(n => [n, n === rootB ? 'root' : 'path'])),
    },
    data: cloneUF(work),
  });

  if (rootA === rootB) {
    frames.push({
      note: `Union(<b>${a}</b>, <b>${b}</b>): both already in the same set (root = <b>${rootA}</b>). No-op.`,
      pseudoLine: 9,
      states: { [rootA]: 'root' },
      data: cloneUF(work),
    });
    return { frames, uf: work };
  }

  // union by rank
  const rA = work.rank[rootA];
  const rB = work.rank[rootB];

  frames.push({
    note: `Union by rank: rank[${rootA}]=${rA}, rank[${rootB}]=${rB}. ` +
      (rA < rB
        ? `rank(${rootA}) < rank(${rootB}) → attach tree of <b>${rootA}</b> under <b>${rootB}</b>.`
        : rA > rB
          ? `rank(${rootA}) > rank(${rootB}) → attach tree of <b>${rootB}</b> under <b>${rootA}</b>.`
          : `Equal ranks → attach <b>${rootB}</b> under <b>${rootA}</b> and increment rank[${rootA}].`),
    pseudoLine: 10,
    states: { [rootA]: 'root', [rootB]: 'root' },
    data: cloneUF(work),
  });

  if (rA < rB) {
    work.parent[rootA] = rootB;
    frames.push({
      note: `Attached: parent[<b>${rootA}</b>] = <b>${rootB}</b>. Set <b>${rootB}</b> is now the combined root.`,
      pseudoLine: 11,
      states: { [rootB]: 'root', [rootA]: 'merged' },
      data: cloneUF(work),
    });
  } else if (rA > rB) {
    work.parent[rootB] = rootA;
    frames.push({
      note: `Attached: parent[<b>${rootB}</b>] = <b>${rootA}</b>. Set <b>${rootA}</b> is now the combined root.`,
      pseudoLine: 11,
      states: { [rootA]: 'root', [rootB]: 'merged' },
      data: cloneUF(work),
    });
  } else {
    work.parent[rootB] = rootA;
    work.rank[rootA]++;
    frames.push({
      note: `Attached: parent[<b>${rootB}</b>] = <b>${rootA}</b>, rank[<b>${rootA}</b>] → ${work.rank[rootA]}.`,
      pseudoLine: 12,
      states: { [rootA]: 'root', [rootB]: 'merged' },
      data: cloneUF(work),
    });
  }

  frames.push({
    note: `Union(<b>${a}</b>, <b>${b}</b>) complete. Both elements now share the same set.`,
    pseudoLine: 13,
    states: { [rootA === work.parent[rootA] ? rootA : rootB]: 'root' },
    data: cloneUF(work),
  });

  return { frames, uf: work };
}

// ── view model ────────────────────────────────────────────────────────────

export interface RenderedUfNode {
  id:    number;
  x:     number;
  y:     number;
  state: string;
  rank:  number;
}

export interface RenderedUfEdge {
  x1: number; y1: number;
  x2: number; y2: number;
  /** child node — used as track key */
  childId: number;
  /** pre-computed CSS class string */
  cls: string;
  /** pre-computed marker-end URL fragment */
  markerEnd: string;
}

// ── pseudocode lines ──────────────────────────────────────────────────────

export const PSEUDO_FIND = [
  '0  find(x):',
  '1    while parent[x] ≠ x: walk up',
  '2    root ← current node',
  '3    path-compress: set parent[n] = root',
  '4    return root',
];

export const PSEUDO_UNION = [
  '6  union(a, b):',
  '7    rootA ← find(a)',
  '8    rootB ← find(b)',
  '9    if rootA = rootB: return (same set)',
  '10   compare rank[rootA] vs rank[rootB]',
  '11   attach smaller-rank tree under larger',
  '12   if equal ranks: attach b→a, rank[a]++',
  '13   done',
];

// ── component ────────────────────────────────────────────────────────────

@Component({
  selector: 'app-viz-union-find',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './union-find.component.html',
  styleUrls: ['./union-find.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UnionFindComponent implements OnInit, Visualizer {
  readonly player = inject(VizPlayerService);

  // lucide icons
  readonly RefreshCw  = RefreshCw;
  readonly GitMerge   = GitMerge;
  readonly SearchIcon = Search;

  readonly SVG_W  = SVG_W;
  readonly SVG_H  = SVG_H;
  readonly NODE_R = NODE_R;

  // ── Visualizer interface ───────────────────────────────────────────────

  readonly meta: VizMeta = {
    slug: 'union-find',
    title: 'Union-Find (Disjoint Set)',
    category: 'Graphs',
    description:
      'Visualizes the Union-Find / Disjoint Set data structure with ' +
      'path compression and union by rank.',
    operations: ['Find', 'Union', 'Reset'],
    complexity: {
      Find:  { time: 'O(α(n))', space: 'O(1)' },
      Union: { time: 'O(α(n))', space: 'O(1)' },
    },
  };

  // ── internal state ─────────────────────────────────────────────────────

  readonly uf = signal<UfFrameData>(makeUF(N));

  // form inputs
  readonly unionA = signal(0);
  readonly unionB = signal(1);
  readonly findX  = signal(0);

  // active pseudocode panel: 'find' | 'union' | null
  readonly activeOp = signal<'find' | 'union' | null>(null);

  readonly pseudoFind  = PSEUDO_FIND;
  readonly pseudoUnion = PSEUDO_UNION;

  // ── lifecycle ──────────────────────────────────────────────────────────

  ngOnInit(): void {
    this._loadInitialFrame();
  }

  // ── operations ─────────────────────────────────────────────────────────

  onFind(): void {
    const x = this.findX();
    if (x < 0 || x >= N) return;
    const { frames, uf: next } = buildFind(this.uf(), x);
    this.uf.set(next);
    this.activeOp.set('find');
    this.player.setFrames(frames);
    this.player.play();
  }

  onUnion(): void {
    const a = this.unionA();
    const b = this.unionB();
    if (a < 0 || a >= N || b < 0 || b >= N) return;
    const { frames, uf: next } = buildUnion(this.uf(), a, b);
    this.uf.set(next);
    this.activeOp.set('union');
    this.player.setFrames(frames);
    this.player.play();
  }

  onReset(): void {
    this.uf.set(makeUF(N));
    this.activeOp.set(null);
    this._loadInitialFrame();
  }

  // ── input handlers ─────────────────────────────────────────────────────

  onUnionAChange(e: Event): void {
    this.unionA.set(+(e.target as HTMLInputElement).value);
  }

  onUnionBChange(e: Event): void {
    this.unionB.set(+(e.target as HTMLInputElement).value);
  }

  onFindXChange(e: Event): void {
    this.findX.set(+(e.target as HTMLInputElement).value);
  }

  onUnionAKeydown(e: KeyboardEvent): void { if (e.key === 'Enter') this.onUnion(); }
  onUnionBKeydown(e: KeyboardEvent): void { if (e.key === 'Enter') this.onUnion(); }
  onFindXKeydown(e: KeyboardEvent): void  { if (e.key === 'Enter') this.onFind(); }

  // ── Visualizer.buildFrames (satisfies interface) ───────────────────────

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const op = input['operation'] as string;
    const a  = (input['a']  as number) ?? 0;
    const b  = (input['b']  as number) ?? 1;
    switch (op) {
      case 'Find':  return buildFind(this.uf(), a).frames;
      case 'Union': return buildUnion(this.uf(), a, b).frames;
      default:      return [];
    }
  }

  // ── computed view model ────────────────────────────────────────────────

  /**
   * Derives the full SVG layout from the current frame's data payload.
   * Falls back to the live `uf` signal if no frame is loaded yet.
   */
  readonly svgLayout = computed(() => {
    const frame = this.player.currentFrame();
    const data  = (frame?.data as UfFrameData | undefined) ?? this.uf();
    const states = frame?.states ?? {};

    const { parent, rank } = data;
    const pos = computeLayout(parent);

    const nodes: RenderedUfNode[] = [];
    const edges: RenderedUfEdge[] = [];

    for (let i = 0; i < parent.length; i++) {
      const p = pos.get(i)!;
      nodes.push({
        id:    i,
        x:     p.x,
        y:     p.y,
        state: states[i] ?? (parent[i] === i ? 'root' : 'default'),
        rank:  rank[i],
      });

      // draw edge child → parent (upward arrow)
      if (parent[i] !== i) {
        const pp = pos.get(parent[i])!;
        const childState = states[i] ?? 'default';
        const edgeCls =
          childState === 'path' || childState === 'current' ? 'uf-edge-active' :
          childState === 'merged'                           ? 'uf-edge-merged'  :
                                                             'uf-edge-default';
        const markerEnd =
          edgeCls === 'uf-edge-active' ? 'url(#uf-arrow-active)' :
          edgeCls === 'uf-edge-merged' ? 'url(#uf-arrow-merged)' :
                                         'url(#uf-arrow-default)';
        edges.push({
          x1: p.x,
          y1: p.y,
          x2: pp.x,
          y2: pp.y,
          childId: i,
          cls: edgeCls,
          markerEnd,
        });
      }
    }

    return { nodes, edges };
  });

  /** Active pseudocode line from current frame (for highlight). */
  readonly activePseudoLine = computed(() => {
    return this.player.currentFrame()?.pseudoLine ?? -1;
  });

  /** Note text from current frame. */
  readonly currentNote = computed(() => {
    return this.player.currentFrame()?.note ?? 'Ready. Enter a Union or Find operation below.';
  });

  // ── CSS class helpers ──────────────────────────────────────────────────

  nodeCircleClass(state: string): string {
    const base = 'transition-all duration-300';
    const map: Record<string, string> = {
      default: 'uf-node-default',
      root:    'uf-node-root',
      current: 'uf-node-current',
      path:    'uf-node-path',
      merged:  'uf-node-merged',
      dim:     'uf-node-dim',
    };
    return `${base} ${map[state] ?? map['default']}`;
  }

  nodeTextClass(state: string): string {
    const light = ['current', 'root', 'merged'];
    return light.includes(state)
      ? 'fill-white font-bold text-sm'
      : 'fill-app-text font-semibold text-sm';
  }

  // ── private helpers ────────────────────────────────────────────────────

  private _loadInitialFrame(): void {
    const initial = this.uf();
    this.player.setFrames([{
      note: 'Initial state: 10 singleton sets {0}, {1}, ..., {9}. Each node is its own root.',
      states: Object.fromEntries(Array.from({ length: N }, (_, i) => [i, 'root'])),
      data: cloneUF(initial),
    }]);
  }
}
