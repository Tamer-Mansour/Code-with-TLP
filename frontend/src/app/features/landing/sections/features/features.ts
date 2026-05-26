import { Component, ChangeDetectionStrategy } from '@angular/core';
import { NgClass } from '@angular/common';
import {
  LucideAngularModule,
  Code2,
  BookOpen,
  FlaskConical,
  GitBranch,
  Bot,
  Trophy,
  BarChart2,
  Moon,
} from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

export interface FeatureCard {
  icon: any;
  title: string;
  description: string;
  /** Tailwind col-span class at lg breakpoint */
  colSpan: string;
  /** Tailwind row-span class at lg breakpoint */
  rowSpan: string;
  /** Whether to apply the accent gradient ring */
  accent: boolean;
}

@Component({
  selector: 'app-landing-features',
  standalone: true,
  imports: [NgClass, LucideAngularModule, RevealDirective],
  templateUrl: './features.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingFeaturesComponent {
  readonly Code2 = Code2;
  readonly BookOpen = BookOpen;
  readonly FlaskConical = FlaskConical;
  readonly GitBranch = GitBranch;
  readonly Bot = Bot;
  readonly Trophy = Trophy;
  readonly BarChart2 = BarChart2;
  readonly Moon = Moon;

  readonly features: FeatureCard[] = [
    {
      icon: Code2,
      title: 'Interactive Coding',
      description:
        'Write and run real code in your browser — Python, JS, TS, Java, and C# with instant feedback.',
      colSpan: 'lg:col-span-2',
      rowSpan: 'lg:row-span-2',
      accent: true,
    },
    {
      icon: BookOpen,
      title: 'A–Z CS Curriculum',
      description:
        '14 courses · 10 subjects · 400+ lessons guiding you from first principles to advanced systems.',
      colSpan: 'lg:col-span-2',
      rowSpan: 'lg:row-span-2',
      accent: true,
    },
    {
      icon: FlaskConical,
      title: 'LeetCode-Style Challenges',
      description:
        'Auto-graded problems with hidden test cases — earn XP and sharpen your problem-solving.',
      colSpan: 'lg:col-span-1',
      rowSpan: 'lg:row-span-1',
      accent: false,
    },
    {
      icon: GitBranch,
      title: 'Algorithm Visualizers',
      description:
        'Watch sorting, graphs, and data structures animate step-by-step as the code runs.',
      colSpan: 'lg:col-span-1',
      rowSpan: 'lg:row-span-1',
      accent: false,
    },
    {
      icon: Bot,
      title: 'TLP Chat (AI)',
      description:
        'A RAG-powered assistant that knows your progress and answers CS questions in context.',
      colSpan: 'lg:col-span-1',
      rowSpan: 'lg:row-span-1',
      accent: false,
    },
    {
      icon: Trophy,
      title: 'Ranked Profile',
      description:
        'Steam-style tiers, XP, and streaks — see where you stand among all learners.',
      colSpan: 'lg:col-span-1',
      rowSpan: 'lg:row-span-1',
      accent: false,
    },
    {
      icon: BarChart2,
      title: 'Progress Dashboard',
      description:
        'Visual heatmaps and mastery charts so you always know what to tackle next.',
      colSpan: 'lg:col-span-2',
      rowSpan: 'lg:row-span-1',
      accent: false,
    },
    {
      icon: Moon,
      title: 'Dark & Light Themes',
      description:
        'Polished in both modes — toggle any time without losing your place.',
      colSpan: 'lg:col-span-2',
      rowSpan: 'lg:row-span-1',
      accent: false,
    },
  ];

  readonly delayMap: number[] = [0, 80, 160, 220, 280, 340, 400, 460];
}
