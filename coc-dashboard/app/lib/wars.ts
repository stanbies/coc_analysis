import { WarLogEntry } from '../types';
import { shortDate } from './coc-time';

export type WarResult = 'win' | 'lose' | 'tie';

export interface WarPoint {
  key: string;
  date: string; // e.g. "29 Oct", in UTC so server and browser agree
  opponent: string;
  result: WarResult | null;
  teamSize: number;
  ourStars: number;
  theirStars: number;
  starMargin: number; // our stars minus theirs
  ourDestruction: number;
  theirDestruction: number;
  winRate10: number | null; // % of the last 10 wars won, null until there are 10
}

const ROLLING_WARS = 10;

const pct = (value: number) => Math.round(value * 10) / 10;

// Regular wars only, oldest first. CWL entries have no opponent and carry
// season totals, so they'd distort every per-war measure.
export function warSeries(warLog: WarLogEntry[]): WarPoint[] {
  const wars = warLog
    .filter(w => w.opponent?.tag)
    .sort((a, b) => a.endTime.localeCompare(b.endTime));

  return wars.map((war, i) => {
    const window = wars.slice(Math.max(0, i - ROLLING_WARS + 1), i + 1);
    const result = war.result === 'win' || war.result === 'lose' || war.result === 'tie' ? war.result : null;
    return {
      key: `${war.endTime}-${war.opponent.tag}`,
      date: shortDate(war.endTime),
      opponent: war.opponent.name ?? 'Unknown clan',
      result,
      teamSize: war.teamSize,
      ourStars: war.clan.stars,
      theirStars: war.opponent.stars,
      starMargin: war.clan.stars - war.opponent.stars,
      ourDestruction: pct(war.clan.destructionPercentage),
      theirDestruction: pct(war.opponent.destructionPercentage),
      winRate10: window.length < ROLLING_WARS
        ? null
        : pct((window.filter(w => w.result === 'win').length / ROLLING_WARS) * 100),
    };
  });
}
