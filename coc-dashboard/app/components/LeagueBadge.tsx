import { LeagueTier, Player } from '../types';

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
        <span className={`${iconClass} shrink-0 flex items-center justify-center`}>🏆</span>
      )}
      {showName && (
        <span className={league ? 'text-white' : 'text-slate-500'}>{league?.name ?? 'Unranked'}</span>
      )}
    </span>
  );
}
