import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
  NgZone,
} from '@angular/core';
import { NgStyle } from '@angular/common';
import { LucideAngularModule, Shuffle } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── types ────────────────────────────────────────────────────────────────

/** Payload stored in VizFrame.data for each array frame. */
interface ArrayFrameData {
  /** Display order: array of original IDs in the current visual positions. */
  order: number[];
}

/** A tracked bar item. */
interface BarItem {
  id: number;
  value: number;
}

// ── frame builders (pure, no side-effects) ───────────────────────────────

function rand(a: number, b: number): number {
  return Math.floor(Math.random() * (b - a + 1)) + a;
}

function generateArray(n = 12): BarItem[] {
  return Array.from({ length: n }, (_, i) => ({ id: i, value: rand(8, 99) }));
}

function buildBubble(items: BarItem[]): VizFrame[] {
  const work = items.slice();
  const fs: VizFrame[] = [];
  const sorted: Record<string, string> = {};
  const n = work.length;

  const push = (states: Record<string, string>, note: string, pLine?: number) =>
    fs.push({
      note,
      pseudoLine: pLine,
      states: { ...sorted, ...states },
      data: { order: work.map(b => b.id) } as ArrayFrameData,
    });

  push({}, 'Initial array.', 0);

  for (let i = 0; i < n - 1; i++) {
    push({}, `Pass ${i + 1}: bubble largest unsorted element to position ${n - 1 - i}`, 1);
    for (let j = 0; j < n - 1 - i; j++) {
      push(
        { [work[j].id]: 'compare', [work[j + 1].id]: 'compare' },
        `Compare <b>${work[j].value}</b> and <b>${work[j + 1].value}</b>`,
        3
      );
      if (work[j].value > work[j + 1].value) {
        [work[j], work[j + 1]] = [work[j + 1], work[j]];
        push(
          { [work[j].id]: 'swap', [work[j + 1].id]: 'swap' },
          `Out of order — swap <b>${work[j].value}</b> and <b>${work[j + 1].value}</b>`,
          4
        );
      }
    }
    sorted[work[n - 1 - i].id] = 'sorted';
    push({}, `<b>${work[n - 1 - i].value}</b> is in its final position`, 1);
  }

  sorted[work[0].id] = 'sorted';
  push({}, 'Array fully sorted.', 0);
  return fs;
}

function buildSelection(items: BarItem[]): VizFrame[] {
  const work = items.slice();
  const fs: VizFrame[] = [];
  const sorted: Record<string, string> = {};
  const n = work.length;

  const push = (states: Record<string, string>, note: string, pLine?: number) =>
    fs.push({
      note,
      pseudoLine: pLine,
      states: { ...sorted, ...states },
      data: { order: work.map(b => b.id) } as ArrayFrameData,
    });

  push({}, 'Initial array.', 7);

  for (let i = 0; i < n - 1; i++) {
    let minIdx = i;
    push({ [work[i].id]: 'active' }, `Find smallest from index ${i}`, 9);
    for (let j = i + 1; j < n; j++) {
      push(
        { [work[minIdx].id]: 'active', [work[j].id]: 'compare' },
        `Is <b>${work[j].value}</b> &lt; <b>${work[minIdx].value}</b>?`,
        10
      );
      if (work[j].value < work[minIdx].value) minIdx = j;
    }
    if (minIdx !== i) {
      [work[i], work[minIdx]] = [work[minIdx], work[i]];
    }
    push({ [work[i].id]: 'swap' }, `Minimum is <b>${work[i].value}</b> — place at index ${i}`, 12);
    sorted[work[i].id] = 'sorted';
  }

  sorted[work[n - 1].id] = 'sorted';
  push({}, 'Array fully sorted.', 7);
  return fs;
}

function buildInsertion(items: BarItem[]): VizFrame[] {
  const work = items.slice();
  const fs: VizFrame[] = [];
  const sorted: Record<string, string> = {};
  const n = work.length;

  const push = (states: Record<string, string>, note: string, pLine?: number) =>
    fs.push({
      note,
      pseudoLine: pLine,
      states: { ...sorted, ...states },
      data: { order: work.map(b => b.id) } as ArrayFrameData,
    });

  sorted[work[0].id] = 'sorted';
  push({}, 'First element forms a sorted run of size 1', 15);

  for (let i = 1; i < n; i++) {
    const key = work[i].value;
    push({ [work[i].id]: 'active' }, `Insert <b>${key}</b> into the sorted left part`, 16);
    let j = i;
    while (j > 0 && work[j - 1].value > work[j].value) {
      push(
        { [work[j - 1].id]: 'compare', [work[j].id]: 'compare' },
        `${work[j - 1].value} &gt; ${key} — shift right`,
        18
      );
      [work[j - 1], work[j]] = [work[j], work[j - 1]];
      push({ [work[j - 1].id]: 'swap', [work[j].id]: 'swap' }, 'Shift', 19);
      j--;
    }
    for (let k = 0; k <= i; k++) sorted[work[k].id] = 'sorted';
    push({}, `Left part sorted up to index ${i}`, 16);
  }

  push({}, 'Array fully sorted.', 15);
  return fs;
}

function buildLinear(items: BarItem[], target: number): VizFrame[] {
  const work = items.slice();
  const fs: VizFrame[] = [];

  const push = (states: Record<string, string>, note: string) =>
    fs.push({
      note,
      states,
      data: { order: work.map(b => b.id) } as ArrayFrameData,
    });

  push({}, `Linear search for <b>${target}</b>`);

  let found = -1;
  for (let i = 0; i < work.length; i++) {
    push({ [work[i].id]: 'active' }, `Check index ${i}: is <b>${work[i].value}</b> = ${target}?`);
    if (work[i].value === target) {
      found = i;
      break;
    }
  }

  if (found >= 0) {
    push({ [work[found].id]: 'found' }, `Found <b>${target}</b> at index ${found}`);
  } else {
    push({}, `<b>${target}</b> is not in the array`);
  }

  return fs;
}

function buildBinary(items: BarItem[], target: number): VizFrame[] {
  const work = items.slice().sort((a, b) => a.value - b.value);
  const fs: VizFrame[] = [];

  const push = (states: Record<string, string>, note: string) =>
    fs.push({
      note,
      states,
      data: { order: work.map(b => b.id) } as ArrayFrameData,
    });

  push({}, `Binary search needs a sorted array — sorted first. Target = <b>${target}</b>`);

  let lo = 0, hi = work.length - 1, found = -1;

  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const states: Record<string, string> = {};
    work.forEach((it, idx) => {
      states[it.id] = idx < lo || idx > hi ? 'dim' : 'range';
    });
    states[work[mid].id] = 'active';
    push(states, `Range [${lo}, ${hi}] · mid=${mid} → <b>${work[mid].value}</b> vs ${target}`);

    if (work[mid].value === target) {
      found = mid;
      break;
    } else if (work[mid].value < target) {
      lo = mid + 1;
      push(states, `${work[mid].value} &lt; ${target} — search right half`);
    } else {
      hi = mid - 1;
      push(states, `${work[mid].value} &gt; ${target} — search left half`);
    }
  }

  if (found >= 0) {
    push({ [work[found].id]: 'found' }, `Found <b>${target}</b> at index ${found}`);
  } else {
    push({}, `<b>${target}</b> not found in the array`);
  }

  return fs;
}

// ── component ────────────────────────────────────────────────────────────

const OPERATIONS = ['Bubble Sort', 'Selection Sort', 'Insertion Sort', 'Linear Search', 'Binary Search'];

@Component({
  selector: 'app-array-sorting',
  standalone: true,
  imports: [LucideAngularModule, NgStyle],
  templateUrl: './array-sorting.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArraySortingComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);
  private readonly zone   = inject(NgZone);

  readonly Shuffle = Shuffle;

  readonly meta: VizMeta = {
    slug: 'array-sorting',
    title: 'Array Sorting & Search',
    category: 'Sorting',
    description: 'Bubble, Selection, Insertion sort + Linear and Binary search.',
    operations: OPERATIONS,
  };

  readonly CELLW  = 46;
  readonly BARW   = 34;
  readonly MAX_H  = 185;
  readonly BASE_H = 28;
  readonly MAX_VAL = 99;

  readonly operations = OPERATIONS;
  readonly selectedOp = signal('Bubble Sort');
  readonly targetVal  = signal(42);
  readonly showTarget = computed(() => this.selectedOp().includes('Search'));

  items = signal<BarItem[]>([]);

  ngOnInit(): void {
    this.generateArray();
  }

  generateArray(): void {
    const arr = generateArray(12);
    this.items.set(arr);
    this.rebuild(arr);
  }

  selectOp(op: string): void {
    this.selectedOp.set(op);
    this.rebuild(this.items());
  }

  onTargetChange(event: Event): void {
    const v = +(event.target as HTMLInputElement).value;
    this.targetVal.set(Number.isFinite(v) ? v : 42);
    if (this.showTarget()) this.rebuild(this.items());
  }

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const operation = input['operation'] as string ?? 'Bubble Sort';
    const array     = input['array'] as BarItem[] ?? this.items();
    const target    = input['target'] as number ?? 42;
    switch (operation) {
      case 'Bubble Sort':    return buildBubble(array);
      case 'Selection Sort': return buildSelection(array);
      case 'Insertion Sort': return buildInsertion(array);
      case 'Linear Search':  return buildLinear(array, target);
      case 'Binary Search':  return buildBinary(array, target);
      default:               return buildBubble(array);
    }
  }

  private rebuild(arr: BarItem[]): void {
    const frames = this.buildFrames({
      operation: this.selectedOp(),
      array: arr,
      target: this.targetVal(),
    });
    this.player.setFrames(frames);
  }

  // ── view helpers ─────────────────────────────────────────────────────

  /** Given the current frame, compute display positions for each bar. */
  readonly displayBars = computed(() => {
    const frame = this.player.currentFrame();
    const allItems = this.items();
    if (!allItems.length) return [];

    // Build an id->item map
    const byId = new Map(allItems.map(it => [it.id, it]));

    // order from frame data, or natural order
    const order: number[] = (frame?.data as ArrayFrameData | undefined)?.order
      ?? allItems.map(it => it.id);

    const n = order.length;
    // We can't know stage width here — use a CSS transform approach
    // We'll position with percentage-based left offsets or use flex
    return order.map((id, pos) => {
      const it = byId.get(id)!;
      const state = frame?.states?.[id] ?? 'idle';
      const heightPx = this.BASE_H + (it.value / this.MAX_VAL) * this.MAX_H;
      return { id, value: it.value, pos, state, heightPx, n };
    });
  });

  barStateClass(state: string): string {
    const map: Record<string, string> = {
      idle:    'bar-idle',
      compare: 'bar-compare',
      swap:    'bar-swap',
      active:  'bar-active',
      sorted:  'bar-sorted',
      found:   'bar-found',
      dim:     'bar-dim',
      range:   'bar-range',
    };
    return map[state] ?? 'bar-idle';
  }
}
