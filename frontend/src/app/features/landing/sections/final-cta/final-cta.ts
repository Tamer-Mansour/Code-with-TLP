import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RevealDirective } from '../../shared/reveal.directive';

@Component({
  selector: 'app-landing-cta',
  standalone: true,
  imports: [RouterLink, RevealDirective],
  templateUrl: './final-cta.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingCtaComponent {}
