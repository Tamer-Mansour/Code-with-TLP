import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, Play, RotateCcw, ChevronRight } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── Graph definition ──────────────────────────────────────────────────────

/** A fixed undirected graph node with pre-computed layout position. */
interface GraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
}

/** An undirected edge between two node IDs. */
interface GraphEdge {
  a: string;
  b: string;
}

/** Payload stored inside VizFrame.data for each traversal frame. */
interface GraphFrameData {
  /** Ordered queue (BFS) or stack (DFS) contents at this moment. */
  buffer: string[];
  /** Set of node IDs already fully visited. */
  visited: string[];
}

// ── Fixed sample graph (~8 nodes) ─────────────────────────────────────────
// Positions are absolute SVG coordinates within a 560 × 340 canvas.

const NODES: GraphNode[] = [
  { id: 'A', label: 'A', x:  80, y:  80 },
  { id: 'B', label: 'B', x: 240, y:  40 },
  { id: 'C', label: 'C', x: 400, y:  80 },
  { id: 'D', label: 'D', x: 480, y: 200 },
  { id: 'E', label: 'E', x: 320, y: 220 },
  { id: 'F', label: 'F', x: 160, y: 220 },
  { id: 'G', label: 'G', x:  60, y: 300 },
  { id: 'H', label: 'H', x: 480, y: 320 },
];

const EDGES: GraphEdge[] = [
  { a: 'A', b: 'B' },
  { a: 'A', b: 'F' },
  { a: 'B', b: 'C' },
  { a: 'B', b: 'E' },
  { a: 'C', b: 'D' },
  { a: 'C', b: 'E' },
  { a: 'D', b: 'H' },
  { a: 'E', b: 'F' },
  { a: 'E', b: 'H' },
  { a: 'F', b: 'G' },
];

/** Build an adjacency list (sorted for deterministic traversal order). */
function buildAdjacency(): Map<string, string[]> {
  const adj = new Map<string, string[]>(NODES.map(n => [n.id, []]));
  for (const e of EDGES) {
    adj.get(e.a)!.push(e.b);
    adj.get(e.b)!.push(e.a);
  }
  // Sort neighbours alphabetically for stable output
  adj.forEach(neighbours => neighbours.sort());
  return adj;
}

const ADJ = buildAdjacency();

// ── Frame builders (pure) ─────────────────────────────────────────────────

const NODE_IDS = NODES.map(n => n.id);

function buildBfsFrames(startId: string): VizFrame[] {
  const frames: VizFrame[] = [];
  const visited = new Set<string>();
  const queue: string[] = [];
  const treeEdges = new Set<string>();

  const edgeKey = (a: string, b: string) => [a, b].sort().join('-');

  const push = (
    states: Record<string, string>,
    note: string,
    bufferSnapshot: string[],
  ) => {
    const data: GraphFrameData = {
      buffer: [...bufferSnapshot],
      visited: [...visited],
    };
    frames.push({ note, states: { ...states }, data });
  };

  // Initial frame
  push(
    Object.fromEntries(NODE_IDS.map(id => [id, 'idle'])),
    `BFS from node <b>${startId}</b>. Enqueue the start node.`,
    [],
  );

  queue.push(startId);
  const initStates: Record<string, string> = Object.fromEntries(NODE_IDS.map(id => [id, 'idle']));
  initStates[startId] = 'frontier';
  push(initStates, `Enqueue <b>${startId}</b> — queue: [${queue.join(', ')}]`, queue);

  while (queue.length > 0) {
    const current = queue.shift()!;
    if (visited.has(current)) continue;
    visited.add(current);

    const states: Record<string, string> = Object.fromEntries(
      NODE_IDS.map(id => {
        if (visited.has(id)) return [id, 'visited'];
        if (queue.includes(id)) return [id, 'frontier'];
        return [id, 'idle'];
      }),
    );
    states[current] = 'current';
    // mark tree edges
    const edgeStates: Record<string, string> = {};
    treeEdges.forEach(k => { edgeStates[k] = 'tree-edge'; });

    push(
      { ...states, ...edgeStates },
      `Dequeue <b>${current}</b> — mark as visited. Queue: [${queue.join(', ')}]`,
      queue,
    );

    const neighbours = ADJ.get(current) ?? [];
    for (const nb of neighbours) {
      if (!visited.has(nb) && !queue.includes(nb)) {
        queue.push(nb);
        treeEdges.add(edgeKey(current, nb));

        const nbStates: Record<string, string> = Object.fromEntries(
          NODE_IDS.map(id => {
            if (visited.has(id)) return [id, 'visited'];
            if (queue.includes(id)) return [id, 'frontier'];
            return [id, 'idle'];
          }),
        );
        nbStates[current] = 'current';
        const edgeSt: Record<string, string> = {};
        treeEdges.forEach(k => { edgeSt[k] = 'tree-edge'; });

        push(
          { ...nbStates, ...edgeSt },
          `Enqueue neighbour <b>${nb}</b>. Queue: [${queue.join(', ')}]`,
          queue,
        );
      }
    }
  }

  // Final frame
  const finalStates: Record<string, string> = Object.fromEntries(
    NODE_IDS.map(id => [id, visited.has(id) ? 'visited' : 'idle']),
  );
  const finalEdgeSt: Record<string, string> = {};
  treeEdges.forEach(k => { finalEdgeSt[k] = 'tree-edge'; });
  push(
    { ...finalStates, ...finalEdgeSt },
    `BFS complete. Visited order: <b>${[...visited].join(' → ')}</b>`,
    [],
  );

  return frames;
}

function buildDfsFrames(startId: string): VizFrame[] {
  const frames: VizFrame[] = [];
  const visited = new Set<string>();
  const stack: string[] = [];
  const treeEdges = new Set<string>();

  const edgeKey = (a: string, b: string) => [a, b].sort().join('-');
  const visitOrder: string[] = [];

  const push = (
    states: Record<string, string>,
    note: string,
    bufferSnapshot: string[],
  ) => {
    const data: GraphFrameData = {
      buffer: [...bufferSnapshot],
      visited: [...visited],
    };
    frames.push({ note, states: { ...states }, data });
  };

  push(
    Object.fromEntries(NODE_IDS.map(id => [id, 'idle'])),
    `DFS from node <b>${startId}</b>. Push the start node onto the stack.`,
    [],
  );

  stack.push(startId);
  const initStates: Record<string, string> = Object.fromEntries(NODE_IDS.map(id => [id, 'idle']));
  initStates[startId] = 'frontier';
  push(initStates, `Push <b>${startId}</b> — stack: [${[...stack].reverse().join(', ')}]`, [...stack].reverse());

  while (stack.length > 0) {
    const current = stack.pop()!;
    if (visited.has(current)) {
      // skip already-visited (iterative DFS may push duplicates)
      continue;
    }
    visited.add(current);
    visitOrder.push(current);

    const states: Record<string, string> = Object.fromEntries(
      NODE_IDS.map(id => {
        if (visited.has(id)) return [id, 'visited'];
        if (stack.includes(id)) return [id, 'frontier'];
        return [id, 'idle'];
      }),
    );
    states[current] = 'current';
    const edgeSt: Record<string, string> = {};
    treeEdges.forEach(k => { edgeSt[k] = 'tree-edge'; });

    push(
      { ...states, ...edgeSt },
      `Pop <b>${current}</b> — mark as visited. Stack: [${[...stack].reverse().join(', ')}]`,
      [...stack].reverse(),
    );

    // Push neighbours in reverse order so the smallest-alphabetical is processed first
    const neighbours = [...(ADJ.get(current) ?? [])].reverse();
    for (const nb of neighbours) {
      if (!visited.has(nb)) {
        stack.push(nb);
        treeEdges.add(edgeKey(current, nb));

        const nbStates: Record<string, string> = Object.fromEntries(
          NODE_IDS.map(id => {
            if (visited.has(id)) return [id, 'visited'];
            if (stack.includes(id)) return [id, 'frontier'];
            return [id, 'idle'];
          }),
        );
        nbStates[current] = 'current';
        const edgeSt2: Record<string, string> = {};
        treeEdges.forEach(k => { edgeSt2[k] = 'tree-edge'; });

        push(
          { ...nbStates, ...edgeSt2 },
          `Push neighbour <b>${nb}</b>. Stack top: <b>${stack[stack.length - 1]}</b> — [${[...stack].reverse().join(', ')}]`,
          [...stack].reverse(),
        );
      }
    }
  }

  const finalStates: Record<string, string> = Object.fromEntries(
    NODE_IDS.map(id => [id, visited.has(id) ? 'visited' : 'idle']),
  );
  const finalEdgeSt: Record<string, string> = {};
  treeEdges.forEach(k => { finalEdgeSt[k] = 'tree-edge'; });
  push(
    { ...finalStates, ...finalEdgeSt },
    `DFS complete. Visited order: <b>${visitOrder.join(' → ')}</b>`,
    [],
  );

  return frames;
}

// ── Rendered view-model types ──────────────────────────────────────────────

/** A node as seen by the template. */
export interface RenderedGraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
  /** State token: 'idle' | 'current' | 'visited' | 'frontier' */
  state: string;
}

/** An edge as seen by the template. */
export interface RenderedGraphEdge {
  key: string;
  x1: number; y1: number;
  x2: number; y2: number;
  /** Whether this edge is part of the spanning tree. */
  treeEdge: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────

const NODE_R = 20;
const SVG_W  = 560;
const SVG_H  = 360;

@Component({
  selector: 'app-viz-graph-traversal',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './graph-traversal.component.html',
  styleUrls: ['./graph-traversal.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GraphTraversalComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  readonly Play      = Play;
  readonly RotateCcw = RotateCcw;
  readonly ChevronRight = ChevronRight;

  readonly NODE_R = NODE_R;
  readonly SVG_W  = SVG_W;
  readonly SVG_H  = SVG_H;

  readonly meta: VizMeta = {
    slug: 'graph-traversal',
    title: 'Graph Traversal',
    category: 'Graphs',
    description: 'Visualise Breadth-First Search (BFS) and Depth-First Search (DFS) on an undirected graph.',
    operations: ['BFS', 'DFS'],
  };

  /** All node IDs available as start nodes. */
  readonly nodeIds = NODE_IDS;

  readonly selectedStart = signal<string>('A');
  readonly selectedOp    = signal<'BFS' | 'DFS'>('BFS');

  ngOnInit(): void {
    this._run();
  }

  selectStart(id: string): void {
    this.selectedStart.set(id);
    this._run();
  }

  selectOp(op: 'BFS' | 'DFS'): void {
    this.selectedOp.set(op);
    this._run();
  }

  onReset(): void {
    this._run();
  }

  onRun(): void {
    this._run();
    this.player.play();
  }

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const op    = (input['operation'] as string) ?? 'BFS';
    const start = (input['start'] as string)     ?? 'A';
    return op === 'DFS' ? buildDfsFrames(start) : buildBfsFrames(start);
  }

  private _run(): void {
    const frames = this.buildFrames({
      operation: this.selectedOp(),
      start: this.selectedStart(),
    });
    this.player.setFrames(frames);
  }

  // ── Computed view model ────────────────────────────────────────────────

  readonly svgLayout = computed<{ nodes: RenderedGraphNode[]; edges: RenderedGraphEdge[] }>(() => {
    const frame  = this.player.currentFrame();
    const states = frame?.states ?? {};

    const nodes: RenderedGraphNode[] = NODES.map(n => ({
      id:    n.id,
      label: n.label,
      x:     n.x,
      y:     n.y,
      state: (states[n.id] as string) ?? 'idle',
    }));

    const edgeKey = (a: string, b: string) => [a, b].sort().join('-');
    const nodeMap = new Map(NODES.map(n => [n.id, n]));

    const edges: RenderedGraphEdge[] = EDGES.map(e => {
      const na = nodeMap.get(e.a)!;
      const nb = nodeMap.get(e.b)!;
      const key = edgeKey(e.a, e.b);
      return {
        key,
        x1: na.x, y1: na.y,
        x2: nb.x, y2: nb.y,
        treeEdge: states[key] === 'tree-edge',
      };
    });

    return { nodes, edges };
  });

  /** Buffer (queue for BFS, stack for DFS) from the current frame data. */
  readonly currentBuffer = computed<string[]>(() => {
    const frame = this.player.currentFrame();
    return (frame?.data as GraphFrameData | undefined)?.buffer ?? [];
  });

  /** Visited set from the current frame data. */
  readonly currentVisited = computed<string[]>(() => {
    const frame = this.player.currentFrame();
    return (frame?.data as GraphFrameData | undefined)?.visited ?? [];
  });

  /** Label for the buffer section header. */
  readonly bufferLabel = computed(() =>
    this.selectedOp() === 'BFS' ? 'Queue' : 'Stack',
  );

}
