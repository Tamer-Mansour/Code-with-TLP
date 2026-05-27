import {
  Component, inject, signal, computed, OnInit, AfterViewInit, OnDestroy,
  ViewChild, ViewContainerRef, ChangeDetectionStrategy, Type,
} from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { LucideAngularModule, ArrowLeft, ChevronRight } from 'lucide-angular';
import { VizPlayerService } from '../core/viz-player.service';
import { VIZ_REGISTRY, VizRegistryEntry } from '../core/registry';
import { PlayerBarComponent } from '../shared/player-bar/player-bar.component';

@Component({
  selector: 'app-viz-page',
  standalone: true,
  imports: [RouterLink, LucideAngularModule, PlayerBarComponent],
  templateUrl: './viz-page.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class VizPageComponent implements OnInit, AfterViewInit, OnDestroy {
  private readonly route  = inject(ActivatedRoute);
  readonly player = inject(VizPlayerService);

  readonly ArrowLeft    = ArrowLeft;
  readonly ChevronRight = ChevronRight;

  readonly entry   = signal<VizRegistryEntry | null>(null);
  readonly notFound = signal(false);

  // Dynamic query — the host lives inside an @else block, so a static query
  // would resolve to undefined. It's available by ngAfterViewInit.
  @ViewChild('moduleHost', { read: ViewContainerRef })
  moduleHost?: ViewContainerRef;

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug') ?? '';
    const reg  = VIZ_REGISTRY[slug];
    if (!reg) {
      this.notFound.set(true);
      return;
    }
    this.entry.set(reg);
    this.player.setFrames([]);
  }

  async ngAfterViewInit(): Promise<void> {
    const reg = this.entry();
    if (!reg || !this.moduleHost) return;
    const ComponentClass = await reg.loadComponent();
    this.moduleHost.clear();
    this.moduleHost.createComponent(ComponentClass as Type<unknown>);
  }

  ngOnDestroy(): void {
    this.player.pause();
  }

  readonly currentNote = computed(() => this.player.currentFrame()?.note ?? '');

  readonly pseudoLines = computed<string[]>(() => {
    const entry = this.entry();
    return entry ? (PSEUDOCODE_MAP[entry.meta.slug] ?? []) : [];
  });

  readonly activeLine = computed(() => this.player.currentFrame()?.pseudoLine ?? -1);
}

/**
 * Per-module pseudocode lines shown in the side panel.
 * Keyed by slug, each string is one line.
 */
const PSEUDOCODE_MAP: Record<string, string[]> = {
  'array-sorting': [
    'procedure bubbleSort(A)',
    '  for i = 0 to n-2',
    '    for j = 0 to n-2-i',
    '      if A[j] > A[j+1]',
    '        swap(A[j], A[j+1])',
    '  end procedure',
    '',
    'procedure selectionSort(A)',
    '  for i = 0 to n-2',
    '    min ← i',
    '    for j = i+1 to n-1',
    '      if A[j] < A[min]  →  min ← j',
    '    swap(A[i], A[min])',
    '  end procedure',
    '',
    'procedure insertionSort(A)',
    '  for i = 1 to n-1',
    '    key ← A[i];  j ← i',
    '    while j > 0 and A[j-1] > key',
    '      A[j] ← A[j-1];  j ← j-1',
    '    A[j] ← key',
    '  end procedure',
  ],
  'bst': [
    'procedure insert(root, value)',
    '  if root = nil  →  return new Node(value)',
    '  if value < root.key',
    '    root.left ← insert(root.left, value)',
    '  else if value > root.key',
    '    root.right ← insert(root.right, value)',
    '  return root',
    '',
    'procedure search(root, value)',
    '  if root = nil  →  return NOT FOUND',
    '  if value = root.key  →  return root',
    '  if value < root.key',
    '    return search(root.left, value)',
    '  return search(root.right, value)',
    '',
    'procedure inorder(root)',
    '  if root = nil  →  return',
    '  inorder(root.left)',
    '  visit(root)',
    '  inorder(root.right)',
  ],
};
