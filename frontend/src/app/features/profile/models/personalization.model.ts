import type { ColorScheme, FontFamily } from '../../../core/models/types';

export interface ColorOption {
  value: ColorScheme;
  label: string;
  hex: string;
}

export interface FontOption {
  value: FontFamily;
  label: string;
  preview: string;
}
