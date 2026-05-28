import { Component, input, computed, ChangeDetectionStrategy } from '@angular/core';
import { NgClass } from '@angular/common';
import { LucideAngularModule } from 'lucide-angular';

@Component({
  selector: 'app-terminal-card',
  standalone: true,
  imports: [NgClass, LucideAngularModule],
  templateUrl: './terminal-card.html',
  styleUrls: ['./terminal-card.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TerminalCardComponent {
  title = input<string>('');
  value = input<string | number>('');
  suffix = input<string>('');
  loading = input<boolean>(false);
  icon = input<string>('');
  badgeText = input<string>('');
  themeColor = input<'blue' | 'green' | 'purple' | 'amber' | 'rose' | 'cyan'>('blue');
  promptPath = input<string>('~');
  footerText = input<string>('');

  colorClasses = computed(() => {
    switch (this.themeColor()) {
      case 'green':
        return {
          card: 'bg-emerald-50/40 border-emerald-100 dark:bg-[#0f1f18]/60 dark:border-emerald-950/40 shadow-emerald-100/10 dark:shadow-emerald-950/5',
          header: 'bg-emerald-50/80 dark:bg-[#0b1712]/80 border-emerald-100/50 dark:border-emerald-950/20',
          titleText: 'text-emerald-700 dark:text-emerald-400',
          promptPath: 'text-emerald-600 dark:text-emerald-400',
          promptArrow: 'text-emerald-500 dark:text-emerald-500',
          badge: 'bg-emerald-100/80 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-400 border border-emerald-200/40 dark:border-emerald-800/30',
          valueText: 'text-emerald-900 dark:text-emerald-100',
          footerText: 'text-emerald-700/70 dark:text-emerald-400/60',
          glow: 'group-hover:border-emerald-300 dark:group-hover:border-emerald-800/60 group-hover:shadow-emerald-200/50 dark:group-hover:shadow-emerald-900/10',
        };
      case 'purple':
        return {
          card: 'bg-purple-50/40 border-purple-100 dark:bg-[#1a142d]/60 dark:border-purple-950/40 shadow-purple-100/10 dark:shadow-purple-950/5',
          header: 'bg-purple-50/80 dark:bg-[#130f22]/80 border-purple-100/50 dark:border-purple-950/20',
          titleText: 'text-purple-700 dark:text-purple-400',
          promptPath: 'text-purple-600 dark:text-purple-400',
          promptArrow: 'text-purple-500 dark:text-purple-500',
          badge: 'bg-purple-100/80 text-purple-800 dark:bg-purple-950/80 dark:text-purple-400 border border-purple-200/40 dark:border-purple-800/30',
          valueText: 'text-purple-900 dark:text-purple-100',
          footerText: 'text-purple-700/70 dark:text-purple-400/60',
          glow: 'group-hover:border-purple-300 dark:group-hover:border-purple-800/60 group-hover:shadow-purple-200/50 dark:group-hover:shadow-purple-900/10',
        };
      case 'amber':
        return {
          card: 'bg-amber-50/30 border-amber-100 dark:bg-[#20170f]/60 dark:border-amber-950/40 shadow-amber-100/10 dark:shadow-amber-950/5',
          header: 'bg-amber-50/70 dark:bg-[#18110b]/80 border-amber-100/50 dark:border-amber-950/20',
          titleText: 'text-amber-700 dark:text-amber-400',
          promptPath: 'text-amber-600 dark:text-amber-400',
          promptArrow: 'text-amber-500 dark:text-amber-500',
          badge: 'bg-amber-100/80 text-amber-800 dark:bg-amber-950/80 dark:text-amber-400 border border-amber-200/40 dark:border-amber-800/30',
          valueText: 'text-amber-900 dark:text-amber-100',
          footerText: 'text-amber-700/70 dark:text-amber-400/60',
          glow: 'group-hover:border-amber-300 dark:group-hover:border-amber-800/60 group-hover:shadow-amber-200/50 dark:group-hover:shadow-amber-900/10',
        };
      case 'rose':
        return {
          card: 'bg-rose-50/40 border-rose-100 dark:bg-[#230f14]/60 dark:border-rose-950/40 shadow-rose-100/10 dark:shadow-rose-950/5',
          header: 'bg-rose-50/80 dark:bg-[#1a0b0f]/80 border-rose-100/50 dark:border-rose-950/20',
          titleText: 'text-rose-700 dark:text-rose-400',
          promptPath: 'text-rose-600 dark:text-rose-400',
          promptArrow: 'text-rose-500 dark:text-rose-500',
          badge: 'bg-rose-100/80 text-rose-800 dark:bg-rose-950/80 dark:text-rose-400 border border-rose-200/40 dark:border-rose-800/30',
          valueText: 'text-rose-900 dark:text-rose-100',
          footerText: 'text-rose-700/70 dark:text-rose-400/60',
          glow: 'group-hover:border-rose-300 dark:group-hover:border-rose-800/60 group-hover:shadow-rose-200/50 dark:group-hover:shadow-rose-900/10',
        };
      case 'cyan':
        return {
          card: 'bg-cyan-50/40 border-cyan-100 dark:bg-[#0b1d24]/60 dark:border-cyan-950/40 shadow-cyan-100/10 dark:shadow-cyan-950/5',
          header: 'bg-cyan-50/80 dark:bg-[#08161b]/80 border-cyan-100/50 dark:border-cyan-950/20',
          titleText: 'text-cyan-700 dark:text-cyan-400',
          promptPath: 'text-cyan-600 dark:text-cyan-400',
          promptArrow: 'text-cyan-500 dark:text-cyan-500',
          badge: 'bg-cyan-100/80 text-cyan-800 dark:bg-cyan-950/80 dark:text-cyan-400 border border-cyan-200/40 dark:border-cyan-800/30',
          valueText: 'text-cyan-900 dark:text-cyan-100',
          footerText: 'text-cyan-700/70 dark:text-cyan-400/60',
          glow: 'group-hover:border-cyan-300 dark:group-hover:border-cyan-800/60 group-hover:shadow-cyan-200/50 dark:group-hover:shadow-cyan-900/10',
        };
      case 'blue':
      default:
        return {
          card: 'bg-blue-50/40 border-blue-100 dark:bg-[#0b1c2b]/60 dark:border-blue-950/40 shadow-blue-100/10 dark:shadow-blue-950/5',
          header: 'bg-blue-50/80 dark:bg-[#081520]/80 border-blue-100/50 dark:border-blue-950/20',
          titleText: 'text-blue-700 dark:text-blue-400',
          promptPath: 'text-blue-600 dark:text-blue-400',
          promptArrow: 'text-blue-500 dark:text-blue-500',
          badge: 'bg-blue-100/80 text-blue-800 dark:bg-blue-950/80 dark:text-blue-400 border border-blue-200/40 dark:border-blue-800/30',
          valueText: 'text-blue-900 dark:text-blue-100',
          footerText: 'text-blue-700/70 dark:text-blue-400/60',
          glow: 'group-hover:border-blue-300 dark:group-hover:border-blue-800/60 group-hover:shadow-blue-200/50 dark:group-hover:shadow-blue-900/10',
        };
    }
  });
}
