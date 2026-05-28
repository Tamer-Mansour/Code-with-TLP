import {
  Component,
  inject,
  signal,
  computed,
  OnInit,
  ChangeDetectionStrategy,
} from '@angular/core';
import {
  LucideAngularModule,
  Play,
  RotateCcw,
  CircleCheck,
  CircleX,
  List,
  Weight,
  Zap,
} from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── Graph definition ──────────────────────────────────────────────────────

/** A fixed weighted undirected graph node with pre-computed SVG position. */
interface MstNode {
  id: string;
  x: number;
  y: number;
}

/** A weighted undirected edge. */
interface MstEdgeDef {
  a: string;
  b: string;
  weight: number;
}

/** Payload stored in VizFrame.data for each MST frame. */
interface MstFrameData {
  /** Accumulated MST weight so far. */
  mstWeight: number;
  /** Kruskal-only: the sorted edge list with current scan index. */
  sortedEdges?: Array<{ a: string; b: string; weight: number; status: 'pending' | 'in-mst' | 'rejected' | 'considering' }>;
  /** Prim-only: nodes currently in the MST set. */
  primInMst?: string[];
  /** Prim-only: min-heap snapshot [{node, key, via}]. */
  primQueue?: Array<{ node: string; key: number; via: string }>;
}

// ── Fixed sample graph (7 nodes, 11 edges) ────────────────────────────────
// Positions are absolute SVG coordinates within a 560 × 340 canvas.

const NODES: MstNode[] = [
  { id: 'A', x:  80, y:  80 },
  { id: 'B', x: 240, y:  40 },
  { id: 'C', x: 420, y:  60 },
  { id: 'D', x: 500, y: 190 },
  { id: 'E', x: 320, y: 230 },
  { id: 'F', x: 140, y: 250 },
  { id: 'G', x:  60, y: 310 },
];

const EDGES: MstEdgeDef[] = [
  { a: 'A', b: 'B', weight:  4 },
  { a: 'A', b: 'F', weight:  2 },
  { a: 'B', b: 'C', weight:  5 },
  { a: 'B', b: 'E', weight:  8 },
  { a: 'B', b: 'F', weight:  6 },
  { a: 'C', b: 'D', weight:  3 },
  { a: 'C', b: 'E', weight:  7 },
  { a: 'D', b: 'E', weight:  9 },
  { a: 'E', b: 'F', weight:  1 },
  { a: 'F', b: 'G', weight: 10 },
  { a: 'A', b: 'G', weight: 11 },
];

const NODE_IDS = NODES.map(n => n.id);
const NODE_MAP = new Map(NODES.map(n => [n.id, n]));

const edgeKey = (a: string, b: string): string => [a, b].sort().join('::');

// ── Union-Find helpers (Kruskal) ──────────────────────────────────────────

function makeUF(ids: string[]): Map<string, string> {
  return new Map(ids.map(id => [id, id]));
}

function find(parent: Map<string, string>, x: string): string {
  while (parent.get(x) !== x) {
    const p = parent.get(x)!;
    parent.set(x, parent.get(p)!); // path compression
    x = p;
  }
  return x;
}

function union(parent: Map<string, string>, a: string, b: string): boolean {
  const ra = find(parent, a);
  const rb = find(parent, b);
  if (ra === rb) return false;
  parent.set(ra, rb);
  return true;
}

// ── Kruskal frame builder ─────────────────────────────────────────────────

function buildKruskalFrames(): VizFrame[] {
  const frames: VizFrame[] = [];

  const sorted = [...EDGES].sort((x, y) => x.weight - y.weight);
  const parent = makeUF(NODE_IDS);

  const edgeStatus = new Map<string, 'pending' | 'in-mst' | 'rejected' | 'considering'>(
    sorted.map(e => [edgeKey(e.a, e.b), 'pending' as const]),
  );

  const nodeState = (): Record<string, string> =>
    Object.fromEntries(NODE_IDS.map(id => [id, 'idle']));

  const edgeState = (): Record<string, string> =>
    Object.fromEntries(
      sorted.map(e => {
        const k = edgeKey(e.a, e.b);
        return [k, edgeStatus.get(k)!];
      }),
    );

  const sortedSnapshot = () =>
    sorted.map(e => ({
      a: e.a,
      b: e.b,
      weight: e.weight,
      status: edgeStatus.get(edgeKey(e.a, e.b))!,
    }));

  let mstWeight = 0;

  // Initial frame
  frames.push({
    note: 'Kruskal: sort all edges by weight ascending. Process each edge — add it if it does not create a cycle.',
    states: { ...nodeState(), ...edgeState() },
    data: { mstWeight: 0, sortedEdges: sortedSnapshot() } satisfies MstFrameData,
  });

  for (const e of sorted) {
    const key = edgeKey(e.a, e.b);
    edgeStatus.set(key, 'considering');

    const ns: Record<string, string> = nodeState();
    ns[e.a] = 'considering';
    ns[e.b] = 'considering';

    frames.push({
      note: `Consider edge <b>${e.a}–${e.b}</b> (weight ${e.weight}). Check if <b>${e.a}</b> and <b>${e.b}</b> are in the same component.`,
      states: { ...ns, ...edgeState() },
      data: { mstWeight, sortedEdges: sortedSnapshot() } satisfies MstFrameData,
    });

    const canAdd = union(parent, e.a, e.b);

    if (canAdd) {
      mstWeight += e.weight;
      edgeStatus.set(key, 'in-mst');
      const ns2: Record<string, string> = Object.fromEntries(
        NODE_IDS.map(id => {
          // A node is "in-mst" if it is connected to the growing MST
          const r = find(parent, id);
          const anyMst = [...edgeStatus.entries()].some(
            ([k, s]) => s === 'in-mst' && (k.includes(id + '::') || k.includes('::' + id)),
          );
          return [id, anyMst ? 'in-mst' : 'idle'];
        }),
      );
      frames.push({
        note: `Add edge <b>${e.a}–${e.b}</b> (weight ${e.weight}) to MST. Total MST weight: <b>${mstWeight}</b>.`,
        states: { ...ns2, ...edgeState() },
        data: { mstWeight, sortedEdges: sortedSnapshot() } satisfies MstFrameData,
      });
    } else {
      edgeStatus.set(key, 'rejected');
      const ns2: Record<string, string> = nodeState();
      ns2[e.a] = 'rejected';
      ns2[e.b] = 'rejected';
      frames.push({
        note: `Reject edge <b>${e.a}–${e.b}</b> — both nodes already connected; would create a cycle.`,
        states: { ...ns2, ...edgeState() },
        data: { mstWeight, sortedEdges: sortedSnapshot() } satisfies MstFrameData,
      });
      // reset node highlight to reflect in-mst membership
      const restoredNs: Record<string, string> = Object.fromEntries(
        NODE_IDS.map(id => {
          const anyMst = [...edgeStatus.entries()].some(
            ([k, s]) => s === 'in-mst' && (k.includes(id + '::') || k.includes('::' + id)),
          );
          return [id, anyMst ? 'in-mst' : 'idle'];
        }),
      );
      frames[frames.length - 1] = {
        ...frames[frames.length - 1],
        states: { ...restoredNs, ...edgeState() },
      };
    }
  }

  // Final frame
  const finalNs: Record<string, string> = Object.fromEntries(
    NODE_IDS.map(id => {
      const anyMst = [...edgeStatus.entries()].some(
        ([k, s]) => s === 'in-mst' && (k.includes(id + '::') || k.includes('::' + id)),
      );
      return [id, anyMst ? 'in-mst' : 'idle'];
    }),
  );
  frames.push({
    note: `Kruskal complete. MST total weight: <b>${mstWeight}</b>. All ${NODE_IDS.length - 1} edges selected.`,
    states: { ...finalNs, ...edgeState() },
    data: { mstWeight, sortedEdges: sortedSnapshot() } satisfies MstFrameData,
  });

  return frames;
}

// ── Prim frame builder ────────────────────────────────────────────────────

function buildPrimFrames(startId: string): VizFrame[] {
  const frames: VizFrame[] = [];

  // key[v] = min weight edge connecting v to current MST (-1 = infinity)
  const key = new Map<string, number>(NODE_IDS.map(id => [id, -1]));
  const via = new Map<string, string>(NODE_IDS.map(id => [id, '']));
  const inMst = new Set<string>();
  const mstEdges = new Set<string>();

  key.set(startId, 0);
  let mstWeight = 0;

  const edgeStatusMap = new Map<string, 'idle' | 'in-mst' | 'rejected' | 'considering'>(
    EDGES.map(e => [edgeKey(e.a, e.b), 'idle' as const]),
  );

  const nodeSnap = (): Record<string, string> =>
    Object.fromEntries(
      NODE_IDS.map(id => {
        if (inMst.has(id)) return [id, 'in-mst'];
        if (key.get(id) !== -1) return [id, 'frontier'];
        return [id, 'idle'];
      }),
    );

  const edgeSnap = (): Record<string, string> =>
    Object.fromEntries([...edgeStatusMap.entries()]);

  const queueSnap = () =>
    NODE_IDS
      .filter(id => !inMst.has(id) && key.get(id) !== -1)
      .map(id => ({ node: id, key: key.get(id)!, via: via.get(id)! }))
      .sort((a, b) => a.key - b.key);

  // Initial frame
  key.set(startId, 0);
  frames.push({
    note: `Prim from <b>${startId}</b>: initialise key[${startId}] = 0, all others = ∞. Extract min-key vertex each round.`,
    states: { ...nodeSnap(), ...edgeSnap() },
    data: {
      mstWeight: 0,
      primInMst: [...inMst],
      primQueue: queueSnap(),
    } satisfies MstFrameData,
  });

  while (inMst.size < NODE_IDS.length) {
    // Find min-key vertex not yet in MST
    let u = '';
    let minKey = Infinity;
    for (const id of NODE_IDS) {
      if (!inMst.has(id) && key.get(id) !== -1 && key.get(id)! < minKey) {
        minKey = key.get(id)!;
        u = id;
      }
    }
    if (!u) break; // disconnected component (shouldn't happen for this graph)

    // Mark considering
    const ns1 = nodeSnap();
    ns1[u] = 'considering';
    const viaNode = via.get(u);
    let consideringEdgeKey = '';
    if (viaNode) {
      consideringEdgeKey = edgeKey(u, viaNode);
      edgeStatusMap.set(consideringEdgeKey, 'considering');
    }

    frames.push({
      note: `Extract min: <b>${u}</b> (key=${key.get(u)})${viaNode ? ` via edge <b>${viaNode}–${u}</b>` : ' (start)'}. Add to MST.`,
      states: { ...ns1, ...edgeSnap() },
      data: {
        mstWeight,
        primInMst: [...inMst],
        primQueue: queueSnap(),
      } satisfies MstFrameData,
    });

    // Add to MST
    inMst.add(u);
    if (viaNode) {
      mstWeight += key.get(u)!;
      mstEdges.add(edgeKey(u, viaNode));
      edgeStatusMap.set(edgeKey(u, viaNode), 'in-mst');
    }

    frames.push({
      note: `<b>${u}</b> joined MST${viaNode ? ` via edge <b>${viaNode}–${u}</b> (weight ${key.get(u)})` : ''}. MST weight so far: <b>${mstWeight}</b>.`,
      states: { ...nodeSnap(), ...edgeSnap() },
      data: {
        mstWeight,
        primInMst: [...inMst],
        primQueue: queueSnap(),
      } satisfies MstFrameData,
    });

    // Update keys of adjacent nodes
    for (const e of EDGES) {
      let neighbour = '';
      if (e.a === u) neighbour = e.b;
      else if (e.b === u) neighbour = e.a;
      else continue;

      if (inMst.has(neighbour)) continue;

      const k = edgeKey(u, neighbour);
      edgeStatusMap.set(k, 'considering');
      const ns2 = nodeSnap();
      ns2[neighbour] = 'considering';

      frames.push({
        note: `Check neighbour <b>${neighbour}</b> via <b>${u}–${neighbour}</b> (weight ${e.weight}). Current key[${neighbour}] = ${key.get(neighbour) === -1 ? '∞' : key.get(neighbour)}.`,
        states: { ...ns2, ...edgeSnap() },
        data: {
          mstWeight,
          primInMst: [...inMst],
          primQueue: queueSnap(),
        } satisfies MstFrameData,
      });

      if (key.get(neighbour) === -1 || e.weight < key.get(neighbour)!) {
        key.set(neighbour, e.weight);
        via.set(neighbour, u);
        edgeStatusMap.set(k, 'considering');
        frames.push({
          note: `Update key[<b>${neighbour}</b>] = ${e.weight} (better path via <b>${u}</b>).`,
          states: { ...nodeSnap(), ...edgeSnap() },
          data: {
            mstWeight,
            primInMst: [...inMst],
            primQueue: queueSnap(),
          } satisfies MstFrameData,
        });
      } else {
        edgeStatusMap.set(k, 'idle');
        frames.push({
          note: `No update for <b>${neighbour}</b> — existing key (${key.get(neighbour)}) ≤ ${e.weight}.`,
          states: { ...nodeSnap(), ...edgeSnap() },
          data: {
            mstWeight,
            primInMst: [...inMst],
            primQueue: queueSnap(),
          } satisfies MstFrameData,
        });
      }
    }
  }

  // Final frame
  frames.push({
    note: `Prim complete. MST total weight: <b>${mstWeight}</b>. All nodes connected.`,
    states: { ...nodeSnap(), ...edgeSnap() },
    data: {
      mstWeight,
      primInMst: [...inMst],
      primQueue: [],
    } satisfies MstFrameData,
  });

  return frames;
}

// ── Rendered view-model types ─────────────────────────────────────────────

export interface RenderedMstNode {
  id: string;
  x: number;
  y: number;
  state: string;
}

export interface RenderedMstEdge {
  key: string;
  x1: number; y1: number;
  x2: number; y2: number;
  mx: number; my: number; // midpoint for weight label
  weight: number;
  state: string; // 'idle' | 'in-mst' | 'rejected' | 'considering'
}

// ── Component ─────────────────────────────────────────────────────────────

const NODE_R = 20;
const SVG_W  = 560;
const SVG_H  = 360;

@Component({
  selector: 'app-viz-mst',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './mst.component.html',
  styleUrls: ['./mst.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MstComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  // Lucide icons
  readonly Play         = Play;
  readonly RotateCcw    = RotateCcw;
  readonly CircleCheck  = CircleCheck;
  readonly CircleX      = CircleX;
  readonly List         = List;
  readonly Weight       = Weight;
  readonly Zap          = Zap;

  readonly NODE_R = NODE_R;
  readonly SVG_W  = SVG_W;
  readonly SVG_H  = SVG_H;

  readonly nodeIds = NODE_IDS;

  readonly selectedOp    = signal<'Prim' | 'Kruskal'>('Prim');
  readonly selectedStart = signal<string>('A');

  // ── Visualizer contract ─────────────────────────────────────────────────

  readonly meta: VizMeta = {
    slug: 'mst',
    title: 'Minimum Spanning Tree',
    category: 'Graphs',
    description: 'Visualise Prim\'s and Kruskal\'s algorithms for finding the Minimum Spanning Tree of a weighted undirected graph.',
    operations: ['Prim', 'Kruskal'],
  };

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const op    = (input['operation'] as string) ?? 'Prim';
    const start = (input['start']     as string) ?? 'A';
    return op === 'Kruskal' ? buildKruskalFrames() : buildPrimFrames(start);
  }

  // ── Lifecycle ───────────────────────────────────────────────────────────

  ngOnInit(): void {
    this._run();
  }

  // ── User actions ────────────────────────────────────────────────────────

  selectOp(op: 'Prim' | 'Kruskal'): void {
    this.selectedOp.set(op);
    this._run();
  }

  selectStart(id: string): void {
    this.selectedStart.set(id);
    if (this.selectedOp() === 'Prim') this._run();
  }

  onRun(): void {
    this._run();
    this.player.play();
  }

  onReset(): void {
    this._run();
  }

  // ── Internal ────────────────────────────────────────────────────────────

  private _run(): void {
    const frames = this.buildFrames({
      operation: this.selectedOp(),
      start:     this.selectedStart(),
    });
    this.player.setFrames(frames);
  }

  // ── Computed view model ─────────────────────────────────────────────────

  readonly svgLayout = computed<{ nodes: RenderedMstNode[]; edges: RenderedMstEdge[] }>(() => {
    const frame  = this.player.currentFrame();
    const states = frame?.states ?? {};

    const nodes: RenderedMstNode[] = NODES.map(n => ({
      id:    n.id,
      x:     n.x,
      y:     n.y,
      state: (states[n.id] as string) ?? 'idle',
    }));

    const edges: RenderedMstEdge[] = EDGES.map(e => {
      const na  = NODE_MAP.get(e.a)!;
      const nb  = NODE_MAP.get(e.b)!;
      const key = edgeKey(e.a, e.b);
      return {
        key,
        x1: na.x, y1: na.y,
        x2: nb.x, y2: nb.y,
        mx: (na.x + nb.x) / 2,
        my: (na.y + nb.y) / 2,
        weight: e.weight,
        state: (states[key] as string) ?? 'idle',
      };
    });

    return { nodes, edges };
  });

  readonly frameData = computed<MstFrameData | null>(() => {
    const f = this.player.currentFrame();
    return (f?.data as MstFrameData | undefined) ?? null;
  });

  readonly mstWeight = computed<number>(() => this.frameData()?.mstWeight ?? 0);

  readonly sortedEdges = computed(() => this.frameData()?.sortedEdges ?? []);

  readonly primQueue   = computed(() => this.frameData()?.primQueue   ?? []);

  readonly primInMst   = computed(() => this.frameData()?.primInMst   ?? []);

  readonly isKruskal   = computed(() => this.selectedOp() === 'Kruskal');
  readonly isPrim      = computed(() => this.selectedOp() === 'Prim');

  readonly stepLabel = computed(() => this.player.stepLabel());
  readonly progress  = computed(() => this.player.progress());
  readonly atEnd     = computed(() => this.player.atEnd());
  readonly atStart   = computed(() => this.player.atStart());
  readonly playing   = computed(() => this.player.playing());
  readonly currentNote = computed(() => this.player.currentFrame()?.note ?? '');
}
