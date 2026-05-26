import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule, ArrowRight, Play, Zap, CheckCircle2, Sparkles } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

@Component({
  selector: 'app-landing-hero',
  standalone: true,
  imports: [RouterLink, LucideAngularModule, RevealDirective],
  templateUrl: './landing-hero.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingHeroComponent {
  readonly ArrowRight = ArrowRight;
  readonly Play = Play;
  readonly Zap = Zap;
  readonly CheckCircle2 = CheckCircle2;
  readonly Sparkles = Sparkles;

  readonly tests = [
    { name: 'two_sum([2,7,11], 9)', delay: 600 },
    { name: 'two_sum([3,2,4], 6)', delay: 1000 },
    { name: 'edge: empty input', delay: 1400 },
  ];
}
