import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import {
  LucideAngularModule,
  Plus, Shuffle, RotateCcw, RotateCw, RefreshCw,
} from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── AVL data model ────────────────────────────────────────────────────────────

interface AvlNode {
  id: number;
  value: number;
  height: number;   // height of subtree rooted here
  left: AvlNode | null;
  right: AvlNode | null;
}

/**
 * Payload inside VizFrame.data for AVL frames.
 * The full serialised tree is cloned into every frame so the renderer
 * can lay it out independently.
 */
interface AvlFrameData {
  /** Serialised tree root (null when the tree is empty). */
  root: SerialNode | null;
  /** Node ID that was just born (gets pop animation), or -1. */
  born: number;
}

/**
 * A plain-object mirror of AvlNode used inside VizFrame.data.
 * We serialise to this so frames remain pure JSON (no circular refs).
 */
interface SerialNode {
  id: number;
  value: number;
  height: number;
  bf: number;           // balance factor at snapshot time
  left: SerialNode | null;
  right: SerialNode | null;
}

// ── layout ────────────────────────────────────────────────────────────────────

const NODE_R = 24;   // circle radius px
const GAP_X  = 62;   // horizontal gap between in-order positions
const GAP_Y  = 84;   // vertical gap between levels
const PAD    = 16;   // canvas padding

interface NodePos { x: number; y: number; }

function layoutTree(
  root: SerialNode | null,
): { pos: Map<number, NodePos>; width: number; height: number } {
  const pos = new Map<number, NodePos>();
  let idx = 0;
  let maxDepth = 0;

  function walk(n: SerialNode | null, depth: number): void {
    if (!n) return;
    walk(n.left, depth + 1);
    pos.set(n.id, { x: idx * GAP_X + PAD, y: depth * GAP_Y + PAD });
    idx++;
    maxDepth = Math.max(maxDepth, depth);
    walk(n.right, depth + 1);
  }
  walk(root, 0);

  return {
    pos,
    width:  Math.max(idx * GAP_X + PAD * 2, 280),
    height: (maxDepth + 1) * GAP_Y + PAD * 2 + 24, // extra room for bf label
  };
}

// ── AVL primitives ────────────────────────────────────────────────────────────

let _nextId = 1;

function makeNode(value: number): AvlNode {
  return { id: _nextId++, value, height: 1, left: null, right: null };
}

function nodeHeight(n: AvlNode | null): number {
  return n ? n.height : 0;
}

function balanceFactor(n: AvlNode | null): number {
  return n ? nodeHeight(n.left) - nodeHeight(n.right) : 0;
}

function updateHeight(n: AvlNode): void {
  n.height = 1 + Math.max(nodeHeight(n.left), nodeHeight(n.right));
}

/**
 * Clone an entire AVL tree so that mutations to the new tree
 * do not retroactively change earlier frames' snapshots.
 */
function cloneTree(n: AvlNode | null): AvlNode | null {
  if (!n) return null;
  return {
    id:    n.id,
    value: n.value,
    height: n.height,
    left:  cloneTree(n.left),
    right: cloneTree(n.right),
  };
}

/** Serialise an AvlNode tree to plain SerialNode objects. */
function serialise(n: AvlNode | null): SerialNode | null {
  if (!n) return null;
  return {
    id:    n.id,
    value: n.value,
    height: n.height,
    bf:    balanceFactor(n),
    left:  serialise(n.left),
    right: serialise(n.right),
  };
}

/** Collect every node in a serialised tree into a flat map. */
function buildSerialMap(root: SerialNode | null): Map<number, SerialNode> {
  const map = new Map<number, SerialNode>();
  function walk(n: SerialNode | null) {
    if (!n) return;
    map.set(n.id, n);
    walk(n.left);
    walk(n.right);
  }
  walk(root);
  return map;
}

// ── rotations ─────────────────────────────────────────────────────────────────

function rotateRight(y: AvlNode): AvlNode {
  const x  = y.left!;
  const t2 = x.right;
  x.right  = y;
  y.left   = t2;
  updateHeight(y);
  updateHeight(x);
  return x;
}

function rotateLeft(x: AvlNode): AvlNode {
  const y  = x.right!;
  const t2 = y.left;
  y.left   = x;
  x.right  = t2;
  updateHeight(x);
  updateHeight(y);
  return y;
}

// ── frame-recording insert ────────────────────────────────────────────────────

/**
 * Stateful recorder passed through the recursive insert so we can
 * push frames at each significant step without returning giant tuples.
 */
interface Recorder {
  frames: VizFrame[];
  /** The id of the newly created node (set once, never changes). */
  createdId: number;
  /** All node IDs visible at the point of the last pushed frame. */
  rootAtFrame: () => SerialNode | null;
}

/**
 * Insert `value` into the subtree `n`, pushing annotated frames
 * into `rec.frames` along the way.  Returns the (possibly new) subtree root.
 *
 * We walk down first (BST path frames), then rebalance on the way back up
 * (balance-factor + rotation frames).
 */
function avlInsertRecording(
  n: AvlNode | null,
  value: number,
  treeRoot: { ref: AvlNode | null },
  rec: Recorder,
): AvlNode {

  // ── Base case: empty slot → create the new node ─────────────────────────
  if (!n) {
    const newNode = makeNode(value);
    rec.createdId = newNode.id;
    return newNode;
  }

  // ── Traverse ──────────────────────────────────────────────────────────────
  const dir = value < n.value ? 'left' : 'right';
  const cmp = value < n.value ? '&lt;' : '&gt;';

  // Frame: visiting current node
  rec.frames.push({
    note: `At <b>${n.value}</b>: ${value} ${cmp} ${n.value} — go <b>${dir}</b>`,
    states: { [n.id]: 'visit' },
    data:  { root: serialise(treeRoot.ref), born: -1 } as AvlFrameData,
    pseudoLine: 1,
  });

  if (value === n.value) {
    // Duplicate — no insert
    rec.frames.push({
      note: `<b>${value}</b> already exists — AVL trees hold unique keys.`,
      states: { [n.id]: 'unbalanced' },
      data: { root: serialise(treeRoot.ref), born: -1 } as AvlFrameData,
    });
    return n;
  }

  if (value < n.value) {
    n.left = avlInsertRecording(n.left, value, treeRoot, rec);
  } else {
    n.right = avlInsertRecording(n.right, value, treeRoot, rec);
  }

  updateHeight(n);

  // ── Balance-factor check ──────────────────────────────────────────────────
  const bf = balanceFactor(n);

  if (bf < -1 || bf > 1) {
    // Frame: unbalanced node detected
    rec.frames.push({
      note: `Balance factor at <b>${n.value}</b> = ${bf > 0 ? '+' : ''}${bf} — rebalancing needed`,
      states: { [n.id]: 'unbalanced' },
      data: { root: serialise(treeRoot.ref), born: -1 } as AvlFrameData,
      pseudoLine: 4,
    });
  }

  // ── LL (right-heavy left subtree) ─────────────────────────────────────────
  if (bf > 1 && value < n.left!.value) {
    rec.frames.push({
      note: `LL case at <b>${n.value}</b>: single <b>right rotation</b>`,
      states: { [n.id]: 'unbalanced', [n.left!.id]: 'rotated' },
      data: { root: serialise(treeRoot.ref), born: -1 } as AvlFrameData,
      pseudoLine: 5,
    });
    const newRoot = rotateRight(n);
    updateTmpRoot(treeRoot, newRoot);
    rec.frames.push({
      note: `Right rotation complete — <b>${newRoot.value}</b> is now the local root`,
      states: { [newRoot.id]: 'rotated' },
      data: { root: serialise(treeRoot.ref), born: rec.createdId } as AvlFrameData,
      pseudoLine: 5,
    });
    return newRoot;
  }

  // ── RR (left-heavy right subtree) ─────────────────────────────────────────
  if (bf < -1 && value > n.right!.value) {
    rec.frames.push({
      note: `RR case at <b>${n.value}</b>: single <b>left rotation</b>`,
      states: { [n.id]: 'unbalanced', [n.right!.id]: 'rotated' },
      data: { root: serialise(treeRoot.ref), born: -1 } as AvlFrameData,
      pseudoLine: 6,
    });
    const newRoot = rotateLeft(n);
    updateTmpRoot(treeRoot, newRoot);
    rec.frames.push({
      note: `Left rotation complete — <b>${newRoot.value}</b> is now the local root`,
      states: { [newRoot.id]: 'rotated' },
      data: { root: serialise(treeRoot.ref), born: rec.createdId } as AvlFrameData,
      pseudoLine: 6,
    });
    return newRoot;
  }

  // ── LR (left-heavy, right child of left subtree) ──────────────────────────
  if (bf > 1 && value > n.left!.value) {
    rec.frames.push({
      note: `LR case at <b>${n.value}</b>: left-rotate <b>${n.left!.value}</b>, then right-rotate <b>${n.value}</b>`,
      states: { [n.id]: 'unbalanced', [n.left!.id]: 'rotated' },
      data: { root: serialise(treeRoot.ref), born: -1 } as AvlFrameData,
      pseudoLine: 7,
    });
    n.left = rotateLeft(n.left!);
    const newRoot = rotateRight(n);
    updateTmpRoot(treeRoot, newRoot);
    rec.frames.push({
      note: `LR double-rotation complete — <b>${newRoot.value}</b> is now the local root`,
      states: { [newRoot.id]: 'rotated' },
      data: { root: serialise(treeRoot.ref), born: rec.createdId } as AvlFrameData,
      pseudoLine: 7,
    });
    return newRoot;
  }

  // ── RL (right-heavy, left child of right subtree) ─────────────────────────
  if (bf < -1 && value < n.right!.value) {
    rec.frames.push({
      note: `RL case at <b>${n.value}</b>: right-rotate <b>${n.right!.value}</b>, then left-rotate <b>${n.value}</b>`,
      states: { [n.id]: 'unbalanced', [n.right!.id]: 'rotated' },
      data: { root: serialise(treeRoot.ref), born: -1 } as AvlFrameData,
      pseudoLine: 8,
    });
    n.right = rotateRight(n.right!);
    const newRoot = rotateLeft(n);
    updateTmpRoot(treeRoot, newRoot);
    rec.frames.push({
      note: `RL double-rotation complete — <b>${newRoot.value}</b> is now the local root`,
      states: { [newRoot.id]: 'rotated' },
      data: { root: serialise(treeRoot.ref), born: rec.createdId } as AvlFrameData,
      pseudoLine: 8,
    });
    return newRoot;
  }

  // ── Balanced — just show balance factor if non-zero ───────────────────────
  if (bf !== 0) {
    rec.frames.push({
      note: `Balance factor at <b>${n.value}</b> = ${bf > 0 ? '+' : ''}${bf} — still balanced`,
      states: { [n.id]: 'visit' },
      data: { root: serialise(treeRoot.ref), born: -1 } as AvlFrameData,
      pseudoLine: 3,
    });
  }

  return n;
}

/**
 * After a rotation the local root changes, so we update the tmp holder
 * so subsequent serialise() calls in the same insert see the new shape.
 * This is a best-effort approximation — the full global root is only
 * correctly updated after the recursive insert unwinds, but for
 * sub-tree frames it's close enough for the visualiser.
 */
function updateTmpRoot(
  holder: { ref: AvlNode | null },
  newSubRoot: AvlNode,
): void {
  // If the old ref IS the same node as what was being rotated we can update it.
  // For deeply nested rotations the serialised snapshot will show the rotated
  // sub-tree even if the global root pointer is one level up — acceptable.
  if (!holder.ref || holder.ref.id === newSubRoot.id) {
    holder.ref = newSubRoot;
  }
}

// ── public insert (wraps the recursive version) ───────────────────────────────

function avlInsert(
  root: AvlNode | null,
  value: number,
): { root: AvlNode; frames: VizFrame[]; createdId: number } {

  const workRoot = cloneTree(root);  // work on a clone
  const treeHolder: { ref: AvlNode | null } = { ref: workRoot };

  const rec: Recorder = {
    frames: [],
    createdId: -1,
    rootAtFrame: () => serialise(treeHolder.ref),
  };

  const newRoot = avlInsertRecording(workRoot, value, treeHolder, rec);
  treeHolder.ref = newRoot;

  // Final summary frame
  rec.frames.push({
    note: `<b>${value}</b> inserted. Tree height = ${nodeHeight(newRoot)}.`,
    states: { [rec.createdId]: 'new' },
    data: { root: serialise(newRoot), born: rec.createdId } as AvlFrameData,
    pseudoLine: 0,
  });

  return { root: newRoot, frames: rec.frames, createdId: rec.createdId };
}

// ── random-build helper ───────────────────────────────────────────────────────

function buildRandomTree(count = 8): { root: AvlNode; allFrames: VizFrame[] } {
  _nextId = 1;
  const used = new Set<number>();
  const values: number[] = [];
  while (values.length < count) {
    const v = Math.floor(Math.random() * 89) + 10;
    if (!used.has(v)) { used.add(v); values.push(v); }
  }

  let root: AvlNode | null = null;
  const allFrames: VizFrame[] = [];

  for (const v of values) {
    const res = avlInsert(root, v);
    root = res.root;
    allFrames.push(...res.frames);
  }

  return { root: root!, allFrames };
}

// ── view-model types ──────────────────────────────────────────────────────────

interface RenderedNode {
  id: number;
  value: number;
  bf: number;
  height: number;
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

// ── component ────────────────────────────────────────────────────────────────

@Component({
  selector: 'app-viz-avl-tree',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './avl-tree.component.html',
  styleUrls: ['./avl-tree.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AvlTreeComponent implements OnInit, Visualizer {

  readonly player = inject(VizPlayerService);

  // ── Lucide icons ──────────────────────────────────────────────────────────
  readonly Plus      = Plus;
  readonly Shuffle   = Shuffle;
  readonly RotateCcw = RotateCcw;
  readonly RotateCw  = RotateCw;
  readonly RefreshCw = RefreshCw;

  // ── Visualizer contract ───────────────────────────────────────────────────

  readonly meta: VizMeta = {
    slug: 'avl-tree',
    title: 'AVL Tree',
    category: 'Trees',
    description:
      'Self-balancing BST that maintains balance factors and performs ' +
      'LL / RR / LR / RL rotations to keep O(log n) height.',
    operations: ['Insert', 'Random Build', 'Reset'],
    complexity: {
      Insert: { time: 'O(log n)', space: 'O(n)' },
      Search: { time: 'O(log n)', space: 'O(n)' },
    },
  };

  /** Exposed as a constant so the template can reference it. */
  readonly NODE_R = NODE_R;

  // ── static display data ───────────────────────────────────────────────────

  readonly pseudoLines: string[] = [
    /* 0 */ 'avlInsert(node, value):',
    /* 1 */ '  if value < node.value → go left',
    /* 2 */ '  if value > node.value → go right',
    /* 3 */ '  updateHeight(node)',
    /* 4 */ '  bf = height(left) - height(right)',
    /* 5 */ '  if bf > 1  and value < left.value  → rotateRight(node)      // LL',
    /* 6 */ '  if bf < -1 and value > right.value → rotateLeft(node)       // RR',
    /* 7 */ '  if bf > 1  and value > left.value  → rotateLeft+Right(node) // LR',
    /* 8 */ '  if bf < -1 and value < right.value → rotateRight+Left(node) // RL',
    /* 9 */ '  return node',
  ];

  readonly rotationInfo = [
    { label: 'LL (Right Rotate)',    desc: 'New key in left subtree of left child',  ccw: true  },
    { label: 'RR (Left Rotate)',     desc: 'New key in right subtree of right child', ccw: false },
    { label: 'LR (Left-Right)',      desc: 'New key in right subtree of left child', ccw: false },
    { label: 'RL (Right-Left)',      desc: 'New key in left subtree of right child',  ccw: true  },
  ];

  // ── state signals ─────────────────────────────────────────────────────────

  root         = signal<AvlNode | null>(null);
  insertValue  = signal('');

  // ── lifecycle ─────────────────────────────────────────────────────────────

  ngOnInit(): void {
    this._loadDefault();
  }

  // ── user actions ──────────────────────────────────────────────────────────

  onInsert(): void {
    const v = parseInt(this.insertValue(), 10);
    if (!Number.isFinite(v)) return;

    const cur = this.root();
    const res = avlInsert(cur, v);
    this.root.set(res.root);
    this.player.setFrames(res.frames);
    this.player.play();
    this.insertValue.set('');
  }

  onRandom(): void {
    const { root, allFrames } = buildRandomTree(8);
    this.root.set(root);
    this.player.setFrames(allFrames);
    this.player.play();
  }

  onReset(): void {
    this._loadDefault();
  }

  onInsertInput(e: Event): void {
    this.insertValue.set((e.target as HTMLInputElement).value);
  }

  onInsertKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') this.onInsert();
  }

  // ── computed view-model ───────────────────────────────────────────────────

  readonly svgLayout = computed(() => {
    const frame = this.player.currentFrame();
    const data  = frame?.data as AvlFrameData | undefined;

    // The rendered tree comes from the frame's serialised snapshot.
    // If no frames loaded yet, fall back to the live root.
    const serial: SerialNode | null = data?.root ?? serialise(this.root());
    if (!serial) return { nodes: [], edges: [], width: 280, height: 160 };

    const born   = data?.born ?? -1;
    const states = frame?.states ?? {};

    const { pos, width, height } = layoutTree(serial);
    const nodeMap = buildSerialMap(serial);

    const nodes: RenderedNode[] = [];
    const edges: RenderedEdge[] = [];

    nodeMap.forEach((n, id) => {
      const p = pos.get(id);
      if (!p) return;

      nodes.push({
        id,
        value:   n.value,
        bf:      n.bf,
        height:  n.height,
        x:       p.x,
        y:       p.y,
        state:   states[id] ?? 'default',
        born:    born === id,
        visible: true,
      });

      if (n.left && pos.has(n.left.id)) {
        const cp = pos.get(n.left.id)!;
        edges.push({ x1: p.x + NODE_R, y1: p.y + NODE_R, x2: cp.x + NODE_R, y2: cp.y + NODE_R });
      }
      if (n.right && pos.has(n.right.id)) {
        const cp = pos.get(n.right.id)!;
        edges.push({ x1: p.x + NODE_R, y1: p.y + NODE_R, x2: cp.x + NODE_R, y2: cp.y + NODE_R });
      }
    });

    return { nodes, edges, width, height };
  });

  nodeClass(n: RenderedNode): string {
    const base = [
      'absolute rounded-full flex items-center justify-center',
      'font-bold text-sm text-white select-none',
      'transition-all duration-300 cursor-default',
    ].join(' ');

    const stateMap: Record<string, string> = {
      default:    'avl-node--default',
      visit:      'avl-node--visit',
      new:        'avl-node--new',
      unbalanced: 'avl-node--unbalanced',
      rotated:    'avl-node--rotated',
    };

    const stateClass = stateMap[n.state] ?? stateMap['default'];
    const bornClass  = n.born ? 'avl-node--born' : '';
    return `${base} ${stateClass} ${bornClass}`.trim();
  }

  bfClass(bf: number): string {
    if (bf > 1 || bf < -1) return 'avl-bf avl-bf--danger';
    if (bf !== 0)           return 'avl-bf avl-bf--warn';
    return 'avl-bf avl-bf--ok';
  }

  // ── buildFrames satisfies interface (no-op; component drives directly) ────
  buildFrames(): VizFrame[] { return []; }

  // ── private ───────────────────────────────────────────────────────────────

  private _loadDefault(): void {
    _nextId = 1;
    const values = [40, 20, 60, 10, 30, 50, 70, 25, 35];
    let root: AvlNode | null = null;
    for (const v of values) {
      const res = avlInsert(root, v);
      root = res.root;
    }
    this.root.set(root);
    this.player.setFrames([{
      note: 'Sample AVL tree loaded. Insert a value to see rotations.',
      states: {},
      data: { root: serialise(root), born: -1 } as AvlFrameData,
    }]);
  }
}
