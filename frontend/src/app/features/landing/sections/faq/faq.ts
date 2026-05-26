import { Component, signal, ChangeDetectionStrategy } from '@angular/core';
import { LucideAngularModule, ChevronDown } from 'lucide-angular';
import { RevealDirective } from '../../shared/reveal.directive';

@Component({
  selector: 'app-landing-faq',
  standalone: true,
  imports: [LucideAngularModule, RevealDirective],
  templateUrl: './faq.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingFaqComponent {
  readonly ChevronDown = ChevronDown;
  readonly openIndex = signal<number | null>(0);

  readonly items = [
    { q: 'Is Code with TLP free?', a: 'Yes — the platform is free. For TLP Chat (the AI assistant) you bring your own API key, so you only ever pay your model provider directly.' },
    { q: 'Which programming languages can I use?', a: 'Challenges run in Python, JavaScript, TypeScript, Java, and C# — right in the browser, auto-graded against test cases.' },
    { q: 'Do I need to install anything?', a: 'No. Everything runs in your browser — the editor, the code runner, and the visualizers.' },
    { q: 'What will I learn?', a: 'A full A-to-Z computer-science curriculum: foundations, data structures & algorithms, systems (OS, architecture, networks), theory, software engineering, AI/ML, web, and databases.' },
    { q: 'How does the AI assistant work?', a: 'TLP Chat uses retrieval over your own progress and the course content (RAG), and supports your choice of model — GPT, Gemini, Claude, DeepSeek, Qwen, and more — via your own key.' },
    { q: 'Is my code and data private?', a: 'Your code runs sandboxed, and any AI calls use your own API key and go directly to the provider you choose.' },
  ];

  toggle(i: number): void {
    this.openIndex.set(this.openIndex() === i ? null : i);
  }
}
