import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, RotateCcw, Plus, Minus, ArrowRight, ArrowLeft } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── types ────────────────────────────────────────────────────────────────────

/** A single element held in the stack or queue. */
interface SQElement {
  /** Unique ID so @for tracking + states map works correctly. */
  id: number;
  value: number;
}

/** Payload stored in every VizFrame.data for this visualiser. */
interface SQFrameData {
  /** Ordered list of element IDs (top-of-stack = last, front-of-queue = first). */
  order: number[];
  /** The element ID that was just pushed/popped/enqueued/dequeued (may be undefined). */
  activeId?: number;
  /** Current structure type being shown. */
  mode: 'stack' | 'queue';
}

// ── pure frame builders ───────────────────────────────────────────────────────

let _idCounter = 0;
function nextId(): number { return ++_idCounter; }

function pushStack(elements: SQElement[], value: number): VizFrame[] {
  const fs: VizFrame[] = [];
  const work = elements.slice();
  const newEl: SQElement = { id: nextId(), value };

  const snap = (activeId: number | undefined, note: string, extraState?: string): void => {
    const states: Record<string, string> = {};
    if (activeId !== undefined) {
      states[String(activeId)] = extraState ?? 'active';
    }
    fs.push({
      note,
      states,
      data: {
        order: work.map(e => e.id),
        activeId,
        mode: 'stack',
      } as SQFrameData,
    });
  };

  snap(undefined, `Stack (LIFO) — preparing to push <b>${value}</b>.`);
  work.push(newEl);
  snap(newEl.id, `Push <b>${value}</b> onto the top of the stack.`, 'push');
  snap(newEl.id, `<b>${value}</b> is now the top of the stack.`, 'top');

  return fs;
}

function popStack(elements: SQElement[]): VizFrame[] {
  const fs: VizFrame[] = [];
  const work = elements.slice();

  if (!work.length) {
    fs.push({ note: 'Stack is empty — nothing to pop.', states: {}, data: { order: [], mode: 'stack' } as SQFrameData });
    return fs;
  }

  const snap = (activeId: number | undefined, note: string, extraState?: string): void => {
    const states: Record<string, string> = {};
    if (activeId !== undefined) {
      states[String(activeId)] = extraState ?? 'active';
    }
    fs.push({
      note,
      states,
      data: {
        order: work.map(e => e.id),
        activeId,
        mode: 'stack',
      } as SQFrameData,
    });
  };

  const top = work[work.length - 1];
  snap(top.id, `Stack (LIFO) — preparing to pop from top. Top element is <b>${top.value}</b>.`, 'top');
  snap(top.id, `Removing <b>${top.value}</b> from the top.`, 'pop');
  work.pop();
  snap(undefined, `<b>${top.value}</b> has been popped. Stack has ${work.length} element(s).`);

  return fs;
}

function enqueue(elements: SQElement[], value: number): VizFrame[] {
  const fs: VizFrame[] = [];
  const work = elements.slice();
  const newEl: SQElement = { id: nextId(), value };

  const snap = (activeId: number | undefined, note: string, extraState?: string): void => {
    const states: Record<string, string> = {};
    if (activeId !== undefined) {
      states[String(activeId)] = extraState ?? 'active';
    }
    if (work.length > 0) {
      states[String(work[0].id)] = states[String(work[0].id)] ?? 'front';
    }
    fs.push({
      note,
      states,
      data: {
        order: work.map(e => e.id),
        activeId,
        mode: 'queue',
      } as SQFrameData,
    });
  };

  snap(undefined, `Queue (FIFO) — preparing to enqueue <b>${value}</b> at the back.`);
  work.push(newEl);
  snap(newEl.id, `Enqueue <b>${value}</b> at the back of the queue.`, 'push');
  snap(newEl.id, `<b>${value}</b> is now at the back. Front is still <b>${work[0].value}</b>.`, 'back');

  return fs;
}

function dequeue(elements: SQElement[]): VizFrame[] {
  const fs: VizFrame[] = [];
  const work = elements.slice();

  if (!work.length) {
    fs.push({ note: 'Queue is empty — nothing to dequeue.', states: {}, data: { order: [], mode: 'queue' } as SQFrameData });
    return fs;
  }

  const snap = (activeId: number | undefined, note: string, extraState?: string): void => {
    const states: Record<string, string> = {};
    if (activeId !== undefined) {
      states[String(activeId)] = extraState ?? 'active';
    }
    fs.push({
      note,
      states,
      data: {
        order: work.map(e => e.id),
        activeId,
        mode: 'queue',
      } as SQFrameData,
    });
  };

  const front = work[0];
  snap(front.id, `Queue (FIFO) — front element is <b>${front.value}</b>. Preparing to dequeue.`, 'front');
  snap(front.id, `Removing <b>${front.value}</b> from the front.`, 'pop');
  work.shift();
  snap(undefined, `<b>${front.value}</b> has been dequeued. Queue has ${work.length} element(s).`);

  return fs;
}

// ── component ────────────────────────────────────────────────────────────────

const OPERATIONS = ['Stack Push', 'Stack Pop', 'Queue Enqueue', 'Queue Dequeue'];

@Component({
  selector: 'app-viz-stack-queue',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './stack-queue.component.html',
  styleUrls: ['./stack-queue.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StackQueueComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  readonly RotateCcw  = RotateCcw;
  readonly Plus       = Plus;
  readonly Minus      = Minus;
  readonly ArrowRight = ArrowRight;
  readonly ArrowLeft  = ArrowLeft;

  readonly meta: VizMeta = {
    slug: 'stack-queue',
    title: 'Stack & Queue',
    category: 'Linear',
    description: 'Interactive Stack (LIFO) and Queue (FIFO) visualizer with push, pop, enqueue, and dequeue operations.',
    operations: OPERATIONS,
  };

  readonly operations = OPERATIONS;

  /** Currently selected mode — drives which controls are shown. */
  readonly selectedOp = signal<string>('Stack Push');

  /** Value typed by the user for push / enqueue. */
  readonly inputValue = signal<number>(7);

  /** Persistent element lists — survive between operations. */
  private _stackElements = signal<SQElement[]>([]);
  private _queueElements = signal<SQElement[]>([]);

  /** Which sub-mode we're in. */
  readonly mode = computed<'stack' | 'queue'>(() =>
    this.selectedOp().startsWith('Stack') ? 'stack' : 'queue',
  );

  ngOnInit(): void {
    this._loadInitial();
  }

  // ── buildFrames (Visualizer contract) ────────────────────────────────────

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const op    = (input['operation'] as string) ?? 'Stack Push';
    const value = (input['value']     as number)  ?? 7;
    const stack = (input['stack']     as SQElement[]) ?? [];
    const queue = (input['queue']     as SQElement[]) ?? [];

    switch (op) {
      case 'Stack Push':    return pushStack(stack, value);
      case 'Stack Pop':     return popStack(stack);
      case 'Queue Enqueue': return enqueue(queue, value);
      case 'Queue Dequeue': return dequeue(queue);
      default:              return pushStack(stack, value);
    }
  }

  // ── user interactions ─────────────────────────────────────────────────────

  selectOp(op: string): void {
    this.selectedOp.set(op);
  }

  onValueChange(event: Event): void {
    const v = +(event.target as HTMLInputElement).value;
    if (Number.isFinite(v)) this.inputValue.set(v);
  }

  execute(): void {
    const op    = this.selectedOp();
    const value = this.inputValue();

    if (op === 'Stack Push') {
      const frames = pushStack(this._stackElements(), value);
      // Apply the operation to persistent state
      const last = frames[frames.length - 1];
      const data = last.data as SQFrameData;
      const newStack = this._rebuildElements(data.order, this._stackElements());
      this._stackElements.set(newStack);
      this.player.setFrames(frames);

    } else if (op === 'Stack Pop') {
      const frames = popStack(this._stackElements());
      const last = frames[frames.length - 1];
      const data = last.data as SQFrameData;
      this._stackElements.set(this._rebuildElements(data.order, this._stackElements()));
      this.player.setFrames(frames);

    } else if (op === 'Queue Enqueue') {
      const frames = enqueue(this._queueElements(), value);
      const last = frames[frames.length - 1];
      const data = last.data as SQFrameData;
      this._queueElements.set(this._rebuildElements(data.order, this._queueElements()));
      this.player.setFrames(frames);

    } else if (op === 'Queue Dequeue') {
      const frames = dequeue(this._queueElements());
      const last = frames[frames.length - 1];
      const data = last.data as SQFrameData;
      this._queueElements.set(this._rebuildElements(data.order, this._queueElements()));
      this.player.setFrames(frames);
    }
  }

  reset(): void {
    this._stackElements.set([]);
    this._queueElements.set([]);
    this._loadInitial();
  }

  // ── view-model computed from current frame ────────────────────────────────

  readonly displayElements = computed<Array<{
    id: number;
    value: number;
    state: string;
    isTop: boolean;
    isFront: boolean;
    isBack: boolean;
  }>>(() => {
    const frame   = this.player.currentFrame();
    const mode    = this.mode();
    const source  = mode === 'stack' ? this._stackElements() : this._queueElements();

    if (!source.length && !frame) return [];

    const data = frame?.data as SQFrameData | undefined;
    const order = data?.order ?? source.map(e => e.id);

    // Reconstruct from the frame's order — elements added during animation
    // may not yet be in source; use frame snapshot element values when available
    const resolvedOrder = this._mergeOrder(order, source, data);

    return resolvedOrder.map((el, idx) => {
      const rawState = frame?.states?.[String(el.id)] ?? 'idle';
      return {
        id:      el.id,
        value:   el.value,
        state:   rawState,
        isTop:   mode === 'stack' && idx === resolvedOrder.length - 1,
        isFront: mode === 'queue' && idx === 0,
        isBack:  mode === 'queue' && idx === resolvedOrder.length - 1,
      };
    });
  });

  readonly currentNote = computed<string>(() =>
    this.player.currentFrame()?.note ?? '',
  );

  readonly showValueInput = computed<boolean>(() => {
    const op = this.selectedOp();
    return op === 'Stack Push' || op === 'Queue Enqueue';
  });

  // ── helpers ───────────────────────────────────────────────────────────────

  private _loadInitial(): void {
    // Seed stack with a few elements so the visualiser has something to show
    const seed = [3, 7, 12, 5];
    const stackEls = seed.map(v => ({ id: nextId(), value: v }));
    const queueEls = seed.map(v => ({ id: nextId(), value: v }));
    this._stackElements.set(stackEls);
    this._queueElements.set(queueEls);

    // Build initial "idle" frames
    const initFrames: VizFrame[] = [
      {
        note: 'Stack (LIFO): top is on the right. Select an operation and press Execute.',
        states: {},
        data: { order: stackEls.map(e => e.id), mode: 'stack' } as SQFrameData,
      },
    ];
    this.player.setFrames(initFrames);
  }

  private _rebuildElements(order: number[], source: SQElement[]): SQElement[] {
    const byId = new Map(source.map(e => [e.id, e]));
    return order.map(id => byId.get(id)!).filter(Boolean);
  }

  /** Merges frame order ids with source elements, filling in newly created elements
   *  (from the animation) that might not yet be in the persistent store. */
  private _mergeOrder(
    order: number[],
    source: SQElement[],
    data: SQFrameData | undefined,
  ): SQElement[] {
    const byId = new Map(source.map(e => [e.id, e]));

    return order.map(id => {
      if (byId.has(id)) return byId.get(id)!;
      // New element created during animation — find from current source + mode
      const mode = data?.mode ?? 'stack';
      const live = mode === 'stack' ? this._stackElements() : this._queueElements();
      const liveById = new Map(live.map(e => [e.id, e]));
      return liveById.get(id) ?? { id, value: 0 };
    });
  }

  /** CSS class for a given state token. */
  elementStateClass(state: string): string {
    const map: Record<string, string> = {
      idle:   'sq-idle',
      active: 'sq-active',
      push:   'sq-push',
      pop:    'sq-pop',
      top:    'sq-top',
      front:  'sq-front',
      back:   'sq-back',
    };
    return map[state] ?? 'sq-idle';
  }
}
