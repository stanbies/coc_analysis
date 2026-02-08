import { Platform } from 'react-native';

export const CoC = {
  background: '#0f172a',
  backgroundGradientStart: '#0f172a',
  backgroundGradientMid: '#1e1b4b',
  backgroundGradientEnd: '#0f172a',
  card: 'rgba(30, 41, 59, 0.9)',
  cardBorder: 'rgba(51, 65, 85, 0.5)',
  statCard: 'rgba(30, 41, 59, 0.95)',
  statCardBorder: 'rgba(249, 115, 22, 0.2)',
  primary: '#f97316',
  primaryLight: '#fb923c',
  text: '#f8fafc',
  textSecondary: '#94a3b8',
  textMuted: '#64748b',
  textDark: '#475569',
  border: '#334155',
  yellow: '#eab308',
  yellowBright: '#facc15',
  green: '#22c55e',
  greenLight: '#4ade80',
  red: '#ef4444',
  redLight: '#f87171',
  cyan: '#22d3ee',
  purple: '#a855f7',
  blue: '#3b82f6',
  amber: '#f59e0b',
  amberDark: '#d97706',
  slate700: '#334155',
  slate800: '#1e293b',
  slate900: '#0f172a',
};

export const RushColors: Record<string, string> = {
  maxed: '#22c55e',
  slight: '#84cc16',
  moderate: '#eab308',
  rushed: '#f97316',
  severe: '#ef4444',
  default: '#64748b',
};

export function getRushColor(status: string): string {
  if (status.includes('Maxed')) return RushColors.maxed;
  if (status.includes('Slightly')) return RushColors.slight;
  if (status.includes('Moderately')) return RushColors.moderate;
  if (status.includes('Severely')) return RushColors.severe;
  if (status.includes('Rushed')) return RushColors.rushed;
  return RushColors.default;
}

export function getRoleIcon(role: string): string {
  switch (role) {
    case 'leader': return '👑';
    case 'coLeader': return '⭐';
    case 'admin': return '🛡️';
    default: return '👤';
  }
}

export function getRoleLabel(role: string): string {
  switch (role) {
    case 'leader': return '👑 Leader';
    case 'coLeader': return '⭐ Co-Leader';
    case 'admin': return '🛡️ Elder';
    default: return '👤 Member';
  }
}

export const THColors: Record<number, string> = {
  17: '#ef4444',
  16: '#f97316',
  15: '#eab308',
  14: '#84cc16',
  13: '#22c55e',
  12: '#14b8a6',
  11: '#06b6d4',
  10: '#3b82f6',
  9: '#8b5cf6',
  8: '#a855f7',
  7: '#d946ef',
};

export const Colors = {
  light: {
    text: '#11181C',
    background: '#fff',
    tint: '#f97316',
    icon: '#687076',
    tabIconDefault: '#687076',
    tabIconSelected: '#f97316',
  },
  dark: {
    text: '#ECEDEE',
    background: '#0f172a',
    tint: '#f97316',
    icon: '#9BA1A6',
    tabIconDefault: '#64748b',
    tabIconSelected: '#f97316',
  },
};

export const Fonts = Platform.select({
  ios: {
    sans: 'system-ui',
    serif: 'ui-serif',
    rounded: 'ui-rounded',
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    rounded: "'SF Pro Rounded', 'Hiragino Maru Gothic ProN', Meiryo, 'MS PGothic', sans-serif",
    mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
  },
});
