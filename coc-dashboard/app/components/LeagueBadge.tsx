import { LeagueTier, Player } from '../types';
import GameIcon from './GameIcon';

// Ranked league tier ids are this base + the league number: 0 Unranked, 1-33
// Skeleton League 1 to Electro League 33, 34-36 Legend III/II/I. Same table as
// api/ranked.py.
const LEAGUE_TIER_BASE_ID = 105000000;
const LEAGUE_CREATURES = ['Skeleton', 'Barbarian', 'Archer', 'Wizard', 'Valkyrie', 'Witch',
  'Golem', 'P.E.K.K.A', 'Titan', 'Dragon', 'Electro'];
const LEGEND_LEAGUES: Record<number, string> = { 34: 'Legend III', 35: 'Legend II', 36: 'Legend I' };

export function leagueNumber(league: LeagueTier | null | undefined): number {
  return league?.id ? league.id - LEAGUE_TIER_BASE_ID : 0;
}

export function leagueName(number: number): string {
  if (LEGEND_LEAGUES[number]) return LEGEND_LEAGUES[number];
  if (number >= 1 && number <= LEAGUE_CREATURES.length * 3) {
    return `${LEAGUE_CREATURES[Math.floor((number - 1) / 3)]} League ${number}`;
  }
  return 'Unranked';
}

export function getLeagueIcon(league: LeagueTier | null | undefined): string | undefined {
  const icons = league?.iconUrls;
  return icons?.small ?? icons?.medium ?? icons?.large ?? icons?.tiny;
}

// Higher ranked league first, then more trophies this week. Tier ids increase
// with the league, so they double as the league order.
export function compareByLeague(a: Player, b: Player): number {
  return (b.leagueTier?.id ?? 0) - (a.leagueTier?.id ?? 0) || b.trophies - a.trophies;
}

interface LeagueBadgeProps {
  league: LeagueTier | null | undefined;
  size?: 'sm' | 'lg';
  showName?: boolean;
}

export default function LeagueBadge({ league, size = 'sm', showName = true }: LeagueBadgeProps) {
  const icon = getLeagueIcon(league);
  const iconClass = size === 'lg' ? 'w-12 h-12' : 'w-7 h-7';

  return (
    <span className="inline-flex items-center gap-2 min-w-0">
      {icon ? (
        <img src={icon} alt={league?.name ?? ''} className={`${iconClass} object-contain shrink-0`} />
      ) : (
        <span className={`${iconClass} shrink-0 flex items-center justify-center`}><GameIcon name="trophy" size={size === 'lg' ? 36 : 20} /></span>
      )}
      {showName && (
        <span className={league ? 'text-white' : 'text-slate-500'}>{league?.name ?? 'Unranked'}</span>
      )}
    </span>
  );
}
