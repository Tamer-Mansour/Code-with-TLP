import { Component, ChangeDetectionStrategy } from '@angular/core';
import { LucideAngularModule, Trophy } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

interface Tier { name: string; color: string; xp: string; here?: boolean; }

@Component({
  selector: 'app-landing-ranks',
  standalone: true,
  imports: [LucideAngularModule, RevealDirective],
  templateUrl: './ranks.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingRanksComponent {
  readonly Trophy = Trophy;
  readonly tiers: Tier[] = [
    { name: 'Newcomer', color: '#94a3b8', xp: '0' },
    { name: 'Apprentice', color: '#22c55e', xp: '250' },
    { name: 'Practitioner', color: '#06b6d4', xp: '750' },
    { name: 'Skilled', color: '#3b82f6', xp: '1.5k', here: true },
    { name: 'Expert', color: '#8b5cf6', xp: '3k' },
    { name: 'Master', color: '#ec4899', xp: '6k' },
    { name: 'Grandmaster', color: '#f59e0b', xp: '12k' },
    { name: 'Legend', color: '#ef4444', xp: '25k' },
  ];
}
