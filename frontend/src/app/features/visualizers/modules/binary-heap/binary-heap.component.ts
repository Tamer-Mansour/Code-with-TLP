import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, Plus, Trash2, Shuffle, RotateCcw } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── constants ────────────────────────────────────────────────────────────────

const NODE_R  = 24;   // circle radius in px
const GAP_Y   = 88;   // vertical gap between levels
const PAD     = 20;   // canvas padding

// ── types ────────────────────────────────────────────────────────────────────

/** State token for a single heap slot across one frame. */
type HeapSlotState = 'default' | 'active' | 'compare' | 'swap' | 'done' | 'removed';

/** Payload carried in every VizFrame.data for this module. */
interface HeapFrameData {
  /** Current heap array at this step (length is the live heap size). */
  heap: number[];
}

/** View-model for one SVG node. */
interface RenderedNode {
  /** 0-based heap index. */
  idx: number;
  value: number;
  cx: number;
  cy: number;
  state: HeapSlotState;
}

/** View-model for one SVG edge (parent → child). */
interface RenderedEdge {
  x1: number; y1: number;
  x2: number; y2: number;
}

/** View-model for one cell in the backing-array row. */
interface ArrayCell {
  idx: number;
  value: number;
  state: HeapSlotState;
}

// ── layout helpers ───────────────────────────────────────────────────────────

/**
 * Compute (cx, cy) for each node in a complete binary tree stored in an array.
 *
 * At depth d the row contains 2^d nodes, evenly distributed across the full
 * canvas width.  The width is sized so that the leaf row has adequate spacing.
 */
function layoutHeap(
  n: number,
  canvasWidth: number,
): Map<number, { cx: number; cy: number }> {
  const pos = new Map<number, { cx: number; cy: number }>();
  if (n === 0) return pos;

  // depth of the deepest level that has nodes
  const maxDepth = Math.floor(Math.log2(n));
  const leafCount = Math.pow(2, maxDepth);
  const effectiveWidth = Math.max(canvasWidth, leafCount * (NODE_R * 2 + 16) + PAD * 2);

  for (let i = 0; i < n; i++) {
    const depth = Math.floor(Math.log2(i + 1));
    const posInRow = i + 1 - Math.pow(2, depth); // 0-based position within row
    const rowCount = Math.pow(2, depth);
    const cx = ((posInRow + 0.5) / rowCount) * effectiveWidth;
    const cy = depth * GAP_Y + PAD + NODE_R;
    pos.set(i, { cx, cy });
  }

  return pos;
}

// ── pure frame-builder helpers ───────────────────────────────────────────────

function snap(
  heap: number[],
  states: Record<number, HeapSlotState>,
  note: string,
  pseudoLine?: number,
): VizFrame {
  return {
    note,
    pseudoLine,
    states: Object.fromEntries(
      Object.entries(states).map(([k, v]) => [String(k), v])
    ),
    data: { heap: heap.slice() } as HeapFrameData,
  };
}

// ── Insert (sift-up) ─────────────────────────────────────────────────────────

function buildInsert(initialHeap: number[], value: number): VizFrame[] {
  const fs: VizFrame[] = [];
  const h = initialHeap.slice();
  h.push(value);
  let i = h.length - 1;

  fs.push(snap(
    h, { [i]: 'active' },
    `Insert <b>${value}</b> at index ${i} (last position).`,
    0,
  ));

  while (i > 0) {
    const parent = Math.floor((i - 1) / 2);
    fs.push(snap(
      h, { [i]: 'compare', [parent]: 'compare' },
      `Compare child <b>${h[i]}</b> (idx ${i}) with parent <b>${h[parent]}</b> (idx ${parent}).`,
      1,
    ));

    if (h[i] > h[parent]) {
      [h[i], h[parent]] = [h[parent], h[i]];
      fs.push(snap(
        h, { [i]: 'swap', [parent]: 'swap' },
        `<b>${h[parent]}</b> &gt; <b>${h[i]}</b> — swap! New position: ${parent}.`,
        2,
      ));
      i = parent;
    } else {
      fs.push(snap(
        h, { [i]: 'done' },
        `<b>${h[i]}</b> &le; parent <b>${h[parent]}</b> — heap property holds. Done.`,
        3,
      ));
      break;
    }
  }

  if (i === 0) {
    fs.push(snap(h, { [0]: 'done' }, `<b>${h[0]}</b> reached the root. Insertion complete.`, 3));
  }

  fs.push(snap(h, {}, `Heap after inserting <b>${value}</b>: [${h.join(', ')}].`));
  return fs;
}

// ── Extract-Max (sift-down) ──────────────────────────────────────────────────

function buildExtractMax(initialHeap: number[]): VizFrame[] {
  const fs: VizFrame[] = [];
  const h = initialHeap.slice();

  if (h.length === 0) {
    fs.push(snap(h, {}, 'Heap is empty — nothing to extract.'));
    return fs;
  }

  const maxVal = h[0];
  fs.push(snap(h, { [0]: 'active' }, `Extract max: root is <b>${maxVal}</b>.`, 5));

  // swap root with last
  const last = h.length - 1;
  [h[0], h[last]] = [h[last], h[0]];
  fs.push(snap(
    h, { [0]: 'swap', [last]: 'swap' },
    `Swap root <b>${maxVal}</b> with last element <b>${h[last]}</b> (idx ${last}).`,
    6,
  ));

  h.pop();
  fs.push(snap(
    h, {},
    `Remove <b>${maxVal}</b> from the end. Heap size: ${h.length}. Now sift-down the new root.`,
    6,
  ));

  // sift-down
  let i = 0;
  while (true) {
    const l = 2 * i + 1;
    const r = 2 * i + 2;
    let largest = i;

    if (l < h.length) {
      fs.push(snap(
        h, { [i]: 'compare', [l]: 'compare' },
        `Compare <b>${h[i]}</b> with left child <b>${h[l]}</b>.`,
        8,
      ));
      if (h[l] > h[largest]) largest = l;
    }

    if (r < h.length) {
      fs.push(snap(
        h, { [largest]: 'compare', [r]: 'compare' },
        `Compare current largest <b>${h[largest]}</b> with right child <b>${h[r]}</b>.`,
        9,
      ));
      if (h[r] > h[largest]) largest = r;
    }

    if (largest === i) {
      fs.push(snap(
        h, { [i]: 'done' },
        `<b>${h[i]}</b> is the largest among its children — max-heap property satisfied.`,
        10,
      ));
      break;
    }

    fs.push(snap(
      h, { [i]: 'swap', [largest]: 'swap' },
      `<b>${h[largest]}</b> &gt; <b>${h[i]}</b> — swap! <b>${h[i]}</b> moves down to index ${largest}.`,
      11,
    ));
    [h[i], h[largest]] = [h[largest], h[i]];
    i = largest;
  }

  fs.push(snap(h, {}, `Extract-Max complete. Removed <b>${maxVal}</b>. Heap: [${h.join(', ')}].`));
  return fs;
}

// ── Build-Heap (Floyd heapify) ───────────────────────────────────────────────

function siftDownMut(
  h: number[],
  i: number,
  n: number,
  fs: VizFrame[],
): void {
  while (true) {
    const l = 2 * i + 1;
    const r = 2 * i + 2;
    let largest = i;

    if (l < n && h[l] > h[largest]) largest = l;
    if (r < n && h[r] > h[largest]) largest = r;

    if (largest === i) {
      fs.push(snap(
        h.slice(0, n), { [i]: 'done' },
        `Node <b>${h[i]}</b> at index ${i} is already the largest among its children.`,
        13,
      ));
      break;
    }

    fs.push(snap(
      h.slice(0, n), { [i]: 'compare', [largest]: 'compare' },
      `Sift-down: <b>${h[largest]}</b> &gt; <b>${h[i]}</b> — swap indices ${i} and ${largest}.`,
      14,
    ));
    [h[i], h[largest]] = [h[largest], h[i]];
    fs.push(snap(
      h.slice(0, n), { [i]: 'swap', [largest]: 'swap' },
      `Swapped: <b>${h[i]}</b> now at ${largest}, <b>${h[largest]}</b> at ${i}.`,
      14,
    ));
    i = largest;
  }
}

function buildHeapify(inputArray: number[]): VizFrame[] {
  const fs: VizFrame[] = [];
  const h = inputArray.slice();
  const n = h.length;

  fs.push(snap(
    h, {},
    `Build-Heap on [${h.join(', ')}] using Floyd's heapify (O(n) bottom-up sift-down).`,
    12,
  ));

  const start = Math.floor(n / 2) - 1;
  for (let i = start; i >= 0; i--) {
    fs.push(snap(
      h, { [i]: 'active' },
      `Sift-down from index ${i} (value <b>${h[i]}</b>).`,
      13,
    ));
    siftDownMut(h, i, n, fs);
  }

  fs.push(snap(h, {}, `Build-Heap complete. Max-heap: [${h.join(', ')}]. Root (max) = <b>${h[0]}</b>.`));
  return fs;
}

// ── pseudo-code lines ────────────────────────────────────────────────────────

const PSEUDO_LINES: string[] = [
  /* 0  */ 'Insert(val): append val to end of heap',
  /* 1  */ '  while i > 0 and heap[parent(i)] < heap[i]:',
  /* 2  */ '    swap(heap[i], heap[parent(i)])',
  /* 3  */ '    i = parent(i)  // or stop if ≤',
  /* 4  */ '',
  /* 5  */ 'ExtractMax(): root ← heap[0]',
  /* 6  */ '  heap[0] ← heap[last]; remove last',
  /* 7  */ '  SiftDown(0)',
  /* 8  */ '  SiftDown: largest ← i',
  /* 9  */ '    if left < n and heap[left] > heap[largest]',
  /* 10 */ '    if right < n and heap[right] > heap[largest]',
  /* 11 */ '    if largest ≠ i: swap, i ← largest; repeat',
  /* 12 */ '',
  /* 13 */ 'BuildHeap: for i = ⌊n/2⌋-1 downto 0:',
  /* 14 */ '  SiftDown(i)',
];

// ── random helpers ────────────────────────────────────────────────────────────

function randInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function makeRandomHeap(size = 7): number[] {
  const arr = Array.from({ length: size }, () => randInt(1, 99));
  // heapify in-place (no animation) to produce a valid max-heap
  for (let i = Math.floor(size / 2) - 1; i >= 0; i--) {
    let j = i;
    while (true) {
      const l = 2 * j + 1, r = 2 * j + 2;
      let lg = j;
      if (l < size && arr[l] > arr[lg]) lg = l;
      if (r < size && arr[r] > arr[lg]) lg = r;
      if (lg === j) break;
      [arr[j], arr[lg]] = [arr[lg], arr[j]];
      j = lg;
    }
  }
  return arr;
}

// ── component ────────────────────────────────────────────────────────────────

@Component({
  selector: 'app-viz-binary-heap',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './binary-heap.component.html',
  styleUrls: ['./binary-heap.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BinaryHeapComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  // ── lucide icon references ────────────────────────────────────────────────
  readonly Plus     = Plus;
  readonly Trash2   = Trash2;
  readonly Shuffle  = Shuffle;
  readonly RotateCcw = RotateCcw;

  // ── static metadata ───────────────────────────────────────────────────────
  readonly meta: VizMeta = {
    slug: 'binary-heap',
    title: 'Binary Max-Heap',
    category: 'Trees',
    description: 'Visualize Insert (sift-up), Extract-Max (sift-down), and Build-Heap (Floyd heapify) on a max-priority queue.',
    operations: ['Insert', 'Extract-Max', 'Build-Heap'],
    complexity: {
      'Insert':       { time: 'O(log n)', space: 'O(1)' },
      'Extract-Max':  { time: 'O(log n)', space: 'O(1)' },
      'Build-Heap':   { time: 'O(n)',     space: 'O(1)' },
    },
  };

  // ── exposed constants for template ───────────────────────────────────────
  readonly NODE_R = NODE_R;
  readonly PSEUDO = PSEUDO_LINES;

  // ── reactive state ────────────────────────────────────────────────────────
  readonly heap        = signal<number[]>([]);
  readonly insertValue = signal('');
  readonly buildInput  = signal('');

  readonly SVG_W = 720; // fixed canvas width; nodes reflow inside

  // ── lifecycle ─────────────────────────────────────────────────────────────
  ngOnInit(): void {
    const initial = makeRandomHeap(7);
    this.heap.set(initial);
    this._loadInitialFrame(initial);
  }

  // ── user actions ──────────────────────────────────────────────────────────
  onInsert(): void {
    const v = parseInt(this.insertValue(), 10);
    if (!Number.isFinite(v) || v < 1 || v > 999) return;

    const before = this.heap();
    const frames = buildInsert(before, v);
    // Update persistent heap to the final state produced by the builder
    const finalData = frames[frames.length - 1]?.data as HeapFrameData | undefined;
    if (finalData) this.heap.set(finalData.heap.slice());

    this.player.setFrames(frames);
    this.player.play();
    this.insertValue.set('');
  }

  onExtractMax(): void {
    const before = this.heap();
    if (before.length === 0) return;

    const frames = buildExtractMax(before);
    const finalData = frames[frames.length - 1]?.data as HeapFrameData | undefined;
    if (finalData) this.heap.set(finalData.heap.slice());

    this.player.setFrames(frames);
    this.player.play();
  }

  onBuildHeap(): void {
    const raw = this.buildInput().trim();
    let arr: number[];

    if (raw) {
      arr = raw.split(/[\s,]+/)
               .map(s => parseInt(s, 10))
               .filter(n => Number.isFinite(n) && n >= 1 && n <= 999)
               .slice(0, 15);
      if (arr.length === 0) return;
    } else {
      // build from a fresh random unsorted array
      arr = Array.from({ length: 7 }, () => randInt(1, 99));
    }

    const frames = buildHeapify(arr);
    const finalData = frames[frames.length - 1]?.data as HeapFrameData | undefined;
    if (finalData) this.heap.set(finalData.heap.slice());

    this.player.setFrames(frames);
    this.player.play();
    this.buildInput.set('');
  }

  onRandomHeap(): void {
    const arr = Array.from({ length: 7 }, () => randInt(1, 99));
    const frames = buildHeapify(arr);
    const finalData = frames[frames.length - 1]?.data as HeapFrameData | undefined;
    if (finalData) this.heap.set(finalData.heap.slice());

    this.player.setFrames(frames);
    this.player.play();
  }

  onReset(): void {
    const initial = makeRandomHeap(7);
    this.heap.set(initial);
    this.insertValue.set('');
    this.buildInput.set('');
    this._loadInitialFrame(initial);
  }

  onInsertInput(e: Event): void {
    this.insertValue.set((e.target as HTMLInputElement).value);
  }

  onInsertKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') this.onInsert();
  }

  onBuildInput(e: Event): void {
    this.buildInput.set((e.target as HTMLInputElement).value);
  }

  onBuildKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') this.onBuildHeap();
  }

  // ── computed SVG layout ───────────────────────────────────────────────────

  readonly svgLayout = computed(() => {
    const frame   = this.player.currentFrame();
    const heap    = (frame?.data as HeapFrameData | undefined)?.heap ?? this.heap();
    const states  = frame?.states ?? {};
    const n       = heap.length;

    if (n === 0) return { nodes: [], edges: [], width: this.SVG_W, height: NODE_R * 2 + PAD * 2 };

    const pos = layoutHeap(n, this.SVG_W);

    // Compute actual canvas width/height from node positions
    let maxCx = 0, maxCy = 0;
    pos.forEach(({ cx, cy }) => {
      if (cx > maxCx) maxCx = cx;
      if (cy > maxCy) maxCy = cy;
    });
    const width  = Math.max(maxCx + NODE_R + PAD, this.SVG_W);
    const height = maxCy + NODE_R + PAD;

    const nodes: RenderedNode[] = heap.map((value, idx) => {
      const { cx, cy } = pos.get(idx)!;
      return {
        idx,
        value,
        cx,
        cy,
        state: (states[String(idx)] as HeapSlotState | undefined) ?? 'default',
      };
    });

    const edges: RenderedEdge[] = [];
    for (let i = 1; i < n; i++) {
      const p  = Math.floor((i - 1) / 2);
      const cp = pos.get(i)!;
      const pp = pos.get(p)!;
      edges.push({ x1: pp.cx, y1: pp.cy, x2: cp.cx, y2: cp.cy });
    }

    return { nodes, edges, width, height };
  });

  // ── computed array row ────────────────────────────────────────────────────

  readonly arrayCells = computed((): ArrayCell[] => {
    const frame  = this.player.currentFrame();
    const heap   = (frame?.data as HeapFrameData | undefined)?.heap ?? this.heap();
    const states = frame?.states ?? {};
    return heap.map((value, idx) => ({
      idx,
      value,
      state: (states[String(idx)] as HeapSlotState | undefined) ?? 'default',
    }));
  });

  // ── highlighted pseudo line ───────────────────────────────────────────────

  readonly activePseudoLine = computed(() => this.player.currentFrame()?.pseudoLine ?? -1);

  // ── note HTML ─────────────────────────────────────────────────────────────

  readonly noteHtml = computed(() => this.player.currentFrame()?.note ?? '');

  // ── buildFrames (satisfies Visualizer interface) ──────────────────────────

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const op    = (input['operation'] as string) ?? 'Insert';
    const value = input['value'] as number | undefined;
    const array = input['array'] as number[] | undefined;
    switch (op) {
      case 'Insert':      return buildInsert(this.heap(), value ?? 50);
      case 'Extract-Max': return buildExtractMax(this.heap());
      case 'Build-Heap':  return buildHeapify(array ?? this.heap());
      default:            return buildInsert(this.heap(), value ?? 50);
    }
  }

  // ── node color class ──────────────────────────────────────────────────────

  nodeCircleClass(state: HeapSlotState): string {
    const base = 'heap-node-circle';
    return `${base} heap-node--${state}`;
  }

  cellClass(state: HeapSlotState): string {
    return `heap-cell heap-cell--${state} w-10 h-10 flex items-center justify-center rounded-lg text-sm font-bold transition-all duration-300`;
  }

  // ── private ───────────────────────────────────────────────────────────────

  private _loadInitialFrame(heap: number[]): void {
    this.player.setFrames([{
      note: `Max-heap loaded. Root = <b>${heap[0] ?? '—'}</b>. Try Insert, Extract-Max, or Build-Heap.`,
      states: {},
      data: { heap: heap.slice() } as HeapFrameData,
    }]);
  }
}
