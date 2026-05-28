import {
  Component,
  OnInit,
  inject,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { LucideAngularModule } from 'lucide-angular';
import { AdminService } from '../../../core/services/admin.service';
import { AdminStats } from '../../../core/models/types';
import { TerminalCardComponent } from '../../../shared/components/terminal-card/terminal-card';

interface StatCard {
  label: string;
  key: keyof AdminStats;
  icon: string;
  themeColor: 'blue' | 'green' | 'purple' | 'amber' | 'rose' | 'cyan';
  promptPath: string;
  badgeText: string;
  footerText: string;
}

@Component({
  selector: 'app-admin-stats',
  standalone: true,
  templateUrl: './admin-stats.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [DecimalPipe, LucideAngularModule, TerminalCardComponent],
})
export class AdminStatsComponent implements OnInit {
  private readonly adminService = inject(AdminService);

  stats = signal<AdminStats | null>(null);
  loading = signal(true);
  error = signal(false);

  readonly statCards: StatCard[] = [
    {
      label: 'Total Users',
      key: 'users_total',
      icon: 'users',
      themeColor: 'blue',
      promptPath: '~/users/all',
      badgeText: 'Users',
      footerText: 'Registered accounts',
    },
    {
      label: 'Active Users',
      key: 'users_active',
      icon: 'activity',
      themeColor: 'cyan',
      promptPath: '~/users/active',
      badgeText: 'Active',
      footerText: 'Currently engaged',
    },
    {
      label: 'Students',
      key: 'students',
      icon: 'graduation-cap',
      themeColor: 'blue',
      promptPath: '~/users/students',
      badgeText: 'Students',
      footerText: 'Registered learners',
    },
    {
      label: 'Admins',
      key: 'admins',
      icon: 'shield',
      themeColor: 'purple',
      promptPath: '~/users/admins',
      badgeText: 'Admins',
      footerText: 'Staff credentials',
    },
    {
      label: 'Published Courses',
      key: 'courses_published',
      icon: 'book-open',
      themeColor: 'blue',
      promptPath: '~/catalog/courses',
      badgeText: 'Courses',
      footerText: 'Published courses',
    },
    {
      label: 'Exercises',
      key: 'exercises_published',
      icon: 'code-2',
      themeColor: 'purple',
      promptPath: '~/catalog/exercises',
      badgeText: 'Exercises',
      footerText: 'Coding exercises',
    },
    {
      label: 'Submissions',
      key: 'submissions',
      icon: 'send',
      themeColor: 'amber',
      promptPath: '~/sandbox/submissions',
      badgeText: 'Submissions',
      footerText: 'Total submission entries',
    },
    {
      label: 'Accepted',
      key: 'submissions_accepted',
      icon: 'check-circle-2',
      themeColor: 'green',
      promptPath: '~/sandbox/accepted',
      badgeText: 'Accepted',
      footerText: 'Successful answers',
    },
  ];

  ngOnInit(): void {
    this.adminService.getStats().subscribe({
      next: (data) => {
        this.stats.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set(true);
      },
    });
  }

  getStatValue(key: keyof AdminStats): number {
    return (this.stats()?.[key] as number) ?? 0;
  }
}
