import {
  Component, inject, signal, computed, OnInit, ChangeDetectionStrategy,
} from '@angular/core';
import { LucideAngularModule, RotateCcw, Plus, Search, Trash2 } from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';
import { VizFrame } from '../../core/viz-frame';
import { Visualizer, VizMeta } from '../../core/visualizer.base';

// ── Types ─────────────────────────────────────────────────────────────────

/** A single node in a bucket's linked chain. */
export interface HtNode {
  key: number;
  /** State token: 'idle' | 'active' | 'compare' | 'found' | 'miss' | 'inserting' | 'deleting' */
  state?: string;
}

/** One bucket row (index + its chain). */
export interface HtBucket {
  index: number;
  /** State token for the bucket row itself: 'idle' | 'active' | 'found' | 'miss' */
  state?: string;
  chain: HtNode[];
}

/** Payload stored in VizFrame.data for each hash-table frame. */
export interface HtFrameData {
  buckets: HtBucket[];
  /** Total number of keys currently stored. */
  size: number;
}

// ── Constants ─────────────────────────────────────────────────────────────

const TABLE_SIZE = 8;

// ── Pure helpers ──────────────────────────────────────────────────────────

function hashFn(key: number, size: number): number {
  return ((key % size) + size) % size; // handles negative mod in JS
}

/**
 * Deep-clone the bucket array so each VizFrame snapshot is independent.
 */
function cloneBuckets(buckets: HtBucket[]): HtBucket[] {
  return buckets.map(b => ({
    index: b.index,
    state: b.state,
    chain: b.chain.map(n => ({ key: n.key, state: n.state })),
  }));
}

function emptyBuckets(size: number): HtBucket[] {
  return Array.from({ length: size }, (_, i) => ({ index: i, chain: [], state: 'idle' }));
}

function countKeys(buckets: HtBucket[]): number {
  return buckets.reduce((s, b) => s + b.chain.length, 0);
}

// ── Frame builders ────────────────────────────────────────────────────────

export function buildInsertFrames(
  initial: HtBucket[],
  key: number,
): VizFrame[] {
  const fs: VizFrame[] = [];
  const size = initial.length;
  const h = hashFn(key, size);

  // Helper: push a frame with a snapshot
  function push(buckets: HtBucket[], note: string, pseudoLine?: number): void {
    fs.push({
      note,
      pseudoLine,
      data: { buckets: cloneBuckets(buckets), size: countKeys(buckets) } as HtFrameData,
    });
  }

  // Step 0: compute hash
  const s0 = cloneBuckets(initial);
  s0[h].state = 'active';
  push(s0, `Insert <b>${key}</b>: h(${key}) = ${key} mod ${size} = <b>${h}</b> → bucket ${h}`, 0);

  // Step 1: scan chain for duplicate
  const s1 = cloneBuckets(initial);
  s1[h].state = 'active';
  const chain = s1[h].chain;

  if (chain.length === 0) {
    // Empty bucket — insert immediately
    chain.push({ key, state: 'inserting' });
    push(s1, `Bucket ${h} is empty — insert <b>${key}</b> at head`, 1);

    // Final idle snapshot
    const sf = cloneBuckets(s1);
    sf[h].state = 'idle';
    sf[h].chain[0].state = 'idle';
    push(sf, `<b>${key}</b> inserted successfully. Load factor = ${countKeys(sf)}/${size} = ${(countKeys(sf)/size).toFixed(2)}`, 2);
    return fs;
  }

  // Chain has nodes — check for duplicate
  for (let i = 0; i < chain.length; i++) {
    const sc = cloneBuckets(s1);
    sc[h].state = 'active';
    sc[h].chain[i].state = 'compare';
    const existing = sc[h].chain[i].key;
    push(sc, `Check node [${i}] = <b>${existing}</b>: is ${existing} === ${key}?`, 1);

    if (existing === key) {
      const sd = cloneBuckets(sc);
      sd[h].chain[i].state = 'miss';
      push(sd, `<b>${key}</b> already exists in bucket ${h} — no duplicate inserted`, 3);
      return fs;
    }
  }

  // No duplicate — append
  const sa = cloneBuckets(s1);
  sa[h].state = 'active';
  sa[h].chain.push({ key, state: 'inserting' });
  push(sa, `No duplicate found — append <b>${key}</b> to bucket ${h}`, 2);

  const sf = cloneBuckets(sa);
  sf[h].state = 'idle';
  sf[h].chain.forEach(n => { n.state = 'idle'; });
  push(sf, `<b>${key}</b> inserted. Load factor = ${countKeys(sf)}/${size} = ${(countKeys(sf)/size).toFixed(2)}`, 4);

  return fs;
}

export function buildSearchFrames(
  initial: HtBucket[],
  key: number,
): VizFrame[] {
  const fs: VizFrame[] = [];
  const size = initial.length;
  const h = hashFn(key, size);

  function push(buckets: HtBucket[], note: string, pseudoLine?: number): void {
    fs.push({
      note,
      pseudoLine,
      data: { buckets: cloneBuckets(buckets), size: countKeys(buckets) } as HtFrameData,
    });
  }

  // Compute hash
  const s0 = cloneBuckets(initial);
  s0[h].state = 'active';
  push(s0, `Search <b>${key}</b>: h(${key}) = ${key} mod ${size} = <b>${h}</b> → go to bucket ${h}`, 6);

  const chain = initial[h].chain;
  if (chain.length === 0) {
    const sm = cloneBuckets(s0);
    sm[h].state = 'miss';
    push(sm, `Bucket ${h} is empty — <b>${key}</b> not found`, 8);
    return fs;
  }

  for (let i = 0; i < chain.length; i++) {
    const sc = cloneBuckets(s0);
    sc[h].state = 'active';
    sc[h].chain[i].state = 'compare';
    const existing = sc[h].chain[i].key;
    push(sc, `Bucket ${h} [${i}]: compare <b>${existing}</b> with <b>${key}</b>`, 7);

    if (existing === key) {
      const sf = cloneBuckets(sc);
      sf[h].state = 'found';
      sf[h].chain[i].state = 'found';
      push(sf, `Found <b>${key}</b> at bucket ${h}, node index ${i}`, 9);
      return fs;
    }
  }

  const sm = cloneBuckets(s0);
  sm[h].state = 'miss';
  push(sm, `Reached end of bucket ${h} chain — <b>${key}</b> not found`, 8);
  return fs;
}

export function buildDeleteFrames(
  initial: HtBucket[],
  key: number,
): VizFrame[] {
  const fs: VizFrame[] = [];
  const size = initial.length;
  const h = hashFn(key, size);

  function push(buckets: HtBucket[], note: string, pseudoLine?: number): void {
    fs.push({
      note,
      pseudoLine,
      data: { buckets: cloneBuckets(buckets), size: countKeys(buckets) } as HtFrameData,
    });
  }

  const s0 = cloneBuckets(initial);
  s0[h].state = 'active';
  push(s0, `Delete <b>${key}</b>: h(${key}) = ${key} mod ${size} = <b>${h}</b> → bucket ${h}`, 11);

  const chain = initial[h].chain;
  if (chain.length === 0) {
    const sm = cloneBuckets(s0);
    sm[h].state = 'miss';
    push(sm, `Bucket ${h} is empty — <b>${key}</b> not found, nothing to delete`, 13);
    return fs;
  }

  for (let i = 0; i < chain.length; i++) {
    const sc = cloneBuckets(s0);
    sc[h].state = 'active';
    sc[h].chain[i].state = 'compare';
    const existing = sc[h].chain[i].key;
    push(sc, `Bucket ${h} [${i}]: compare <b>${existing}</b> with <b>${key}</b>`, 12);

    if (existing === key) {
      // Mark as deleting
      const sd = cloneBuckets(sc);
      sd[h].chain[i].state = 'deleting';
      push(sd, `Match found at [${i}] — removing <b>${key}</b> from bucket ${h}`, 14);

      // Remove the node
      const sf = cloneBuckets(sd);
      sf[h].chain.splice(i, 1);
      sf[h].state = 'idle';
      push(sf, `<b>${key}</b> deleted. Load factor = ${countKeys(sf)}/${size} = ${(countKeys(sf)/size).toFixed(2)}`, 15);
      return fs;
    }
  }

  const sm = cloneBuckets(s0);
  sm[h].state = 'miss';
  push(sm, `Reached end of bucket ${h} chain — <b>${key}</b> not found`, 13);
  return fs;
}

// ── Component ─────────────────────────────────────────────────────────────

@Component({
  selector: 'app-viz-hash-table',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './hash-table.component.html',
  styleUrls: ['./hash-table.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HashTableComponent implements OnInit, Visualizer {
  private readonly player = inject(VizPlayerService);

  // Lucide icons
  readonly RotateCcw = RotateCcw;
  readonly Plus      = Plus;
  readonly Search    = Search;
  readonly Trash2    = Trash2;

  // ── VizMeta ──────────────────────────────────────────────────────────────
  readonly meta: VizMeta = {
    slug: 'hash-table',
    title: 'Hash Table (Separate Chaining)',
    category: 'Hashing',
    description:
      'Visualise a hash table with separate chaining. Insert, search, and delete integer keys while watching the hash function h(k) = k mod 8 route each key to its bucket.',
    operations: ['Insert', 'Search', 'Delete'],
    complexity: {
      Insert: { time: 'O(1) avg / O(n) worst', space: 'O(1)' },
      Search: { time: 'O(1) avg / O(n) worst', space: 'O(1)' },
      Delete: { time: 'O(1) avg / O(n) worst', space: 'O(1)' },
    },
  };

  // ── State ─────────────────────────────────────────────────────────────────
  readonly TABLE_SIZE = TABLE_SIZE;

  /** Live backing store — mutated only by operations, never by frames. */
  buckets = signal<HtBucket[]>(emptyBuckets(TABLE_SIZE));

  readonly inputValue = signal('');
  readonly selectedOp = signal<'Insert' | 'Search' | 'Delete'>('Insert');

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  ngOnInit(): void {
    // Pre-load a few interesting keys so the table is not empty on first view
    const defaults = [23, 7, 15, 31, 6];
    let b = emptyBuckets(TABLE_SIZE);
    for (const k of defaults) {
      const h = hashFn(k, TABLE_SIZE);
      if (!b[h].chain.find(n => n.key === k)) {
        b = cloneBuckets(b);
        b[h].chain.push({ key: k, state: 'idle' });
      }
    }
    this.buckets.set(b);
    this.player.setFrames([{
      note: 'Sample table loaded — keys 23, 7, 15, 31, 6. Try Insert, Search, or Delete.',
      data: { buckets: cloneBuckets(b), size: countKeys(b) } as HtFrameData,
    }]);
  }

  // ── User actions ───────────────────────────────────────────────────────────
  onInputChange(e: Event): void {
    this.inputValue.set((e.target as HTMLInputElement).value);
  }

  onInputKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') this.runOp();
  }

  selectOp(op: string): void {
    if (op === 'Insert' || op === 'Search' || op === 'Delete') {
      this.selectedOp.set(op);
    }
  }

  runOp(): void {
    const raw = parseInt(this.inputValue(), 10);
    if (!Number.isFinite(raw)) return;

    const current = this.buckets();
    const op = this.selectedOp();

    if (op === 'Insert') {
      const frames = buildInsertFrames(current, raw);
      this.player.setFrames(frames);
      this.player.play();

      // Mutate backing store
      const h = hashFn(raw, TABLE_SIZE);
      const already = current[h].chain.some(n => n.key === raw);
      if (!already) {
        const next = cloneBuckets(current);
        next[h].chain.push({ key: raw, state: 'idle' });
        this.buckets.set(next);
      }
    } else if (op === 'Search') {
      const frames = buildSearchFrames(current, raw);
      this.player.setFrames(frames);
      this.player.play();
    } else {
      const frames = buildDeleteFrames(current, raw);
      this.player.setFrames(frames);
      this.player.play();

      // Mutate backing store
      const h = hashFn(raw, TABLE_SIZE);
      const idx = current[h].chain.findIndex(n => n.key === raw);
      if (idx !== -1) {
        const next = cloneBuckets(current);
        next[h].chain.splice(idx, 1);
        this.buckets.set(next);
      }
    }

    this.inputValue.set('');
  }

  onReset(): void {
    const b = emptyBuckets(TABLE_SIZE);
    this.buckets.set(b);
    this.player.setFrames([{
      note: 'Table cleared. Enter a key and choose Insert, Search, or Delete.',
      data: { buckets: cloneBuckets(b), size: 0 } as HtFrameData,
    }]);
  }

  // ── Visualizer interface ──────────────────────────────────────────────────
  buildFrames(input: Record<string, unknown>): VizFrame[] {
    const op  = input['operation'] as string ?? 'Insert';
    const key = input['value']     as number ?? 0;
    const bkt = (input['buckets'] as HtBucket[] | undefined) ?? this.buckets();
    switch (op) {
      case 'Insert': return buildInsertFrames(bkt, key);
      case 'Search': return buildSearchFrames(bkt, key);
      case 'Delete': return buildDeleteFrames(bkt, key);
      default:       return buildInsertFrames(bkt, key);
    }
  }

  // ── Computed view model ────────────────────────────────────────────────────

  /** Buckets derived from the current frame (falls back to live store). */
  readonly displayBuckets = computed<HtBucket[]>(() => {
    const frame = this.player.currentFrame();
    if (frame?.data) {
      return (frame.data as HtFrameData).buckets;
    }
    return this.buckets();
  });

  /** Load factor from current frame. */
  readonly loadFactor = computed<number>(() => {
    const frame = this.player.currentFrame();
    const size = (frame?.data as HtFrameData | undefined)?.size ?? countKeys(this.buckets());
    return size / TABLE_SIZE;
  });

  /** Total keys from current frame. */
  readonly keyCount = computed<number>(() => {
    const frame = this.player.currentFrame();
    return (frame?.data as HtFrameData | undefined)?.size ?? countKeys(this.buckets());
  });

  // ── CSS class helpers ──────────────────────────────────────────────────────

  bucketRowClass(state: string | undefined): string {
    const base = 'ht-bucket-row';
    switch (state) {
      case 'active': return `${base} ht-bucket-active`;
      case 'found':  return `${base} ht-bucket-found`;
      case 'miss':   return `${base} ht-bucket-miss`;
      default:       return base;
    }
  }

  nodeClass(state: string | undefined): string {
    const base = 'ht-node';
    switch (state) {
      case 'compare':   return `${base} ht-node-compare`;
      case 'found':     return `${base} ht-node-found`;
      case 'miss':      return `${base} ht-node-miss`;
      case 'inserting': return `${base} ht-node-inserting`;
      case 'deleting':  return `${base} ht-node-deleting`;
      default:          return `${base} ht-node-idle`;
    }
  }

  /** Clamped 0-100 percentage for the load-factor progress bar. */
  readonly loadFactorPct = computed<number>(() =>
    Math.min(100, Math.round(this.loadFactor() * 100))
  );

  loadFactorBarClass(): string {
    const lf = this.loadFactor();
    if (lf >= 0.75) return 'ht-lf-high';
    if (lf >= 0.5)  return 'ht-lf-med';
    return 'ht-lf-low';
  }
}
