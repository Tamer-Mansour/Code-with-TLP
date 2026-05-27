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
  selector: 'tlp-checkbox',
  standalone: true,
  imports: [],
  templateUrl: './tlp-checkbox.html',
  styleUrl: './tlp-checkbox.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => TlpCheckboxComponent),
      multi: true,
    },
  ],
})
export class TlpCheckboxComponent implements ControlValueAccessor {
  /** Label rendered next to the box. Leave empty to provide label via slot. */
  @Input() label = '';
  /** Unique id for accessibility; auto-generated if omitted. */
  @Input() inputId = `tlp-cb-${Math.random().toString(36).slice(2, 7)}`;
  /** Additional CSS classes on the host wrapper. */
  @Input() class = '';

  private readonly cdr = inject(ChangeDetectorRef);

  readonly checked = signal(false);
  readonly disabled = signal(false);
  readonly focused = signal(false);

  private onChange: (v: boolean) => void = () => {};
  private onTouched: () => void = () => {};

  writeValue(value: boolean): void {
    this.checked.set(!!value);
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
    this.checked.update((v) => !v);
    this.onChange(this.checked());
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
