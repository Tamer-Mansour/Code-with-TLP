import { Component, ChangeDetectionStrategy } from '@angular/core';
import { LucideAngularModule, Star } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

interface Testimonial { quote: string; name: string; role: string; initials: string; }

@Component({
  selector: 'app-landing-testimonials',
  standalone: true,
  imports: [LucideAngularModule, RevealDirective],
  templateUrl: './testimonials.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingTestimonialsComponent {
  readonly Star = Star;
  readonly stars = [0, 1, 2, 3, 4];

  // Placeholder testimonials.
  readonly items: Testimonial[] = [
    { quote: 'The challenges plus instant feedback finally made data structures click for me.', name: 'Maya R.', role: 'CS student', initials: 'MR' },
    { quote: 'I went from theory to actually shipping side projects. The curriculum is gold.', name: 'Daniel K.', role: 'Self-taught dev', initials: 'DK' },
    { quote: 'The visualizers are unreal — I finally understand how Dijkstra works.', name: 'Aisha M.', role: 'Bootcamp grad', initials: 'AM' },
    { quote: 'TLP Chat explaining my weak spots is like having a tutor on call 24/7.', name: 'Leo P.', role: 'Career switcher', initials: 'LP' },
    { quote: 'Ranks and XP make me come back daily. Best study habit I have built.', name: 'Sara T.', role: 'University student', initials: 'ST' },
    { quote: 'Everything in one place — lessons, coding, progress. No more 12 open tabs.', name: 'Omar H.', role: 'Junior engineer', initials: 'OH' },
  ];
}
