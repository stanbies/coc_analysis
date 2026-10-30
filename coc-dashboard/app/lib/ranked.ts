import { LeagueTier, Player, RankedWeek } from '../types';
import { leagueNumber } from '../components/LeagueBadge';

export interface ClanWeekPoint {
  week: string;
  date: string; // Monday the week started, e.g. "26 Oct"
  avgLeague: number | null; // average over ranked members
  ranked: number;
  atBenchmark: number; // members at or above the benchmark for their Town Hall
  measured: number; // ranked members with a known Town Hall
  atBenchmarkPct: number | null;
}

export interface BenchmarkDot {
  tag: string;
  name: string;
  townHall: number;
  league: number;
  benchmark: number;
}

export interface MissedAttacks {
  tag: string;
  name: string;
  attacks: number;
  maxAttacks: number;
  placement: number | null;
}

const round1 = (n: number) => Math.round(n * 10) / 10;

function weekDate(start: string): string {
  return new Date(`${start}T00:00:00Z`).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', timeZone: 'UTC' });
}

// Benchmark for a Town Hall, or for the closest lower one listed (same rule as api/ranked.py)
export function benchmarkFor(benchmarks: Record<string, number>, townHall: number): number | null {
  const lower = Object.keys(benchmarks).map(Number).filter(th => th <= townHall);
  return lower.length ? benchmarks[String(Math.max(...lower))] : null;
}

// Clan-wide ranked progress per week. Weeks backfilled from league history
// don't know the Town Hall then, so those fall back to the member's current one.
export function clanRankedSeries(history: RankedWeek[], players: Player[], benchmarks: Record<string, number>): ClanWeekPoint[] {
  const currentTownHall = new Map(players.map(p => [p.tag, p.townHallLevel]));
  return history.map(week => {
    const entries = Object.entries(week.players).filter(([, p]) => p && p.league > 0);
    let atBenchmark = 0;
    let measured = 0;
    for (const [tag, p] of entries) {
      const townHall = p?.townHallLevel ?? currentTownHall.get(tag);
      const benchmark = townHall ? benchmarkFor(benchmarks, townHall) : null;
      if (!p || benchmark === null) continue;
      measured += 1;
      if (p.league >= benchmark) atBenchmark += 1;
    }
    const total = entries.reduce((sum, [, p]) => sum + (p?.league ?? 0), 0);
    return {
      week: week.week,
      date: weekDate(week.start),
      avgLeague: entries.length ? round1(total / entries.length) : null,
      ranked: entries.length,
      atBenchmark,
      measured,
      atBenchmarkPct: measured ? round1((atBenchmark / measured) * 100) : null,
    };
  });
}

// Every member now, placed against the benchmark for their Town Hall
export function benchmarkDots(players: Player[], benchmarks: Record<string, number>): BenchmarkDot[] {
  return players.flatMap(p => {
    const benchmark = benchmarkFor(benchmarks, p.townHallLevel);
    return benchmark === null ? [] : [{
      tag: p.tag,
      name: p.name,
      townHall: p.townHallLevel,
      league: leagueNumber(p.leagueTier),
      benchmark,
    }];
  });
}

// League per week for one member, null where they weren't recorded
export function playerLeagues(history: RankedWeek[], tag: string): (number | null)[] {
  return history.map(week => week.players[tag]?.league ?? null);
}

// The most recent finished week: who left ranked attacks unused
export function lastFinishedWeek(history: RankedWeek[], players: Player[]) {
  const week = [...history].reverse().find(w => Object.values(w.players).some(p => p?.result));
  if (!week) return null;
  const names = new Map(players.map(p => [p.tag, p.name]));
  const results = Object.entries(week.players).flatMap(([tag, p]) =>
    p?.result && names.has(tag) ? [{ tag, name: names.get(tag)!, ...p.result }] : []);
  const missed: MissedAttacks[] = results
    .filter(r => r.maxAttacks !== null && r.attacks < r.maxAttacks)
    .map(r => ({ tag: r.tag, name: r.name, attacks: r.attacks, maxAttacks: r.maxAttacks!, placement: r.placement }))
    .sort((a, b) => (b.maxAttacks - b.attacks) - (a.maxAttacks - a.attacks) || a.name.localeCompare(b.name));
  return { date: weekDate(week.start), played: results.length, complete: results.length - missed.length, missed };
}

export interface WeekStar {
  tag: string;
  name: string;
  townHall: number;
  league: number;
  leagueTier: LeagueTier | null; // for the league icon
  benchmark: number;
  previousLeague: number;
}

// Members who reached the benchmark for their Town Hall through last week's
// ranked results: below it in the second-newest recorded week, at or above it
// in the newest. Leagues only change at the Monday reset, so this list changes
// once a week, when the weekly ranked snapshot lands in the export.
export function zwegersOfTheWeek(players: Player[], history: RankedWeek[], benchmarks: Record<string, number>) {
  if (history.length < 2) return null;
  const [previous, latest] = history.slice(-2);
  const stars: WeekStar[] = players
    .flatMap(p => {
      const now = latest.players[p.tag];
      const before = previous.players[p.tag];
      if (!now || !before) return [];
      const townHall = now.townHallLevel ?? p.townHallLevel;
      const benchmark = benchmarkFor(benchmarks, townHall);
      if (benchmark === null || now.league < benchmark || before.league >= benchmark) return [];
      return [{
        tag: p.tag,
        name: p.name,
        townHall,
        league: now.league,
        leagueTier: p.leagueTier ?? null,
        benchmark,
        previousLeague: before.league,
      }];
    })
    .sort((a, b) => (b.league - b.benchmark) - (a.league - a.benchmark) || b.league - a.league);
  return { weekOf: weekDate(previous.start), stars };
}
