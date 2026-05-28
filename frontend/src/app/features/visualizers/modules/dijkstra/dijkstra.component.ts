import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, Play, RotateCcw, ChevronRight, Table2, ListOrdered } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── Graph definition ──────────────────────────────────────────────────────

/** A weighted graph node with pre-computed SVG layout position. */
interface GraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
}

/** A weighted undirected edge. */
interface WeightedEdge {
  a: string;
  b: string;
  w: number;
}

/** Distance-table entry stored per frame. */
export interface DistEntry {
  node: string;
  dist: number;
  prev: string | null;
}

/** Priority-queue entry stored per frame. */
export interface PQEntry {
  node: string;
  dist: number;
}

/** Payload stored inside VizFrame.data for each Dijkstra frame. */
export interface DijkstraFrameData {
  distTable: DistEntry[];
  pq: PQEntry[];
  settled: string[];
}

// ── Fixed sample graph — 8 nodes, weighted undirected ────────────────────
// Positions are absolute SVG coordinates within a 580 × 360 canvas.

const NODES: GraphNode[] = [
  { id: 'A', label: 'A', x:  80, y: 170 },
  { id: 'B', label: 'B', x: 200, y:  60 },
  { id: 'C', label: 'C', x: 200, y: 280 },
  { id: 'D', label: 'D', x: 340, y:  60 },
  { id: 'E', label: 'E', x: 340, y: 280 },
  { id: 'F', label: 'F', x: 460, y: 170 },
  { id: 'G', label: 'G', x: 500, y:  50 },
  { id: 'H', label: 'H', x: 500, y: 300 },
];

const EDGES: WeightedEdge[] = [
  { a: 'A', b: 'B', w:  4 },
  { a: 'A', b: 'C', w:  2 },
  { a: 'B', b: 'D', w:  5 },
  { a: 'B', b: 'E', w: 10 },
  { a: 'C', b: 'E', w:  3 },
  { a: 'D', b: 'F', w:  2 },
  { a: 'D', b: 'G', w:  6 },
  { a: 'E', b: 'F', w:  4 },
  { a: 'E', b: 'H', w:  7 },
  { a: 'F', b: 'G', w:  3 },
  { a: 'F', b: 'H', w:  5 },
];

const NODE_IDS = NODES.map(n => n.id);

/** Build weighted adjacency list. */
function buildWeightedAdj(): Map<string, { nb: string; w: number }[]> {
  const adj = new Map<string, { nb: string; w: number }[]>(
    NODES.map(n => [n.id, []]),
  );
  for (const e of EDGES) {
    adj.get(e.a)!.push({ nb: e.b, w: e.w });
    adj.get(e.b)!.push({ nb: e.a, w: e.w });
  }
  adj.forEach(list => list.sort((a, b) => a.nb.localeCompare(b.nb)));
  return adj;
}

const W_ADJ = buildWeightedAdj();

// ── Helpers ───────────────────────────────────────────────────────────────

const edgeKey = (a: string, b: string) => [a, b].sort().join('-');

const INF = Infinity;

function distLabel(d: number): string {
  return d === INF ? '∞' : String(d);
}

/** Minimal naive priority queue (no decrease-key — uses lazy deletion). */
class MinPQ {
  private _heap: PQEntry[] = [];

  push(entry: PQEntry): void {
    this._heap.push(entry);
    this._bubbleUp(this._heap.length - 1);
  }

  pop(): PQEntry | undefined {
    if (!this._heap.length) return undefined;
    this._swap(0, this._heap.length - 1);
    const top = this._heap.pop()!;
    this._sinkDown(0);
    return top;
  }

  get size(): number {
    return this._heap.length;
  }

  snapshot(): PQEntry[] {
    return [...this._heap].sort((a, b) => a.dist - b.dist);
  }

  private _bubbleUp(i: number): void {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (this._heap[parent].dist <= this._heap[i].dist) break;
      this._swap(parent, i);
      i = parent;
    }
  }

  private _sinkDown(i: number): void {
    const n = this._heap.length;
    while (true) {
      let smallest = i;
      const l = 2 * i + 1;
      const r = 2 * i + 2;
      if (l < n && this._heap[l].dist < this._heap[smallest].dist) smallest = l;
      if (r < n && this._heap[r].dist < this._heap[smallest].dist) smallest = r;
      if (smallest === i) break;
      this._swap(i, smallest);
      i = smallest;
    }
  }

  private _swap(i: number, j: number): void {
    [this._heap[i], this._heap[j]] = [this._heap[j], this._heap[i]];
  }
}

// ── Frame builder ─────────────────────────────────────────────────────────

function buildDijkstraFrames(startId: string): VizFrame[] {
  const frames: VizFrame[] = [];

  const dist: Record<string, number>       = {};
  const prev: Record<string, string | null> = {};
  const settled  = new Set<string>();
  const treeEdgeSet = new Set<string>();
  const relaxedEdgeSet = new Set<string>();

  for (const id of NODE_IDS) {
    dist[id] = INF;
    prev[id] = null;
  }
  dist[startId] = 0;

  const pq = new MinPQ();
  pq.push({ node: startId, dist: 0 });

  // ── Snapshot helpers ──────────────────────────────────────────────────

  const makeDistTable = (): DistEntry[] =>
    NODE_IDS.map(id => ({ node: id, dist: dist[id], prev: prev[id] }));

  const makeStates = (
    current: string | null,
    frontier: Set<string>,
    extra: Record<string, string> = {},
  ): Record<string, string> => {
    const states: Record<string, string> = {};
    for (const id of NODE_IDS) {
      if (settled.has(id))       states[id] = 'visited';
      else if (frontier.has(id)) states[id] = 'frontier';
      else                       states[id] = 'idle';
    }
    if (current) states[current] = 'current';
    for (const [k, v] of Object.entries(extra)) states[k] = v;
    // edge states
    treeEdgeSet.forEach(k  => { states[k] = 'tree';    });
    relaxedEdgeSet.forEach(k => { if (!treeEdgeSet.has(k)) states[k] = 'relaxed'; });
    return states;
  };

  const push = (
    note: string,
    current: string | null,
    frontier: Set<string>,
    extraStates: Record<string, string> = {},
  ) => {
    frames.push({
      note,
      states: makeStates(current, frontier, extraStates),
      data: {
        distTable: makeDistTable(),
        pq: pq.snapshot(),
        settled: [...settled],
      } satisfies DijkstraFrameData,
    });
  };

  // ── Initial frame ─────────────────────────────────────────────────────

  const frontierSet = new Set<string>([startId]);

  push(
    `Initialise Dijkstra from <b>${startId}</b>. Set dist[${startId}] = 0, all others = ∞. Enqueue (${startId}, 0).`,
    null,
    frontierSet,
  );

  // ── Main loop ─────────────────────────────────────────────────────────

  while (pq.size > 0) {
    const top = pq.pop()!;
    const u = top.node;

    // Lazy deletion — skip stale entries
    if (settled.has(u)) continue;

    settled.add(u);
    frontierSet.delete(u);

    push(
      `Extract minimum: <b>${u}</b> with dist = <b>${distLabel(dist[u])}</b>. Mark as settled.`,
      u,
      frontierSet,
    );

    // Process neighbours
    const neighbours = W_ADJ.get(u) ?? [];
    for (const { nb: v, w } of neighbours) {
      if (settled.has(v)) continue;

      const ek = edgeKey(u, v);
      relaxedEdgeSet.add(ek);
      const newDist = dist[u] + w;
      const oldDist = dist[v];

      if (newDist < oldDist) {
        // Relaxation succeeds
        dist[v] = newDist;
        prev[v] = u;
        treeEdgeSet.add(ek);
        pq.push({ node: v, dist: newDist });
        frontierSet.add(v);

        push(
          `Relax edge <b>${u} → ${v}</b> (weight ${w}): dist[${v}] updated ${distLabel(oldDist)} → <b>${newDist}</b>. Enqueue (${v}, ${newDist}).`,
          u,
          frontierSet,
          { [ek]: 'relaxed' },
        );
      } else {
        push(
          `Check edge <b>${u} → ${v}</b> (weight ${w}): ${dist[u]} + ${w} = ${newDist} ≥ dist[${v}] = ${distLabel(oldDist)}. No update.`,
          u,
          frontierSet,
          { [ek]: 'relaxed' },
        );
      }
    }
  }

  // ── Final frame ───────────────────────────────────────────────────────

  const reachable = NODE_IDS.filter(id => dist[id] !== INF);
  const summary = reachable
    .map(id => `${id}:${dist[id]}`)
    .join(', ');

  frames.push({
    note: `Dijkstra complete from <b>${startId}</b>. Shortest distances — ${summary}.`,
    states: makeStates(null, new Set()),
    data: {
      distTable: makeDistTable(),
      pq: [],
      settled: [...settled],
    } satisfies DijkstraFrameData,
  });

  return frames;
}

// ── Rendered view-model types ─────────────────────────────────────────────

export interface RenderedNode {
  id: string;
  label: string;
  x: number;
  y: number;
  state: string;
  dist: string;
}

export interface RenderedEdge {
  key: string;
  x1: number; y1: number;
  x2: number; y2: number;
  /** Mid-point for weight label. */
  mx: number;
  my: number;
  weight: number;
  state: 'tree' | 'relaxed' | 'default';
}

// ── Component ─────────────────────────────────────────────────────────────

const NODE_R = 22;
const SVG_W  = 580;
const SVG_H  = 360;

@Component({
  selector: 'app-viz-dijkstra',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './dijkstra.component.html',
  styleUrls: ['./dijkstra.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DijkstraComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  // Lucide icons
  readonly Play         = Play;
  readonly RotateCcw    = RotateCcw;
  readonly ChevronRight = ChevronRight;
  readonly Table2       = Table2;
  readonly ListOrdered  = ListOrdered;

  readonly NODE_R = NODE_R;
  readonly SVG_W  = SVG_W;
  readonly SVG_H  = SVG_H;

  readonly meta: VizMeta = {
    slug: 'dijkstra',
    title: "Dijkstra's Shortest Path",
    category: 'Graphs',
    description:
      "Visualise Dijkstra's single-source shortest-path algorithm on a fixed weighted undirected graph. " +
      'Shows step-by-step relaxation, the live distance table, and priority-queue contents.',
    operations: ['Shortest Path'],
    complexity: {
      'Shortest Path': { time: 'O((V + E) log V)', space: 'O(V + E)' },
    },
  };

  readonly nodeIds = NODE_IDS;

  readonly selectedStart = signal<string>('A');

  ngOnInit(): void {
    this._run();
  }

  selectStart(id: string): void {
    this.selectedStart.set(id);
    this._run();
  }

  onRun(): void {
    this._run();
    this.player.play();
  }

  onReset(): void {
    this._run();
  }

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const start = (input['start'] as string) ?? 'A';
    return buildDijkstraFrames(start);
  }

  private _run(): void {
    this.player.setFrames(buildDijkstraFrames(this.selectedStart()));
  }

  // ── Computed view model ───────────────────────────────────────────────

  readonly svgLayout = computed<{ nodes: RenderedNode[]; edges: RenderedEdge[] }>(() => {
    const frame  = this.player.currentFrame();
    const states = frame?.states ?? {};
    const data   = frame?.data as DijkstraFrameData | undefined;

    const distMap = new Map<string, number>(
      (data?.distTable ?? []).map(e => [e.node, e.dist]),
    );

    const nodes: RenderedNode[] = NODES.map(n => ({
      id:    n.id,
      label: n.label,
      x:     n.x,
      y:     n.y,
      state: (states[n.id] as string) ?? 'idle',
      dist:  distLabel(distMap.get(n.id) ?? INF),
    }));

    const nodeMap = new Map(NODES.map(n => [n.id, n]));
    const edges: RenderedEdge[] = EDGES.map(e => {
      const na  = nodeMap.get(e.a)!;
      const nb  = nodeMap.get(e.b)!;
      const key = edgeKey(e.a, e.b);
      const st  = states[key];
      return {
        key,
        x1: na.x, y1: na.y,
        x2: nb.x, y2: nb.y,
        mx: (na.x + nb.x) / 2,
        my: (na.y + nb.y) / 2,
        weight: e.w,
        state: st === 'tree' ? 'tree' : st === 'relaxed' ? 'relaxed' : 'default',
      };
    });

    return { nodes, edges };
  });

  readonly distTable = computed<DistEntry[]>(() => {
    const data = this.player.currentFrame()?.data as DijkstraFrameData | undefined;
    return data?.distTable ?? NODE_IDS.map(id => ({ node: id, dist: INF, prev: null }));
  });

  readonly pqEntries = computed<PQEntry[]>(() => {
    const data = this.player.currentFrame()?.data as DijkstraFrameData | undefined;
    return data?.pq ?? [];
  });

  readonly settledNodes = computed<string[]>(() => {
    const data = this.player.currentFrame()?.data as DijkstraFrameData | undefined;
    return data?.settled ?? [];
  });

  readonly currentNote = computed<string>(() =>
    this.player.currentFrame()?.note ?? '',
  );

  readonly stepLabel  = this.player.stepLabel;
  readonly atStart    = this.player.atStart;
  readonly atEnd      = this.player.atEnd;
  readonly isPlaying  = this.player.playing;

  onPlay():     void { this.player.play(); }
  onPause():    void { this.player.pause(); }
  onToggle():   void { this.player.toggle(); }
  onStep():     void { this.player.step(); }
  onStepBack(): void { this.player.stepBack(); }

  distLabelFn(d: number): string {
    return distLabel(d);
  }
}
