import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule, Sun, Moon } from 'lucide-angular';
import { ThemeService } from '../../../../core/services/theme.service';

@Component({
  selector: 'app-landing-footer',
  standalone: true,
  imports: [RouterLink, LucideAngularModule],
  templateUrl: './landing-footer.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingFooterComponent {
  readonly theme = inject(ThemeService);
  readonly Sun = Sun;
  readonly Moon = Moon;
  readonly year = new Date().getFullYear();

  readonly columns = [
    { title: 'Product', links: [
      { label: 'Courses', path: '/catalog' },
      { label: 'Challenges', path: '/exercises' },
      { label: 'Dashboard', path: '/dashboard' },
    ]},
    { title: 'Account', links: [
      { label: 'Log in', path: '/login' },
      { label: 'Sign up', path: '/register' },
      { label: 'Profile', path: '/profile' },
    ]},
  ];
}
