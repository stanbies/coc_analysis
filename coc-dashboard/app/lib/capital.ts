import { CapitalRaid, Player } from '../types';
import { shortDate } from './coc-time';

export interface RaidPoint {
  key: string;
  date: string; // start of the raid weekend, e.g. "23 Oct"
  loot: number;
  attacks: number;
  raidsCompleted: number;
  districtsDestroyed: number;
  lootPerAttack: number;
}

export interface RaidMemberResult {
  tag: string;
  name: string;
  loot: number;
  attacks: number;
  maxAttacks: number; // 5, or 6 with the bonus attack
}

// Finished raid weekends, oldest first. The running weekend is left out: its
// numbers are partial until it ends.
export function raidSeries(raids: CapitalRaid[]): RaidPoint[] {
  return raids
    .filter(r => r.state === 'ended')
    .sort((a, b) => a.startTime.localeCompare(b.startTime))
    .map(r => ({
      key: r.startTime,
      date: shortDate(r.startTime),
      loot: r.capitalTotalLoot,
      attacks: r.totalAttacks,
      raidsCompleted: r.raidsCompleted,
      districtsDestroyed: r.enemyDistrictsDestroyed,
      lootPerAttack: r.totalAttacks ? Math.round(r.capitalTotalLoot / r.totalAttacks) : 0,
    }));
}

// Who raided in the last finished weekend (most loot first) and which current
// members didn't. The API only lists members for the most recent weekends.
export function lastRaidResults(raids: CapitalRaid[], players: Player[]) {
  const raid = raids.find(r => r.state === 'ended' && r.members?.length);
  if (!raid) return null;
  const raiders: RaidMemberResult[] = raid.members
    .map(m => ({
      tag: m.tag,
      name: m.name,
      loot: m.capitalResourcesLooted,
      attacks: m.attacks,
      maxAttacks: m.attackLimit + m.bonusAttackLimit,
    }))
    .sort((a, b) => b.loot - a.loot);
  const raided = new Set(raiders.map(r => r.tag));
  const absent = players.filter(p => !raided.has(p.tag)).map(p => p.name).sort((a, b) => a.localeCompare(b));
  return { date: shortDate(raid.startTime), raiders, absent };
}
