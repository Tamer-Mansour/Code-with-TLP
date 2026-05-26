import { Directive, ElementRef, Input, AfterViewInit, OnDestroy, inject } from '@angular/core';

/**
 * Animated number count-up that triggers when scrolled into view.
 * Usage: <span [appCountUp]="407" countSuffix="+"></span>
 */
@Directive({ selector: '[appCountUp]', standalone: true })
export class CountUpDirective implements AfterViewInit, OnDestroy {
  private readonly el = inject(ElementRef<HTMLElement>);

  @Input('appCountUp') end = 0;
  @Input() countDuration = 1600;
  @Input() countSuffix = '';
  @Input() countPrefix = '';

  private observer?: IntersectionObserver;
  private done = false;

  ngAfterViewInit(): void {
    const node = this.el.nativeElement;
    node.textContent = this.countPrefix + '0' + this.countSuffix;

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      node.textContent = this.countPrefix + this.end + this.countSuffix;
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting && !this.done) {
            this.done = true;
            this.run();
            this.observer?.disconnect();
          }
        }
      },
      { threshold: 0.4 }
    );
    this.observer.observe(node);
  }

  private run(): void {
    const node = this.el.nativeElement;
    const start = performance.now();
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / this.countDuration);
      const eased = 1 - Math.pow(1 - p, 3);
      node.textContent = this.countPrefix + Math.round(this.end * eased) + this.countSuffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
  }
}
