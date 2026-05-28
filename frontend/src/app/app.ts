import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './shared/components/navbar/navbar';
import { ToastContainerComponent } from './shared/components/toast-container/toast-container';
import { PersonalizationComponent } from './features/profile/personalization/personalization.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    NavbarComponent,
    ToastContainerComponent,
    PersonalizationComponent,
  ],
  template: `
    <app-navbar />
    <main class="pt-14 min-h-dvh bg-app-bg">
      <router-outlet />
    </main>
    <app-toast-container />
    <app-personalization />
  `,
})
export class App {}
