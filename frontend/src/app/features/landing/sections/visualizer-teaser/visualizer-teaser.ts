import { Component, signal, OnInit, OnDestroy, ChangeDetectionStrategy } from '@angular/core';
import { NgClass } from '@angular/common';
import { LucideAngularModule, ArrowRight } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

@Component({
  selector: 'app-landing-visualizer',
  standalone: true,
  imports: [NgClass, LucideAngularModule, RevealDirective],
  templateUrl: './visualizer-teaser.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingVisualizerComponent implements OnInit, OnDestroy {
  readonly ArrowRight = ArrowRight;
  readonly bars = signal<number[]>([]);
  readonly aIdx = signal(-1);
  readonly bIdx = signal(-1);

  private i = 0;
  private j = 0;
  private timer: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.shuffle();
    this.timer = setInterval(() => this.step(), 650);
  }

  ngOnDestroy(): void {
    if (this.timer) clearInterval(this.timer);
  }

  private shuffle(): void {
    this.bars.set(Array.from({ length: 11 }, () => 14 + Math.floor(Math.random() * 86)));
    this.i = 0;
    this.j = 0;
    this.aIdx.set(-1);
    this.bIdx.set(-1);
  }

  private step(): void {
    const arr = [...this.bars()];
    const n = arr.length;
    if (this.i >= n - 1) { this.shuffle(); return; }   // sorted → loop
    this.aIdx.set(this.j);
    this.bIdx.set(this.j + 1);
    if (arr[this.j] > arr[this.j + 1]) {
      [arr[this.j], arr[this.j + 1]] = [arr[this.j + 1], arr[this.j]];
      this.bars.set(arr);
    }
    this.j++;
    if (this.j >= n - 1 - this.i) { this.j = 0; this.i++; }
  }
}
