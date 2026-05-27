import {
  Component,
  Input,
  forwardRef,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  inject,
  signal,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

@Component({
  selector: 'tlp-switch',
  standalone: true,
  imports: [],
  templateUrl: './tlp-switch.html',
  styleUrl: './tlp-switch.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => TlpSwitchComponent),
      multi: true,
    },
  ],
})
export class TlpSwitchComponent implements ControlValueAccessor {
  /** Label rendered next to the track. */
  @Input() label = '';
  /** Position of the label relative to the track. */
  @Input() labelPosition: 'before' | 'after' = 'after';
  /** Unique id for accessibility. */
  @Input() inputId = `tlp-sw-${Math.random().toString(36).slice(2, 7)}`;

  private readonly cdr = inject(ChangeDetectorRef);

  readonly on = signal(false);
  readonly disabled = signal(false);
  readonly focused = signal(false);

  private onChange: (v: boolean) => void = () => {};
  private onTouched: () => void = () => {};

  writeValue(value: boolean): void {
    this.on.set(!!value);
    this.cdr.markForCheck();
  }

  registerOnChange(fn: (v: boolean) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled.set(isDisabled);
    this.cdr.markForCheck();
  }

  toggle(): void {
    if (this.disabled()) return;
    this.on.update((v) => !v);
    this.onChange(this.on());
    this.onTouched();
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === ' ' || event.key === 'Enter') {
      event.preventDefault();
      this.toggle();
    }
  }

  onFocus(): void  { this.focused.set(true); }
  onBlur(): void   { this.focused.set(false); this.onTouched(); }
}
