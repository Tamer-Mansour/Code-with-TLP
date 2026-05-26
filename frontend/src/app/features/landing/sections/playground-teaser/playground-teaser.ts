import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule, CheckCircle2, ArrowRight } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

@Component({
  selector: 'app-landing-playground',
  standalone: true,
  imports: [RouterLink, LucideAngularModule, RevealDirective],
  templateUrl: './playground-teaser.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingPlaygroundComponent {
  readonly CheckCircle2 = CheckCircle2;
  readonly ArrowRight = ArrowRight;

  readonly bullets = [
    'Five languages: Python, JavaScript, TypeScript, Java, C#',
    'Hidden test cases with instant auto-grading',
    'Earn XP for every challenge you solve',
  ];
  readonly tests = [
    { n: 'sample case', d: 500 },
    { n: 'edge: empty input', d: 900 },
    { n: 'hidden: large input', d: 1300 },
  ];
}
