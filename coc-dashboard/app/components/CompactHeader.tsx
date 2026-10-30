import { Clan } from '../types';

// Slim clan bar for the tabs other than the overview, which has the full banner
export default function CompactHeader({ clan }: { clan: Clan }) {
  return (
    <header className="coc-wood flex items-center gap-3 px-4 py-3 mb-6">
      {clan.badgeUrls?.medium && (
        // eslint-disable-next-line @next/next/no-img-element -- remote API image
        <img
          src={clan.badgeUrls.medium}
          alt=""
          className="w-12 h-12 md:w-14 md:h-14 shrink-0 drop-shadow-[0_3px_0_rgba(0,0,0,0.45)]"
        />
      )}
      <div className="min-w-0">
        <p className="coc-text text-2xl md:text-3xl leading-tight truncate">{clan.name}</p>
        <p className="coc-text text-xs opacity-90">{clan.tag} · Level {clan.clanLevel}</p>
      </div>
    </header>
  );
}
