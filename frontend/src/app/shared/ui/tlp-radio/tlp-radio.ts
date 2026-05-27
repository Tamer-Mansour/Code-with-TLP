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
  selector: 'tlp-radio',
  standalone: true,
  imports: [],
  templateUrl: './tlp-radio.html',
  styleUrl: './tlp-radio.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => TlpRadioComponent),
      multi: true,
    },
  ],
})
export class TlpRadioComponent implements ControlValueAccessor {
  /** The value this radio represents. */
  @Input() value: unknown = null;
  /** Label text. */
  @Input() label = '';
  /** Unique id for accessibility. */
  @Input() inputId = `tlp-rd-${Math.random().toString(36).slice(2, 7)}`;
  /** Optional name attribute for native grouping. */
  @Input() name = '';

  private readonly cdr = inject(ChangeDetectorRef);

  /** Currently selected value from the form model. */
  private modelValue: unknown = null;

  readonly selected = signal(false);
  readonly disabled = signal(false);
  readonly focused = signal(false);

  private onChange: (v: unknown) => void = () => {};
  private onTouched: () => void = () => {};

  writeValue(value: unknown): void {
    this.modelValue = value;
    this.selected.set(value === this.value);
    this.cdr.markForCheck();
  }

  registerOnChange(fn: (v: unknown) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled.set(isDisabled);
    this.cdr.markForCheck();
  }

  select(): void {
    if (this.disabled() || this.selected()) return;
    this.selected.set(true);
    this.onChange(this.value);
    this.onTouched();
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === ' ' || event.key === 'Enter') {
      event.preventDefault();
      this.select();
    }
  }

  onFocus(): void  { this.focused.set(true); }
  onBlur(): void   { this.focused.set(false); this.onTouched(); }
}
