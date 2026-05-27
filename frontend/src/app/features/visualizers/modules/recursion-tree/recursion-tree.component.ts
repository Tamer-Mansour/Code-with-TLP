import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, RotateCcw, Play, StepForward, StepBack, Pause } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── Data model ────────────────────────────────────────────────────────────

/** Visual state token for a recursion call node. */
type NodeState = 'calling' | 'returning' | 'memo-hit' | 'done' | 'idle';

/** A node in the recursion call tree (used for layout + rendering). */
interface CallNode {
  id: string;
  label: string;
  depth: number;
  parentId: string | null;
  childIds: string[];
  returnValue: number | null;
  x: number;
  y: number;
}

/** Payload stored in VizFrame.data. */
interface RecursionFrameData {
  /** IDs revealed so far (call order). */
  revealed: string[];
  /** Return value labels known at this frame step. */
  returnLabels: Record<string, number>;
}

// ── Layout constants ──────────────────────────────────────────────────────

const NODE_R = 24;
const V_GAP  = 76;
const H_GAP  = 54;
const PAD_X  = 36;
const PAD_Y  = 40;

// ── Tree layout (in-order slot assignment) ────────────────────────────────

function assignPositions(rootId: string, nodes: Map<string, CallNode>): void {
  let slot = 0;

  function walk(id: string): void {
    const n = nodes.get(id);
    if (!n) return;

    const leftIds  = n.childIds.slice(0, Math.ceil(n.childIds.length / 2));
    const rightIds = n.childIds.slice(Math.ceil(n.childIds.length / 2));

    for (const cid of leftIds)  walk(cid);

    n.x = PAD_X + slot * H_GAP;
    n.y = PAD_Y + n.depth * V_GAP;
    slot++;

    for (const cid of rightIds) walk(cid);
  }

  walk(rootId);

  // Centre each internal node over its children
  function centre(id: string): void {
    const n = nodes.get(id);
    if (!n || n.childIds.length === 0) return;
    for (const cid of n.childIds) centre(cid);
    const xs = n.childIds.map(cid => nodes.get(cid)!.x);
    n.x = (Math.min(...xs) + Math.max(...xs)) / 2;
  }

  centre(rootId);
}

// ── Result bundle returned by every frame builder ─────────────────────────

interface BuildResult {
  frames: VizFrame[];
  /** Stable node map for SVG rendering (covers the full final tree). */
  nodeMap: Map<string, CallNode>;
}

// ── Factorial ─────────────────────────────────────────────────────────────

function buildFactorialFrames(n: number): BuildResult {
  const nodes  = new Map<string, CallNode>();
  const frames: VizFrame[] = [];
  const revealed: string[]          = [];
  const returnLabels: Record<string, number> = {};
  let   idCtr = 0;
  let   rootId = '';

  function sim(val: number, parentId: string | null, depth: number): number {
    const id    = `n${idCtr++}`;
    const label = `fact(${val})`;
    if (!rootId) rootId = id;

    nodes.set(id, {
      id, label, depth, parentId,
      childIds: [], returnValue: null, x: 0, y: 0,
    });
    if (parentId) nodes.get(parentId)!.childIds.push(id);
    revealed.push(id);
    assignPositions(rootId, nodes);

    frames.push({
      note: parentId
        ? `<b>${label}</b> called by fact(${val + 1})`
        : `Start: <b>${label}</b>`,
      pseudoLine: 0,
      states: { [id]: 'calling' },
      data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
    });

    let result: number;
    if (val <= 1) {
      result = 1;
      returnLabels[id] = result;
      nodes.get(id)!.returnValue = result;
      assignPositions(rootId, nodes);
      frames.push({
        note: `<b>${label}</b> — base case, returns <b>1</b>`,
        pseudoLine: 1,
        states: { [id]: 'returning' },
        data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
      });
    } else {
      result = val * sim(val - 1, id, depth + 1);
      returnLabels[id] = result;
      nodes.get(id)!.returnValue = result;
      assignPositions(rootId, nodes);
      frames.push({
        note: `<b>${label}</b> = ${val} &times; ${result / val} = <b>${result}</b>`,
        pseudoLine: 2,
        states: { [id]: 'returning' },
        data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
      });
    }

    return result;
  }

  sim(n, null, 0);
  assignPositions(rootId, nodes);

  const doneStates: Record<string, string> = {};
  for (const k of nodes.keys()) doneStates[k] = 'done';
  frames.push({
    note: `<b>fact(${n}) = ${returnLabels[rootId]}</b> — complete`,
    pseudoLine: 0,
    states: doneStates,
    data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
  });

  return { frames, nodeMap: nodes };
}

// ── Fibonacci naive ────────────────────────────────────────────────────────

function buildFibNaiveFrames(n: number): BuildResult {
  const nodes  = new Map<string, CallNode>();
  const frames: VizFrame[] = [];
  const revealed: string[]          = [];
  const returnLabels: Record<string, number> = {};
  let   idCtr  = 0;
  let   rootId = '';

  function sim(val: number, parentId: string | null, depth: number): number {
    const id    = `n${idCtr++}`;
    const label = `fib(${val})`;
    if (!rootId) rootId = id;

    nodes.set(id, {
      id, label, depth, parentId,
      childIds: [], returnValue: null, x: 0, y: 0,
    });
    if (parentId) nodes.get(parentId)!.childIds.push(id);
    revealed.push(id);
    assignPositions(rootId, nodes);

    frames.push({
      note: parentId
        ? `<b>${label}</b> called`
        : `Start: <b>fib(${val})</b> — naive (no memoization)`,
      pseudoLine: val <= 1 ? 1 : 2,
      states: { [id]: 'calling' },
      data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
    });

    let result: number;
    if (val <= 1) {
      result = val;
      returnLabels[id] = result;
      nodes.get(id)!.returnValue = result;
      assignPositions(rootId, nodes);
      frames.push({
        note: `<b>${label}</b> — base case, returns <b>${val}</b>`,
        pseudoLine: 1,
        states: { [id]: 'returning' },
        data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
      });
    } else {
      const left  = sim(val - 1, id, depth + 1);
      const right = sim(val - 2, id, depth + 1);
      result = left + right;
      returnLabels[id] = result;
      nodes.get(id)!.returnValue = result;
      assignPositions(rootId, nodes);
      frames.push({
        note: `<b>${label}</b> = fib(${val - 1}) + fib(${val - 2}) = ${left} + ${right} = <b>${result}</b>`,
        pseudoLine: 3,
        states: { [id]: 'returning' },
        data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
      });
    }

    return result;
  }

  sim(n, null, 0);
  assignPositions(rootId, nodes);

  const doneStates: Record<string, string> = {};
  for (const k of nodes.keys()) doneStates[k] = 'done';
  frames.push({
    note: `<b>fib(${n}) = ${returnLabels[rootId]}</b> — naive used <b>${nodes.size}</b> calls`,
    pseudoLine: 0,
    states: doneStates,
    data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
  });

  return { frames, nodeMap: nodes };
}

// ── Fibonacci memoized ────────────────────────────────────────────────────

function buildFibMemoFrames(n: number): BuildResult {
  const nodes  = new Map<string, CallNode>();
  const frames: VizFrame[] = [];
  const revealed: string[]          = [];
  const returnLabels: Record<string, number> = {};
  const memo   = new Map<number, number>();
  let   idCtr  = 0;
  let   rootId = '';

  function sim(val: number, parentId: string | null, depth: number): number {
    const id    = `n${idCtr++}`;
    const label = `fib(${val})`;
    if (!rootId) rootId = id;

    nodes.set(id, {
      id, label, depth, parentId,
      childIds: [], returnValue: null, x: 0, y: 0,
    });
    if (parentId) nodes.get(parentId)!.childIds.push(id);
    revealed.push(id);
    assignPositions(rootId, nodes);

    // --- Memo hit ---
    if (memo.has(val)) {
      const cached = memo.get(val)!;
      returnLabels[id] = cached;
      nodes.get(id)!.returnValue = cached;
      assignPositions(rootId, nodes);
      frames.push({
        note: `<b>${label}</b> — memo hit! Returns cached <b>${cached}</b>, subtree skipped`,
        pseudoLine: 1,
        states: { [id]: 'memo-hit' },
        data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
      });
      return cached;
    }

    // --- Fresh call ---
    frames.push({
      note: parentId
        ? `<b>${label}</b> called — not in memo yet`
        : `Start: <b>fib(${val})</b> — memoized`,
      pseudoLine: val <= 1 ? 2 : 3,
      states: { [id]: 'calling' },
      data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
    });

    let result: number;
    if (val <= 1) {
      result = val;
      memo.set(val, result);
      returnLabels[id] = result;
      nodes.get(id)!.returnValue = result;
      assignPositions(rootId, nodes);
      frames.push({
        note: `<b>${label}</b> — base case, returns <b>${val}</b>, cached`,
        pseudoLine: 2,
        states: { [id]: 'returning' },
        data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
      });
    } else {
      const left  = sim(val - 1, id, depth + 1);
      const right = sim(val - 2, id, depth + 1);
      result = left + right;
      memo.set(val, result);
      returnLabels[id] = result;
      nodes.get(id)!.returnValue = result;
      assignPositions(rootId, nodes);
      frames.push({
        note: `<b>${label}</b> = ${left} + ${right} = <b>${result}</b> — stored in memo`,
        pseudoLine: 4,
        states: { [id]: 'returning' },
        data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
      });
    }

    return result;
  }

  sim(n, null, 0);
  assignPositions(rootId, nodes);

  const doneStates: Record<string, string> = {};
  for (const k of nodes.keys()) doneStates[k] = 'done';
  frames.push({
    note: `<b>fib(${n}) = ${returnLabels[rootId]}</b> — memoized used only <b>${nodes.size}</b> calls`,
    pseudoLine: 0,
    states: doneStates,
    data: { revealed: [...revealed], returnLabels: { ...returnLabels } } as RecursionFrameData,
  });

  return { frames, nodeMap: nodes };
}

// ── Pseudocode lines ──────────────────────────────────────────────────────

const PSEUDO: Record<string, string[]> = {
  'Factorial(n)': [
    'function fact(n):',
    '  if n <= 1: return 1',
    '  return n * fact(n - 1)',
  ],
  'Fibonacci(n) — naive': [
    'function fib(n):',
    '  if n <= 1: return n',
    '  left  = fib(n - 1)',
    '  right = fib(n - 2)',
    '  return left + right',    // pseudoLine 3 maps here; offset is 0
  ],
  'Fibonacci(n) — memoized': [
    'function fib(n, memo={}):',
    '  if n in memo: return memo[n]',
    '  if n <= 1: return n',
    '  memo[n] = fib(n-1) + fib(n-2)',
    '  return memo[n]',
  ],
};

// ── Operations ────────────────────────────────────────────────────────────

const OPERATIONS = [
  'Factorial(n)',
  'Fibonacci(n) — naive',
  'Fibonacci(n) — memoized',
] as const;
type Operation = typeof OPERATIONS[number];

// ── Component ─────────────────────────────────────────────────────────────

/** Rendered node view-model. */
interface RenderedNode {
  id: string; label: string;
  cx: number; cy: number;
  state: string; returnValue: number | null; visible: boolean;
}

/** Rendered edge view-model. */
interface RenderedEdge {
  x1: number; y1: number; x2: number; y2: number;
}

@Component({
  selector: 'app-viz-recursion-tree',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './recursion-tree.component.html',
  styleUrls: ['./recursion-tree.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RecursionTreeComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  // Lucide icons
  readonly RotateCcw   = RotateCcw;
  readonly Play        = Play;
  readonly StepForward = StepForward;
  readonly StepBack    = StepBack;
  readonly Pause       = Pause;

  // ── meta ──────────────────────────────────────────────────────────────
  readonly meta: VizMeta = {
    slug:        'recursion-tree',
    title:       'Recursion Tree',
    category:    'Recursion & DP',
    description: 'Visualise call trees for Factorial and Fibonacci (naive vs memoized). Observe how memoization prunes duplicate branches.',
    operations:  [...OPERATIONS],
    complexity: {
      'Factorial(n)':            { time: 'O(n)',   space: 'O(n)' },
      'Fibonacci(n) — naive':    { time: 'O(2^n)', space: 'O(n)' },
      'Fibonacci(n) — memoized': { time: 'O(n)',   space: 'O(n)' },
    },
  };

  // ── state ─────────────────────────────────────────────────────────────
  readonly selectedOp = signal<Operation>('Fibonacci(n) — naive');
  readonly nInput     = signal(5);

  /** Stable node map from the most-recently-built animation (as a signal so svgLayout reacts). */
  private readonly _nodeMap = signal(new Map<string, CallNode>());

  // ── n clamp ───────────────────────────────────────────────────────────
  readonly nMax = computed(() =>
    this.selectedOp() === 'Fibonacci(n) — naive' ? 7 : 10,
  );

  private clampN(op: Operation, n: number): number {
    const max = op === 'Fibonacci(n) — naive' ? 7 : 10;
    return Math.max(1, Math.min(max, n));
  }

  // ── pseudocode ────────────────────────────────────────────────────────
  readonly pseudoLines = computed(() => PSEUDO[this.selectedOp()] ?? []);

  readonly activePseudoLine = computed(() => {
    const line = this.player.currentFrame()?.pseudoLine ?? -1;
    return line;
  });

  // ── lifecycle / controls ──────────────────────────────────────────────
  ngOnInit(): void { this._run(); }

  onSelectOp(op: Operation): void {
    this.selectedOp.set(op);
    this.nInput.set(this.clampN(op, this.nInput()));
    this._run();
  }

  onNInput(e: Event): void {
    const v = parseInt((e.target as HTMLInputElement).value, 10);
    if (Number.isFinite(v)) {
      this.nInput.set(this.clampN(this.selectedOp(), v));
    }
  }

  onReset():    void { this._run(); }
  onPlay():     void { this.player.restart(); this.player.play(); }
  onToggle():   void { this.player.toggle(); }
  onStep():     void { this.player.step(); }
  onStepBack(): void { this.player.stepBack(); }

  onSeek(e: Event): void {
    this.player.seek(+(e.target as HTMLInputElement).value);
  }

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const op = (input['operation'] as Operation) ?? 'Fibonacci(n) — naive';
    const n  = (input['value']     as number)    ?? 5;
    const result = this._buildResult(op, n);
    this._nodeMap.set(result.nodeMap);
    return result.frames;
  }

  private _run(): void {
    const op = this.selectedOp();
    const n  = this.clampN(op, this.nInput());
    const result = this._buildResult(op, n);
    this._nodeMap.set(result.nodeMap);
    this.player.setFrames(result.frames);
  }

  private _buildResult(op: Operation, n: number): BuildResult {
    switch (op) {
      case 'Factorial(n)':            return buildFactorialFrames(n);
      case 'Fibonacci(n) — naive':    return buildFibNaiveFrames(n);
      case 'Fibonacci(n) — memoized': return buildFibMemoFrames(n);
      default:                        return buildFibNaiveFrames(n);
    }
  }

  // ── SVG layout (computed signal) ──────────────────────────────────────

  readonly svgLayout = computed(() => {
    const frame    = this.player.currentFrame();
    const nodeMap  = this._nodeMap();

    const empty = { nodes: [] as RenderedNode[], edges: [] as RenderedEdge[], width: 360, height: 200 };
    if (!frame || !nodeMap.size) return empty;

    const frameData  = frame.data as RecursionFrameData | undefined;
    if (!frameData)  return empty;

    const revealed   = new Set(frameData.revealed);
    const retLabels  = frameData.returnLabels ?? {};
    const states     = frame.states ?? {};

    const rNodes: RenderedNode[] = [];
    const rEdges: RenderedEdge[] = [];
    let   maxX = 0, maxY = 0;

    for (const [id, n] of nodeMap) {
      const vis   = revealed.has(id);
      const state = vis ? (states[id] ?? 'idle') : 'idle';
      const retVal = (retLabels[id] !== undefined) ? retLabels[id] : null;

      if (vis) {
        maxX = Math.max(maxX, n.x + NODE_R);
        maxY = Math.max(maxY, n.y + NODE_R);
      }

      rNodes.push({ id, label: n.label, cx: n.x, cy: n.y, state, returnValue: retVal, visible: vis });

      if (vis && n.parentId && revealed.has(n.parentId)) {
        const parent = nodeMap.get(n.parentId);
        if (parent) {
          rEdges.push({ x1: parent.x, y1: parent.y, x2: n.x, y2: n.y });
        }
      }
    }

    return {
      nodes:  rNodes,
      edges:  rEdges,
      width:  Math.max(maxX + PAD_X * 2, 360),
      height: Math.max(maxY + PAD_Y * 2, 200),
    };
  });

  // ── Player shortcuts ──────────────────────────────────────────────────
  readonly currentFrame = computed(() => this.player.currentFrame());
  readonly stepLabel    = computed(() => this.player.stepLabel());
  readonly progress     = computed(() => this.player.progress());
  readonly playing      = computed(() => this.player.playing());
  readonly atStart      = computed(() => this.player.atStart());
  readonly atEnd        = computed(() => this.player.atEnd());
  readonly frameCount   = computed(() => this.player.frames().length);
  readonly frameIndex   = computed(() => this.player.index());

  // ── Template constants ────────────────────────────────────────────────
  readonly NODE_R     = NODE_R;
  readonly OPERATIONS = OPERATIONS;
}
