import { Directive, ElementRef, Input, AfterViewInit, OnDestroy, inject } from '@angular/core';

/**
 * Reveal-on-scroll. Adds `.reveal` (+ optional `.reveal-<variant>`) immediately,
 * then `.revealed` when the element scrolls into view. Honors reduced-motion.
 *
 * Usage: <div appReveal>            (fade up, default)
 *        <div appReveal="left" [revealDelay]="120">
 */
@Directive({ selector: '[appReveal]', standalone: true })
export class RevealDirective implements AfterViewInit, OnDestroy {
  private readonly el = inject(ElementRef<HTMLElement>);

  @Input('appReveal') variant: '' | 'left' | 'right' | 'scale' = '';
  @Input() revealDelay = 0;

  private observer?: IntersectionObserver;

  ngAfterViewInit(): void {
    const node = this.el.nativeElement;
    node.classList.add('reveal');
    if (this.variant) node.classList.add('reveal-' + this.variant);
    if (this.revealDelay) node.style.transitionDelay = this.revealDelay + 'ms';

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      node.classList.add('revealed');
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            node.classList.add('revealed');
            this.observer?.unobserve(node);
          }
        }
      },
      { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
    );
    this.observer.observe(node);
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
  }
}
