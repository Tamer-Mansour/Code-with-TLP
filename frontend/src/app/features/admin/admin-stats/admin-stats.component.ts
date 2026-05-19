import {
  Component,
  OnInit,
  inject,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import { NgClass, DecimalPipe } from '@angular/common';
import { LucideAngularModule } from 'lucide-angular';
import { AdminService } from '../../../core/services/admin.service';
import { AdminStats } from '../../../core/models/types';

interface StatCard {
  label: string;
  key: keyof AdminStats;
  icon: string;
  colorClass: string;
  bgClass: string;
}

@Component({
  selector: 'app-admin-stats',
  standalone: true,
  templateUrl: './admin-stats.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgClass, DecimalPipe, LucideAngularModule],
})
export class AdminStatsComponent implements OnInit {
  private readonly adminService = inject(AdminService);

  stats = signal<AdminStats | null>(null);
  loading = signal(true);
  error = signal(false);

  readonly statCards: StatCard[] = [
    { label: 'Total Users',      key: 'users_total',          icon: 'users',          colorClass: 'text-brand',       bgClass: 'bg-brand/10' },
    { label: 'Students',         key: 'students',             icon: 'graduation-cap', colorClass: 'text-blue-400',    bgClass: 'bg-blue-500/10' },
    { label: 'Admins',           key: 'admins',               icon: 'shield',         colorClass: 'text-purple-400',  bgClass: 'bg-purple-500/10' },
    { label: 'Published Courses',key: 'courses_published',    icon: 'book-open',      colorClass: 'text-green-400',   bgClass: 'bg-green-500/10' },
    { label: 'Exercises',        key: 'exercises_published',  icon: 'code-2',         colorClass: 'text-yellow-400',  bgClass: 'bg-yellow-500/10' },
    { label: 'Submissions',      key: 'submissions',          icon: 'send',           colorClass: 'text-orange-400',  bgClass: 'bg-orange-500/10' },
    { label: 'Accepted',         key: 'submissions_accepted', icon: 'check-circle-2', colorClass: 'text-emerald-400', bgClass: 'bg-emerald-500/10' },
    { label: 'Active Users',     key: 'users_active',         icon: 'activity',       colorClass: 'text-cyan-400',    bgClass: 'bg-cyan-500/10' },
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
