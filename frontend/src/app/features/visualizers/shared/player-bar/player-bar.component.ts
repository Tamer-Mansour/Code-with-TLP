import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import {
  LucideAngularModule,
  Play, Pause, SkipBack, SkipForward, RotateCcw,
} from 'lucide-angular';
import { VizPlayerService } from '../../core/viz-player.service';

@Component({
  selector: 'app-player-bar',
  standalone: true,
  imports: [LucideAngularModule],
  templateUrl: './player-bar.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlayerBarComponent {
  readonly player = inject(VizPlayerService);

  readonly Play        = Play;
  readonly Pause       = Pause;
  readonly SkipBack    = SkipBack;
  readonly SkipForward = SkipForward;
  readonly RotateCcw   = RotateCcw;

  /** Convert slider value (0-100) to ms speed (2000 down to 80). */
  sliderToSpeed(val: number): number {
    // slider 0 = slowest (2000 ms), slider 100 = fastest (80 ms)
    return Math.round(2000 - (val / 100) * 1920);
  }

  /** Convert ms speed back to slider value. */
  speedToSlider(ms: number): number {
    return Math.round(((2000 - ms) / 1920) * 100);
  }

  onSlider(event: Event): void {
    const val = +(event.target as HTMLInputElement).value;
    this.player.setSpeed(this.sliderToSpeed(val));
  }

  onSeek(event: Event): void {
    const val = +(event.target as HTMLInputElement).value;
    const len  = this.player.frames().length;
    if (len) this.player.seek(Math.round((val / 100) * (len - 1)));
  }

  /** Progress as 0-100 integer for the seek range input. */
  progressInt(): number {
    return Math.floor(this.player.progress() * 100);
  }
}
