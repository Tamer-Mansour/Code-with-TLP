export interface RankInfo {
  tier: number;
  name: string;
  label: string;
  minScore: number;
  nextScore: number | null;
  gradientFrom: string;
  gradientTo: string;
  accentColor: string;
  glowColor: string;
  textColor: string;
  animated: boolean;
  icon: string;
}
