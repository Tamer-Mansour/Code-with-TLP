import {
  Component,
  inject,
  signal,
  ChangeDetectionStrategy,
  HostListener,
} from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { NgClass } from '@angular/common';
import {
  LucideAngularModule,
  Code2, BookOpen, LayoutDashboard, ChevronDown,
  Menu, X, User, LogOut, Shield, BarChart2, Sun, Moon, Activity,
  Bot, Key, MessageCircleQuestion, Settings,
} from 'lucide-angular';
import { AuthService } from '../../../core/services/auth.service';
import { ThemeService } from '../../../core/services/theme.service';
import { UserSettingsService } from '../../../core/services/user-settings.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, NgClass, LucideAngularModule],
  templateUrl: './navbar.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NavbarComponent {
  readonly auth  = inject(AuthService);
  readonly theme = inject(ThemeService);
  readonly settingsService = inject(UserSettingsService);

  readonly mobileOpen   = signal(false);
  readonly dropdownOpen = signal(false);

  readonly Code2          = Code2;
  readonly BookOpen       = BookOpen;
  readonly LayoutDashboard = LayoutDashboard;
  readonly ChevronDown    = ChevronDown;
  readonly Menu           = Menu;
  readonly X              = X;
  readonly User           = User;
  readonly LogOut         = LogOut;
  readonly Shield         = Shield;
  readonly BarChart2      = BarChart2;
  readonly Sun            = Sun;
  readonly Moon           = Moon;
  readonly Activity       = Activity;
  readonly Bot            = Bot;
  readonly Key            = Key;
  readonly MessageCircleQuestion = MessageCircleQuestion;
  readonly Settings = Settings;

  toggleMobile(): void {
    this.mobileOpen.update(v => !v);
    if (this.dropdownOpen()) this.dropdownOpen.set(false);
  }

  toggleDropdown(): void { this.dropdownOpen.update(v => !v); }
  closeMobile(): void    { this.mobileOpen.set(false); }
  closeDropdown(): void  { this.dropdownOpen.set(false); }

  openPersonalization(): void {
    this.dropdownOpen.set(false);
    this.settingsService.openDrawer();
  }

  logout(): void {
    this.dropdownOpen.set(false);
    this.mobileOpen.set(false);
    this.auth.logout();
  }

  get userInitials(): string {
    const user = this.auth.currentUser();
    if (!user) return '?';
    const name = user.full_name || user.username || user.email;
    return name
      .split(/[\s@._-]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map(p => p[0].toUpperCase())
      .join('');
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(e: MouseEvent): void {
    const target = e.target as HTMLElement;
    if (!target.closest('[data-dropdown]')) {
      this.dropdownOpen.set(false);
    }
  }
}
