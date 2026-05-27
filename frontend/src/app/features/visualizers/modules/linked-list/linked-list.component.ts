import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, Plus, Search, RotateCcw, Trash2, RefreshCw } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── data model ────────────────────────────────────────────────────────────────

interface LLNode {
  id: number;
  value: number;
}

/** Payload stored in every VizFrame.data for linked-list frames. */
interface LLFrameData {
  /** Ordered list of node ids representing the current list state. */
  order: number[];
  /** Node ids that have been visually removed (for fade-out on last frame). */
  removed?: number[];
}

// ── id counter ────────────────────────────────────────────────────────────────

let _nextId = 1;
function makeNode(value: number): LLNode {
  return { id: _nextId++, value };
}

// ── pure frame builders ────────────────────────────────────────────────────────

function buildInsertHead(nodes: LLNode[], value: number): { frames: VizFrame[]; result: LLNode[] } {
  const newNode = makeNode(value);
  const result = [newNode, ...nodes];
  const frames: VizFrame[] = [];

  frames.push({
    note: `Insert <b>${value}</b> at the head — create new node`,
    states: { [newNode.id]: 'new' },
    data: { order: result.map(n => n.id) } as LLFrameData,
  });

  if (nodes.length > 0) {
    frames.push({
      note: `Point new node's next to the old head (<b>${nodes[0].value}</b>)`,
      states: { [newNode.id]: 'active', [nodes[0].id]: 'pointer' },
      data: { order: result.map(n => n.id) } as LLFrameData,
    });
  }

  frames.push({
    note: `Update <b>head</b> pointer to new node — <b>${value}</b> is now the head`,
    states: { [newNode.id]: 'head' },
    data: { order: result.map(n => n.id) } as LLFrameData,
  });

  return { frames, result };
}

function buildInsertTail(nodes: LLNode[], value: number): { frames: VizFrame[]; result: LLNode[] } {
  const newNode = makeNode(value);
  const result = [...nodes, newNode];
  const frames: VizFrame[] = [];

  if (nodes.length === 0) {
    frames.push({
      note: `List is empty — <b>${value}</b> becomes both head and tail`,
      states: { [newNode.id]: 'head' },
      data: { order: result.map(n => n.id) } as LLFrameData,
    });
    return { frames, result };
  }

  frames.push({
    note: `Insert <b>${value}</b> at the tail — traverse to find the last node`,
    states: {},
    data: { order: nodes.map(n => n.id) } as LLFrameData,
  });

  // Walk through nodes one by one
  for (let i = 0; i < nodes.length; i++) {
    const isLast = i === nodes.length - 1;
    frames.push({
      note: isLast
        ? `At node <b>${nodes[i].value}</b> — next is null, this is the tail`
        : `Visit node <b>${nodes[i].value}</b> — next is not null, keep going`,
      states: { [nodes[i].id]: isLast ? 'active' : 'visit' },
      data: { order: nodes.map(n => n.id) } as LLFrameData,
    });
  }

  frames.push({
    note: `Point tail's next to the new node <b>${value}</b>`,
    states: { [nodes[nodes.length - 1].id]: 'pointer', [newNode.id]: 'new' },
    data: { order: result.map(n => n.id) } as LLFrameData,
  });

  frames.push({
    note: `<b>${value}</b> appended at the tail successfully`,
    states: { [newNode.id]: 'active' },
    data: { order: result.map(n => n.id) } as LLFrameData,
  });

  return { frames, result };
}

function buildDeleteValue(nodes: LLNode[], value: number): { frames: VizFrame[]; result: LLNode[] } {
  const frames: VizFrame[] = [];

  if (nodes.length === 0) {
    frames.push({
      note: 'List is empty — nothing to delete',
      states: {},
      data: { order: [] } as LLFrameData,
    });
    return { frames, result: [] };
  }

  frames.push({
    note: `Delete node with value <b>${value}</b> — scan the list`,
    states: {},
    data: { order: nodes.map(n => n.id) } as LLFrameData,
  });

  let foundIdx = -1;
  for (let i = 0; i < nodes.length; i++) {
    const match = nodes[i].value === value;
    frames.push({
      note: match
        ? `Found <b>${value}</b> at position ${i}`
        : `Node <b>${nodes[i].value}</b> does not match — move to next`,
      states: { [nodes[i].id]: match ? 'found' : 'visit' },
      data: { order: nodes.map(n => n.id) } as LLFrameData,
    });
    if (match) { foundIdx = i; break; }
  }

  if (foundIdx === -1) {
    frames.push({
      note: `<b>${value}</b> is not in the list`,
      states: {},
      data: { order: nodes.map(n => n.id) } as LLFrameData,
    });
    return { frames, result: nodes };
  }

  const result = nodes.filter((_, i) => i !== foundIdx);

  if (foundIdx === 0) {
    frames.push({
      note: `Removing head — update head pointer to <b>${result[0]?.value ?? 'null'}</b>`,
      states: { [nodes[0].id]: 'delete' },
      data: { order: nodes.map(n => n.id), removed: [nodes[0].id] } as LLFrameData,
    });
  } else {
    const prev = nodes[foundIdx - 1];
    const next = nodes[foundIdx + 1];
    frames.push({
      note: `Bridge: point <b>${prev.value}</b>'s next to <b>${next?.value ?? 'null'}</b>, bypassing deleted node`,
      states: { [nodes[foundIdx].id]: 'delete', [prev.id]: 'pointer' },
      data: { order: nodes.map(n => n.id), removed: [nodes[foundIdx].id] } as LLFrameData,
    });
  }

  frames.push({
    note: `Node <b>${value}</b> removed — list updated`,
    states: result[0] ? { [result[0].id]: 'head' } : {},
    data: { order: result.map(n => n.id) } as LLFrameData,
  });

  return { frames, result };
}

function buildSearch(nodes: LLNode[], value: number): { frames: VizFrame[]; result: LLNode[] } {
  const frames: VizFrame[] = [];

  if (nodes.length === 0) {
    frames.push({
      note: 'List is empty — nothing to search',
      states: {},
      data: { order: [] } as LLFrameData,
    });
    return { frames, result: nodes };
  }

  frames.push({
    note: `Search for <b>${value}</b> — start at head`,
    states: nodes[0] ? { [nodes[0].id]: 'pointer' } : {},
    data: { order: nodes.map(n => n.id) } as LLFrameData,
  });

  let found = false;
  for (let i = 0; i < nodes.length; i++) {
    const match = nodes[i].value === value;
    frames.push({
      note: match
        ? `Found <b>${value}</b> at position ${i}`
        : `Check node <b>${nodes[i].value}</b> — not a match, advance pointer`,
      states: { [nodes[i].id]: match ? 'found' : 'visit' },
      data: { order: nodes.map(n => n.id) } as LLFrameData,
    });
    if (match) { found = true; break; }
  }

  if (!found) {
    frames.push({
      note: `<b>${value}</b> is not in the list — search exhausted`,
      states: {},
      data: { order: nodes.map(n => n.id) } as LLFrameData,
    });
  }

  return { frames, result: nodes };
}

function buildReverse(nodes: LLNode[]): { frames: VizFrame[]; result: LLNode[] } {
  const frames: VizFrame[] = [];

  if (nodes.length <= 1) {
    frames.push({
      note: nodes.length === 0
        ? 'List is empty — nothing to reverse'
        : 'Single node — already reversed',
      states: nodes[0] ? { [nodes[0].id]: 'head' } : {},
      data: { order: nodes.map(n => n.id) } as LLFrameData,
    });
    return { frames, result: nodes };
  }

  frames.push({
    note: 'Reverse the list — set prev=null, curr=head',
    states: { [nodes[0].id]: 'active' },
    data: { order: nodes.map(n => n.id) } as LLFrameData,
  });

  // Show pointer flip for each pair
  for (let i = 0; i < nodes.length; i++) {
    const cur = nodes[i];
    const prev = i > 0 ? nodes[i - 1] : null;
    const next = i < nodes.length - 1 ? nodes[i + 1] : null;

    if (i === 0) {
      frames.push({
        note: `curr = <b>${cur.value}</b>: set next to prev (<b>null</b>) — first node's pointer flipped`,
        states: { [cur.id]: 'flip' },
        data: { order: nodes.map(n => n.id) } as LLFrameData,
      });
    } else {
      frames.push({
        note: `curr = <b>${cur.value}</b>: point next to prev (<b>${prev!.value}</b>) — pointer flipped`,
        states: { [cur.id]: 'flip', [prev!.id]: 'pointer' },
        data: { order: nodes.map(n => n.id) } as LLFrameData,
      });
    }

    if (next) {
      frames.push({
        note: `Advance: prev = <b>${cur.value}</b>, curr = <b>${next.value}</b>`,
        states: { [next.id]: 'active', [cur.id]: 'sorted' },
        data: { order: nodes.map(n => n.id) } as LLFrameData,
      });
    }
  }

  const result = [...nodes].reverse();

  frames.push({
    note: `curr is null — reverse complete. New head is <b>${result[0].value}</b>`,
    states: { [result[0].id]: 'head' },
    data: { order: result.map(n => n.id) } as LLFrameData,
  });

  return { frames, result };
}

// ── default list ───────────────────────────────────────────────────────────────

function buildDefaultList(): LLNode[] {
  _nextId = 1;
  return [10, 20, 30, 40, 50].map(v => makeNode(v));
}

// ── operations ─────────────────────────────────────────────────────────────────

const OPERATIONS = [
  'Insert at Head',
  'Insert at Tail',
  'Delete Value',
  'Search Value',
  'Reverse',
] as const;

type Operation = typeof OPERATIONS[number];

// ── component ──────────────────────────────────────────────────────────────────

@Component({
  selector: 'app-viz-linked-list',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './linked-list.component.html',
  styleUrl: './linked-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LinkedListComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  // Lucide icons
  readonly Plus      = Plus;
  readonly Search    = Search;
  readonly RotateCcw = RotateCcw;
  readonly Trash2    = Trash2;
  readonly RefreshCw = RefreshCw;

  readonly meta: VizMeta = {
    slug: 'linked-list',
    title: 'Singly Linked List',
    category: 'Linear',
    description: 'Visualize insert, delete, search, and reverse on a singly linked list with animated pointer walk and node transitions.',
    operations: [...OPERATIONS],
    complexity: {
      'Insert at Head': { time: 'O(1)', space: 'O(1)' },
      'Insert at Tail': { time: 'O(n)', space: 'O(1)' },
      'Delete Value':   { time: 'O(n)', space: 'O(1)' },
      'Search Value':   { time: 'O(n)', space: 'O(1)' },
      'Reverse':        { time: 'O(n)', space: 'O(1)' },
    },
  };

  readonly operations = OPERATIONS;

  // ── state signals ────────────────────────────────────────────────────────
  readonly selectedOp = signal<Operation>('Insert at Head');
  readonly inputValue = signal('');
  readonly nodes      = signal<LLNode[]>(buildDefaultList());

  // True when the current operation needs a value input
  readonly needsValue = computed<boolean>(() => {
    const op = this.selectedOp();
    return op !== 'Reverse';
  });

  readonly currentComplexity = computed(() => {
    return this.meta.complexity?.[this.selectedOp()] ?? null;
  });

  // ── view model from current frame ────────────────────────────────────────

  /** Nodes as rendered in the current frame. */
  readonly displayNodes = computed(() => {
    const frame    = this.player.currentFrame();
    const allNodes = this.nodes();
    const byId     = new Map(allNodes.map(n => [n.id, n]));

    const order: number[] = (frame?.data as LLFrameData | undefined)?.order
      ?? allNodes.map(n => n.id);
    const removed = new Set((frame?.data as LLFrameData | undefined)?.removed ?? []);
    const states  = frame?.states ?? {};

    return order.map((id, pos) => {
      const n     = byId.get(id);
      const value = n?.value ?? id;
      const state = removed.has(id) ? 'delete' : (states[id] ?? 'idle');
      return { id, value, pos, state };
    });
  });

  readonly currentNote = computed(() => this.player.currentFrame()?.note ?? '');

  // ── lifecycle ─────────────────────────────────────────────────────────────

  ngOnInit(): void {
    this._pushInitialFrame();
  }

  // ── public actions ────────────────────────────────────────────────────────

  selectOp(op: Operation): void {
    this.selectedOp.set(op);
    this.inputValue.set('');
    this._pushInitialFrame();
  }

  onInputChange(event: Event): void {
    this.inputValue.set((event.target as HTMLInputElement).value);
  }

  onInputKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter') this.run();
  }

  run(): void {
    const op    = this.selectedOp();
    const raw   = parseInt(this.inputValue(), 10);
    const value = Number.isFinite(raw) ? raw : 0;

    let frames: VizFrame[];
    let result: LLNode[];

    switch (op) {
      case 'Insert at Head': {
        const r = buildInsertHead(this.nodes(), value);
        frames = r.frames; result = r.result; break;
      }
      case 'Insert at Tail': {
        const r = buildInsertTail(this.nodes(), value);
        frames = r.frames; result = r.result; break;
      }
      case 'Delete Value': {
        const r = buildDeleteValue(this.nodes(), value);
        frames = r.frames; result = r.result; break;
      }
      case 'Search Value': {
        const r = buildSearch(this.nodes(), value);
        frames = r.frames; result = r.result; break;
      }
      case 'Reverse': {
        const r = buildReverse(this.nodes());
        frames = r.frames; result = r.result; break;
      }
      default:
        return;
    }

    this.nodes.set(result);
    this.player.setFrames(frames);
    this.player.play();
    this.inputValue.set('');
  }

  reset(): void {
    this.nodes.set(buildDefaultList());
    this.inputValue.set('');
    this._pushInitialFrame();
  }

  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const op    = (input['operation'] as Operation) ?? 'Insert at Head';
    const value = (input['value'] as number) ?? 0;
    const nodes = (input['nodes'] as LLNode[]) ?? this.nodes();
    switch (op) {
      case 'Insert at Head': return buildInsertHead(nodes, value).frames;
      case 'Insert at Tail': return buildInsertTail(nodes, value).frames;
      case 'Delete Value':   return buildDeleteValue(nodes, value).frames;
      case 'Search Value':   return buildSearch(nodes, value).frames;
      case 'Reverse':        return buildReverse(nodes).frames;
      default:               return [];
    }
  }

  // ── view helpers ──────────────────────────────────────────────────────────

  nodeClass(state: string): string {
    const base = 'node-box';
    const stateMap: Record<string, string> = {
      idle:    'node-idle',
      active:  'node-active',
      visit:   'node-visit',
      found:   'node-found',
      delete:  'node-delete',
      new:     'node-new',
      head:    'node-head',
      pointer: 'node-pointer',
      flip:    'node-flip',
      sorted:  'node-sorted',
    };
    return `${base} ${stateMap[state] ?? 'node-idle'}`;
  }

  arrowClass(state: string): string {
    const map: Record<string, string> = {
      pointer: 'arrow-active',
      flip:    'arrow-flip',
      delete:  'arrow-delete',
    };
    return `ll-arrow ${map[state] ?? 'arrow-idle'}`;
  }

  trackById(_: number, node: { id: number }): number {
    return node.id;
  }

  // ── private ────────────────────────────────────────────────────────────────

  private _pushInitialFrame(): void {
    const ns = this.nodes();
    this.player.setFrames([{
      note: ns.length
        ? `Linked list has <b>${ns.length}</b> node${ns.length !== 1 ? 's' : ''}. Select an operation and run it.`
        : 'List is empty. Insert a value to begin.',
      states: ns[0] ? { [ns[0].id]: 'head' } : {},
      data:   { order: ns.map(n => n.id) } as LLFrameData,
    }]);
  }
}
