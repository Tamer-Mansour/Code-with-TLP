import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, Shuffle, Plus, Search } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── BST data model ────────────────────────────────────────────────────────

interface BstNode {
  id: number;
  value: number;
  left: BstNode | null;
  right: BstNode | null;
}

/** Payload inside VizFrame.data for BST frames. */
interface BstFrameData {
  /** IDs of nodes that should be visible in this frame. */
  revealed: number[];
  /** ID of the "born" node (gets pop animation), or -1. */
  born: number;
}

// ── layout ────────────────────────────────────────────────────────────────

const NODE_R   = 22;
const GAP_X    = 58;
const GAP_Y    = 80;
const PAD      = 12;

interface NodePos { x: number; y: number; }

function layoutTree(
  root: BstNode | null,
  revealed: Set<number>
): { pos: Map<number, NodePos>; width: number; height: number } {
  const pos = new Map<number, NodePos>();
  let idx = 0;
  let maxDepth = 0;

  function walk(n: BstNode | null, depth: number): void {
    if (!n || !revealed.has(n.id)) return;
    walk(n.left, depth + 1);
    pos.set(n.id, { x: idx * GAP_X + PAD, y: depth * GAP_Y + PAD });
    idx++;
    maxDepth = Math.max(maxDepth, depth);
    walk(n.right, depth + 1);
  }
  walk(root, 0);

  return {
    pos,
    width:  Math.max(idx * GAP_X + PAD * 2, 240),
    height: (maxDepth + 1) * GAP_Y + PAD * 2,
  };
}

// ── frame builders ────────────────────────────────────────────────────────

let _nextId = 1;

function makeNode(value: number): BstNode {
  return { id: _nextId++, value, left: null, right: null };
}

function bstInsert(
  root: BstNode | null,
  value: number
): { root: BstNode; path: number[]; created: number | null } {
  const path: number[] = [];

  if (!root) {
    const n = makeNode(value);
    return { root: n, path: [], created: n.id };
  }

  // Clone the tree so previous frames are unaffected
  function clone(n: BstNode): BstNode {
    return { ...n, left: n.left ? clone(n.left) : null, right: n.right ? clone(n.right) : null };
  }
  const newRoot = clone(root);

  let cur = newRoot;
  while (true) {
    path.push(cur.id);
    if (value === cur.value) return { root: newRoot, path, created: null };
    if (value < cur.value) {
      if (!cur.left) {
        cur.left = makeNode(value);
        return { root: newRoot, path, created: cur.left.id };
      }
      cur = cur.left;
    } else {
      if (!cur.right) {
        cur.right = makeNode(value);
        return { root: newRoot, path, created: cur.right.id };
      }
      cur = cur.right;
    }
  }
}

function allIds(root: BstNode | null): Set<number> {
  const ids = new Set<number>();
  function walk(n: BstNode | null) {
    if (!n) return;
    ids.add(n.id);
    walk(n.left);
    walk(n.right);
  }
  walk(root);
  return ids;
}

function buildNodes(root: BstNode | null): Map<number, BstNode> {
  const map = new Map<number, BstNode>();
  function walk(n: BstNode | null) {
    if (!n) return;
    map.set(n.id, n);
    walk(n.left);
    walk(n.right);
  }
  walk(root);
  return map;
}

function frameInsert(root: BstNode, value: number, prev: Set<number>): VizFrame[] {
  const { root: newRoot, path, created } = bstInsert(root, value);
  const after = allIds(newRoot);
  const fs: VizFrame[] = [];

  if (created === null) {
    fs.push({
      note: `<b>${value}</b> already exists — BSTs hold unique keys.`,
      states: { [path[path.length - 1]]: 'miss' },
      data: { revealed: [...prev], born: -1 } as BstFrameData,
    });
    return fs;
  }

  if (path.length === 0) {
    fs.push({
      note: `Tree was empty — <b>${value}</b> becomes the root.`,
      states: { [created]: 'found' },
      data: { revealed: [created], born: created } as BstFrameData,
      pseudoLine: 1,
    });
    return fs;
  }

  const nodeMap = buildNodes(newRoot);

  path.forEach(id => {
    const nv = nodeMap.get(id)!.value;
    const dir = value < nv ? 'left' : 'right';
    fs.push({
      note: `At <b>${nv}</b>: ${value} ${value < nv ? '&lt;' : '&gt;'} ${nv} — go <b>${dir}</b>`,
      states: { [id]: 'visit' },
      data: { revealed: [...prev], born: -1 } as BstFrameData,
      pseudoLine: value < nv ? 2 : 4,
    });
  });

  fs.push({
    note: `Empty spot found — insert <b>${value}</b>`,
    states: { [created]: 'found' },
    data: { revealed: [...after], born: created } as BstFrameData,
    pseudoLine: 1,
  });
  fs.push({
    note: `<b>${value}</b> inserted successfully.`,
    states: {},
    data: { revealed: [...after], born: -1 } as BstFrameData,
    pseudoLine: 0,
  });

  return fs;
}

function frameSearch(root: BstNode | null, value: number): VizFrame[] {
  const ids = allIds(root);
  const nodeMap = buildNodes(root);
  const fs: VizFrame[] = [];
  let cur = root;
  let found = false;

  while (cur) {
    if (value === cur.value) {
      fs.push({
        note: `Found <b>${value}</b>`,
        states: { [cur.id]: 'found' },
        data: { revealed: [...ids], born: -1 } as BstFrameData,
        pseudoLine: 10,
      });
      found = true;
      break;
    }
    const dir = value < cur.value ? 'left' : 'right';
    fs.push({
      note: `At <b>${cur.value}</b>: ${value} ${value < cur.value ? '&lt;' : '&gt;'} ${cur.value} — go <b>${dir}</b>`,
      states: { [cur.id]: 'visit' },
      data: { revealed: [...ids], born: -1 } as BstFrameData,
      pseudoLine: value < cur.value ? 11 : 13,
    });
    cur = value < cur.value ? cur.left : cur.right;
  }

  if (!found) {
    fs.push({
      note: `<b>${value}</b> is not in the tree`,
      states: {},
      data: { revealed: [...ids], born: -1 } as BstFrameData,
      pseudoLine: 9,
    });
  }

  return fs;
}

function frameTraversal(root: BstNode | null, kind: 'in' | 'pre' | 'post'): VizFrame[] {
  const ids = allIds(root);
  const order: BstNode[] = [];

  function walk(n: BstNode | null) {
    if (!n) return;
    if (kind === 'pre') order.push(n);
    walk(n.left);
    if (kind === 'in') order.push(n);
    walk(n.right);
    if (kind === 'post') order.push(n);
  }
  walk(root);

  const fs: VizFrame[] = [];
  const seq: number[] = [];
  const names: Record<string, string> = { in: 'In-order', pre: 'Pre-order', post: 'Post-order' };
  const lineMap: Record<string, number> = { in: 18, pre: 16, post: 19 };

  order.forEach(n => {
    seq.push(n.value);
    fs.push({
      note: `${names[kind]} so far: <b>${seq.join(' → ')}</b>`,
      states: { [n.id]: 'visit' },
      data: { revealed: [...ids], born: -1 } as BstFrameData,
      pseudoLine: lineMap[kind],
    });
  });

  fs.push({
    note: `${names[kind]} traversal complete: <b>${seq.join(' → ')}</b>`,
    states: {},
    data: { revealed: [...ids], born: -1 } as BstFrameData,
    pseudoLine: 15,
  });

  return fs;
}

// ── default tree ──────────────────────────────────────────────────────────

function buildDefaultTree(): BstNode {
  _nextId = 1;
  const values = [50, 30, 70, 20, 40, 60, 80, 35, 65, 90];
  let root: BstNode | null = null;
  for (const v of values) {
    const res = bstInsert(root, v);
    root = res.root;
  }
  return root!;
}

// ── component ────────────────────────────────────────────────────────────

/** View-model for one rendered node. */
interface RenderedNode {
  id: number;
  value: number;
  x: number;
  y: number;
  state: string;
  born: boolean;
  visible: boolean;
}

interface RenderedEdge {
  x1: number; y1: number;
  x2: number; y2: number;
}

@Component({
  selector: 'app-bst',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './bst.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BstComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  readonly Plus   = Plus;
  readonly Search = Search;
  readonly Shuffle = Shuffle;

  readonly meta: VizMeta = {
    slug: 'bst',
    title: 'Binary Search Tree',
    category: 'Trees',
    description: 'Insert, search, and traverse a BST.',
    operations: ['Insert', 'Search', 'In-order', 'Pre-order', 'Post-order'],
  };

  readonly NODE_R = NODE_R;

  root  = signal<BstNode | null>(null);
  insertValue = signal('');
  searchValue = signal('');

  ngOnInit(): void {
    const t = buildDefaultTree();
    this.root.set(t);
    const ids = allIds(t);
    this.player.setFrames([{
      note: 'Sample tree loaded. Try insert, search, or a traversal.',
      states: {},
      data: { revealed: [...ids], born: -1 } as BstFrameData,
    }]);
  }

  onInsert(): void {
    const v = parseInt(this.insertValue(), 10);
    if (!Number.isFinite(v)) return;
    const cur = this.root();
    const prev = cur ? allIds(cur) : new Set<number>();

    const { root: newRoot } = bstInsert(cur, v);
    this.root.set(newRoot);

    const frames = cur
      ? frameInsert(cur, v, prev)
      : [{
          note: `Tree was empty — <b>${v}</b> becomes the root.`,
          states: { [newRoot.id]: 'found' },
          data: { revealed: [newRoot.id], born: newRoot.id } as BstFrameData,
          pseudoLine: 1,
        }];

    this.player.setFrames(frames);
    this.player.play();
    this.insertValue.set('');
  }

  onSearch(): void {
    const v = parseInt(this.searchValue(), 10);
    if (!Number.isFinite(v)) return;
    const frames = frameSearch(this.root(), v);
    this.player.setFrames(frames);
    this.player.play();
  }

  onTraversal(kind: 'in' | 'pre' | 'post'): void {
    if (!this.root()) return;
    const frames = frameTraversal(this.root(), kind);
    this.player.setFrames(frames);
    this.player.play();
  }

  onRandom(): void {
    const v = Math.floor(Math.random() * 99) + 1;
    this.insertValue.set(String(v));
    this.onInsert();
  }

  onReset(): void {
    const t = buildDefaultTree();
    this.root.set(t);
    const ids = allIds(t);
    this.player.setFrames([{
      note: 'Tree reset to default. Try insert, search, or a traversal.',
      states: {},
      data: { revealed: [...ids], born: -1 } as BstFrameData,
    }]);
  }

  onInsertInput(e: Event): void {
    this.insertValue.set((e.target as HTMLInputElement).value);
  }

  onSearchInput(e: Event): void {
    this.searchValue.set((e.target as HTMLInputElement).value);
  }

  onInsertKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') this.onInsert();
  }

  onSearchKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') this.onSearch();
  }

  // ── computed view model ────────────────────────────────────────────────

  readonly svgLayout = computed(() => {
    const frame = this.player.currentFrame();
    const root  = this.root();
    if (!root) return { nodes: [], edges: [], width: 240, height: 120 };

    const revealedIds: number[] = (frame?.data as BstFrameData | undefined)?.revealed ?? [...allIds(root)];
    const revealed = new Set(revealedIds);
    const born     = (frame?.data as BstFrameData | undefined)?.born ?? -1;
    const states   = frame?.states ?? {};

    const { pos, width, height } = layoutTree(root, revealed);
    const nodeMap = buildNodes(root);

    const nodes: RenderedNode[] = [];
    const edges: RenderedEdge[] = [];

    nodeMap.forEach((n, id) => {
      const p = pos.get(id);
      const visible = revealed.has(id) && !!p;
      nodes.push({
        id,
        value: n.value,
        x: p ? p.x : 0,
        y: p ? p.y : 0,
        state: states[id] ?? (visible ? 'default' : 'hidden'),
        born: born === id,
        visible,
      });

      if (visible && p) {
        for (const child of [n.left, n.right]) {
          if (child && revealed.has(child.id) && pos.has(child.id)) {
            const cp = pos.get(child.id)!;
            edges.push({
              x1: p.x  + NODE_R,
              y1: p.y  + NODE_R,
              x2: cp.x + NODE_R,
              y2: cp.y + NODE_R,
            });
          }
        }
      }
    });

    return { nodes, edges, width, height };
  });

  nodeClass(n: RenderedNode): string {
    const base = 'absolute rounded-full flex items-center justify-center font-bold text-sm text-white transition-all duration-300 select-none';
    const stateClasses: Record<string, string> = {
      default: 'brand-gradient shadow-md',
      visit:   'bg-gradient-to-br from-amber-400 to-amber-500 shadow-[0_0_0_4px_rgba(245,158,11,0.35)]',
      found:   'bg-gradient-to-br from-green-400 to-green-600 shadow-[0_0_0_4px_rgba(34,197,94,0.4)]',
      miss:    'bg-gradient-to-br from-red-400 to-red-600 shadow-[0_0_0_4px_rgba(239,68,68,0.4)]',
      hidden:  'opacity-0 scale-0 pointer-events-none',
    };
    return `${base} ${stateClasses[n.state] ?? stateClasses['default']} ${n.born ? 'animate-[pop_0.45s_cubic-bezier(.34,1.56,.64,1)]' : ''}`;
  }

  buildFrames(): VizFrame[] { return []; } // satisfies interface
}
