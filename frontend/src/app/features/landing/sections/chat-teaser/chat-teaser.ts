import { Component, ChangeDetectionStrategy } from '@angular/core';
import { LucideAngularModule, Bot, Send, CheckCircle2, Sparkles } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

@Component({
  selector: 'app-landing-chat',
  standalone: true,
  imports: [LucideAngularModule, RevealDirective],
  templateUrl: './chat-teaser.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingChatComponent {
  readonly Bot = Bot;
  readonly Send = Send;
  readonly CheckCircle2 = CheckCircle2;
  readonly Sparkles = Sparkles;

  readonly bullets = [
    'Explains how you are doing across every topic',
    'Recommends exactly what to learn next',
    'Cites the precise lessons and challenges',
  ];
}
