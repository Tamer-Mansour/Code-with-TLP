import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule, Activity } from 'lucide-angular';
import { getVizByCategory, VizRegistryEntry } from '../core/registry';

@Component({
  selector: 'app-viz-catalog',
  standalone: true,
  imports: [RouterLink, LucideAngularModule],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class VizCatalogComponent {
  readonly Activity = Activity;

  readonly grouped: { category: string; entries: VizRegistryEntry[] }[] =
    Object.entries(getVizByCategory()).map(([category, entries]) => ({ category, entries }));

  /** Slice operations to max 5 for the folder "files". */
  getOps(entry: VizRegistryEntry): string[] {
    return entry.meta.operations.slice(0, 5);
  }

  /** Return the total ops count zero-padded to 2 digits. */
  padCount(entry: VizRegistryEntry): string {
    return String(entry.meta.operations.length).padStart(2, '0');
  }

  /** Return the file class index (1-based) for color assignment. */
  fileClass(index: number): string {
    return `file-${index + 1}`;
  }
}
