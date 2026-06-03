import {
  Directive,
  ElementRef,
  EventEmitter,
  HostListener,
  Output,
  inject,
} from '@angular/core';

/**
 * Pointer-drag resize handle (like the claude.ai artifact divider).
 *
 * Put it on a thin vertical handle element. It captures the pointer, locks
 * text-selection + sets a col-resize cursor on the body while dragging, and
 * emits the absolute pointer X on every move plus a `dragEnd` when released.
 * The host decides what the new width should be (and clamps / persists it),
 * keeping this directive layout-agnostic and reusable.
 */
@Directive({
  selector: '[tlpDragResize]',
  standalone: true,
})
export class DragResizeDirective {
  private readonly el = inject(ElementRef<HTMLElement>);

  /** Absolute viewport X of the pointer during a drag. */
  @Output() readonly dragMove = new EventEmitter<number>();
  /** Fired once when a drag begins. */
  @Output() readonly dragStart = new EventEmitter<void>();
  /** Fired once when the drag finishes (pointer up / cancel). */
  @Output() readonly dragEnd = new EventEmitter<void>();

  private dragging = false;

  @HostListener('pointerdown', ['$event'])
  onPointerDown(event: PointerEvent): void {
    if (event.button !== 0) return;
    event.preventDefault();
    this.dragging = true;
    this.el.nativeElement.setPointerCapture(event.pointerId);
    document.body.classList.add('tlp-resizing');
    this.dragStart.emit();
  }

  @HostListener('pointermove', ['$event'])
  onPointerMove(event: PointerEvent): void {
    if (!this.dragging) return;
    event.preventDefault();
    this.dragMove.emit(event.clientX);
  }

  @HostListener('pointerup', ['$event'])
  @HostListener('pointercancel', ['$event'])
  onPointerUp(event: PointerEvent): void {
    if (!this.dragging) return;
    this.dragging = false;
    try {
      this.el.nativeElement.releasePointerCapture(event.pointerId);
    } catch {
      /* pointer may already be released */
    }
    document.body.classList.remove('tlp-resizing');
    this.dragEnd.emit();
  }

  /** Double-click the handle to reset to the host's default width. */
  @Output() readonly resetWidth = new EventEmitter<void>();

  @HostListener('dblclick')
  onDoubleClick(): void {
    this.resetWidth.emit();
  }
}
