export interface FeatureCard {
  icon: any;
  title: string;
  description: string;
  /** Tailwind col-span class at lg breakpoint */
  colSpan: string;
  /** Tailwind row-span class at lg breakpoint */
  rowSpan: string;
  /** Whether to apply the accent gradient ring */
  accent: boolean;
}
