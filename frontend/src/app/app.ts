import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './shared/components/navbar/navbar';
import { ToastContainerComponent } from './shared/components/toast-container/toast-container';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    NavbarComponent,
    ToastContainerComponent,
  ],
  template: `
    <app-navbar />
    <main class="pt-14 min-h-dvh bg-app-bg">
      <router-outlet />
    </main>
    <app-toast-container />
  `,
})
export class App {}
