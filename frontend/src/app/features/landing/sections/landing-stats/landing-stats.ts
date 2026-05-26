import { Component, ChangeDetectionStrategy } from '@angular/core';
import { LucideAngularModule, BookOpen, GraduationCap, Code2, Layers, Terminal, Trophy } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';
import { CountUpDirective } from '../../shared/count-up.directive';

interface Stat { icon: any; value: number; suffix: string; label: string; }

@Component({
  selector: 'app-landing-stats',
  standalone: true,
  imports: [LucideAngularModule, RevealDirective, CountUpDirective],
  templateUrl: './landing-stats.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingStatsComponent {
  readonly stats: Stat[] = [
    { icon: BookOpen,       value: 14,  suffix: '',  label: 'Courses' },
    { icon: Layers,         value: 10,  suffix: '',  label: 'Subjects' },
    { icon: GraduationCap,  value: 407, suffix: '+', label: 'Lessons' },
    { icon: Code2,          value: 149, suffix: '+', label: 'Challenges' },
    { icon: Terminal,       value: 5,   suffix: '',  label: 'Languages' },
    { icon: Trophy,         value: 8,   suffix: '',  label: 'Rank tiers' },
  ];
}
