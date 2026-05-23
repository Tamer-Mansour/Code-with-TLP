import {
  Component,
  Input,
  OnInit,
  inject,
  signal,
  ChangeDetectionStrategy,
  ViewEncapsulation,
} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { NgClass } from '@angular/common';

@Component({
  selector: 'app-tlp-loader',
  standalone: true,
  imports: [NgClass],
  templateUrl: './tlp-loader.html',
  styleUrl: './tlp-loader.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  // None so CSS rules reach SVG elements injected via innerHTML
  encapsulation: ViewEncapsulation.None,
})
export class TlpLoaderComponent implements OnInit {
  /** Whether the wave animation is active */
  @Input() loading = true;
  /** Overlay the entire viewport (true) or just sit inline (false) */
  @Input() overlay = true;
  /** Optional label shown below the logo */
  @Input() label = '';

  private readonly http = inject(HttpClient);
  private readonly sanitizer = inject(DomSanitizer);

  svgHtml = signal<SafeHtml>('');

  ngOnInit(): void {
    this.http.get('/tlp-logo.svg', { responseType: 'text' }).subscribe({
      next: (svg) => {
        // bypassSecurityTrustHtml is safe here: we load from our own /public assets
        this.svgHtml.set(this.sanitizer.bypassSecurityTrustHtml(svg));
      },
    });
  }
}
