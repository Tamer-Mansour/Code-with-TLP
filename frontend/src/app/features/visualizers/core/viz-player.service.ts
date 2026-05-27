import { Injectable, signal, computed } from '@angular/core';
import { VizFrame } from './viz-frame';

/**
 * VizPlayerService — module-agnostic frame player.
 *
 * Holds the frame list + current position as Angular signals so any
 * component can react without manual subscriptions.
 *
 * Usage:
 *   1. Call setFrames(frames) to load a new animation.
 *   2. Call play() / pause() / step() / stepBack() / seek(i) as needed.
 *   3. Read currentFrame() in templates / components.
 */
@Injectable({ providedIn: 'root' })
export class VizPlayerService {
  // ── state ──────────────────────────────────────────────────────────────
  private readonly _frames  = signal<VizFrame[]>([]);
  private readonly _index   = signal(0);
  private readonly _playing = signal(false);
  private readonly _speed   = signal(600); // ms per frame

  private _timer: ReturnType<typeof setTimeout> | null = null;

  // ── public computed ────────────────────────────────────────────────────
  readonly frames  = this._frames.asReadonly();
  readonly index   = this._index.asReadonly();
  readonly playing = this._playing.asReadonly();
  readonly speed   = this._speed.asReadonly();

  readonly currentFrame = computed<VizFrame | null>(() => {
    const fs = this._frames();
    const i  = this._index();
    return fs.length ? fs[i] : null;
  });

  readonly progress = computed(() => {
    const len = this._frames().length;
    return len ? (this._index() + 1) / len : 0;
  });

  readonly stepLabel = computed(() => {
    const len = this._frames().length;
    return len ? `${this._index() + 1} / ${len}` : '0 / 0';
  });

  readonly atEnd   = computed(() => this._index() >= this._frames().length - 1);
  readonly atStart = computed(() => this._index() === 0);

  // ── API ────────────────────────────────────────────────────────────────

  /** Replace the frame list and reset to frame 0. */
  setFrames(frames: VizFrame[]): void {
    this._stopTimer();
    this._playing.set(false);
    this._frames.set(frames);
    this._index.set(0);
  }

  /** Start auto-playing through frames. */
  play(): void {
    if (this._playing() || !this._frames().length) return;
    if (this.atEnd()) this._index.set(0);
    this._playing.set(true);
    this._tick();
  }

  /** Pause auto-play. */
  pause(): void {
    this._playing.set(false);
    this._stopTimer();
  }

  /** Toggle play/pause. */
  toggle(): void {
    this._playing() ? this.pause() : this.play();
  }

  /** Advance one frame (pauses first). */
  step(): void {
    this.pause();
    if (!this.atEnd()) this._index.update(i => i + 1);
  }

  /** Go back one frame (pauses first). */
  stepBack(): void {
    this.pause();
    if (!this.atStart()) this._index.update(i => i - 1);
  }

  /** Jump to a specific frame index. */
  seek(i: number): void {
    this.pause();
    const len = this._frames().length;
    if (!len) return;
    this._index.set(Math.max(0, Math.min(len - 1, i)));
  }

  /** Restart to frame 0 (keeps playing state as-was, but restarts from 0). */
  restart(): void {
    const wasPlaying = this._playing();
    this.pause();
    this._index.set(0);
    if (wasPlaying) this.play();
  }

  /** Set playback speed in milliseconds per frame (50 – 2000). */
  setSpeed(ms: number): void {
    this._speed.set(Math.max(50, Math.min(2000, ms)));
  }

  // ── internal ───────────────────────────────────────────────────────────

  private _tick(): void {
    this._timer = setTimeout(() => {
      if (!this._playing()) return;
      if (this.atEnd()) {
        this._playing.set(false);
        return;
      }
      this._index.update(i => i + 1);
      this._tick();
    }, this._speed());
  }

  private _stopTimer(): void {
    if (this._timer !== null) {
      clearTimeout(this._timer);
      this._timer = null;
    }
  }
}
