import type { AdminStats } from '../../../core/models/types';

export interface StatCard {
  label: string;
  key: keyof AdminStats;
  icon: string;
  themeColor: 'blue' | 'green' | 'purple' | 'amber' | 'rose' | 'cyan';
  promptPath: string;
  badgeText: string;
  footerText: string;
}
