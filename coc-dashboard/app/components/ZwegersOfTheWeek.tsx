import { WeekStar } from '../lib/ranked';
import GameIcon from './GameIcon';
import LeagueBadge, { leagueName } from './LeagueBadge';

// Overview section: members who reached the ranked league we expect for their
// Town Hall during last week. Refreshes with the weekly ranked snapshot.
export default function ZwegersOfTheWeek({ weekOf, stars }: { weekOf: string; stars: WeekStar[] }) {
  return (
    <section className="coc-wood p-5 md:p-6 mb-6">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <GameIcon name="crown" size={44} className="drop-shadow-[0_3px_0_rgba(0,0,0,0.4)]" />
        <div>
          <h2 className="coc-text text-3xl leading-tight">Zwegers of the Week</h2>
          <p className="coc-text text-sm opacity-95">
            Reached their ranked benchmark in the week of {weekOf}
          </p>
        </div>
      </div>

      {stars.length === 0 ? (
        <p className="coc-parchment px-4 py-3 text-sm">
          Nobody reached a new benchmark last week. Next week it could be you!
        </p>
      ) : (
        <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {stars.map(s => {
            const margin = s.league - s.benchmark;
            return (
              <li key={s.tag} className="coc-parchment flex items-center gap-3 px-3 py-2.5">
                <LeagueBadge league={s.leagueTier} size="lg" showName={false} />
                <div className="min-w-0">
                  <p className="font-bold text-[#3a2410] truncate">{s.name}</p>
                  <p className="text-xs text-[#6b4a2a]">TH{s.townHall} · {leagueName(s.league)}</p>
                  <p className="text-xs text-green-800">
                    Up from {leagueName(s.previousLeague)}
                    {margin > 0 && ` · ${margin} above benchmark`}
                  </p>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
