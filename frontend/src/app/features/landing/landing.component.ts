import { Component, inject, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { LandingHeroComponent } from './sections/landing-hero/landing-hero';
import { LandingStatsComponent } from './sections/landing-stats/landing-stats';
import { LandingFeaturesComponent } from './sections/features/features';
import { LandingHowComponent } from './sections/how-it-works/how-it-works';
import { LandingCurriculumComponent } from './sections/curriculum/curriculum';
import { LandingPlaygroundComponent } from './sections/playground-teaser/playground-teaser';
import { LandingVisualizerComponent } from './sections/visualizer-teaser/visualizer-teaser';
import { LandingChatComponent } from './sections/chat-teaser/chat-teaser';
import { LandingRanksComponent } from './sections/ranks/ranks';
import { LandingTestimonialsComponent } from './sections/testimonials/testimonials';
import { LandingFaqComponent } from './sections/faq/faq';
import { LandingCtaComponent } from './sections/final-cta/final-cta';
import { LandingFooterComponent } from './sections/landing-footer/landing-footer';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [
    LandingHeroComponent,
    LandingStatsComponent,
    LandingFeaturesComponent,
    LandingHowComponent,
    LandingCurriculumComponent,
    LandingPlaygroundComponent,
    LandingVisualizerComponent,
    LandingChatComponent,
    LandingRanksComponent,
    LandingTestimonialsComponent,
    LandingFaqComponent,
    LandingCtaComponent,
    LandingFooterComponent,
  ],
  templateUrl: './landing.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  ngOnInit(): void {
    // Logged-in users skip the marketing page.
    if (this.auth.isAuthenticated()) {
      this.router.navigate([this.auth.isAdmin() ? '/admin' : '/dashboard']);
    }
  }
}
