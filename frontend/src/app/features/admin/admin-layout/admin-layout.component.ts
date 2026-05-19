import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
} from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../../../core/services/auth.service';

interface NavItem {
  label: string;
  icon: string;
  route: string;
}

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  templateUrl: './admin-layout.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, RouterLinkActive, RouterOutlet, LucideAngularModule],
})
export class AdminLayoutComponent {
  private readonly auth = inject(AuthService);

  sidebarOpen = signal(true);

  readonly navItems: NavItem[] = [
    { label: 'Dashboard',   icon: 'bar-chart-2',  route: '/admin/stats' },
    { label: 'Users',       icon: 'users',         route: '/admin/users' },
    { label: 'Courses',     icon: 'book-open',     route: '/admin/courses' },
    { label: 'Exercises',   icon: 'code-2',        route: '/admin/exercises' },
    { label: 'Submissions', icon: 'send',          route: '/admin/submissions' },
  ];

  toggleSidebar(): void {
    this.sidebarOpen.update((v) => !v);
  }

  logout(): void {
    this.auth.logout();
  }
}
