import { Component, ChangeDetectionStrategy } from '@angular/core';
import { LucideAngularModule, Compass, Code2, Trophy } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

@Component({
  selector: 'app-landing-how',
  standalone: true,
  imports: [LucideAngularModule, RevealDirective],
  templateUrl: './how-it-works.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingHowComponent {
  readonly steps = [
    { n: 1, icon: Compass, title: 'Pick a path', text: 'Choose a course or subject — from foundations to AI. Enroll in one click.' },
    { n: 2, icon: Code2, title: 'Learn & practice', text: 'Read bite-size lessons, then solve challenges in a real multi-language code runner.' },
    { n: 3, icon: Trophy, title: 'Track & rank up', text: 'Earn XP, climb the 8 tiers, and watch your progress on a visual dashboard.' },
  ];
}
