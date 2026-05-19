import { Component, Input, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-spinner',
  standalone: true,
  imports: [],
  templateUrl: './spinner.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SpinnerComponent {
  @Input() size: 'sm' | 'md' | 'lg' = 'md';

  get sizeClasses(): string {
    switch (this.size) {
      case 'sm': return 'w-4 h-4 border-2';
      case 'lg': return 'w-8 h-8 border-[3px]';
      default:   return 'w-5 h-5 border-2';
    }
  }
}
