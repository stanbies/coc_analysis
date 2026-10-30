import GameIcon, { IconName } from './GameIcon';

interface TabHeroProps {
  // Colour scheme, matching the tab's scenery
  variant: 'players' | 'wars' | 'capital';
  icon: IconName;
  title: string;
  subtitle?: React.ReactNode;
  children: React.ReactNode;
}

// The top section of a tab: big icon and title, then a row of HeroStats
export default function TabHero({ variant, icon, title, subtitle, children }: TabHeroProps) {
  return (
    <section className={`coc-hero coc-hero-${variant} p-5 md:p-6 mb-6`}>
      <div className="flex items-center gap-4 mb-5">
        <GameIcon name={icon} size={64} className="drop-shadow-[0_4px_0_rgba(0,0,0,0.4)]" />
        <div className="min-w-0">
          <h2 className="coc-text text-3xl md:text-4xl leading-tight">{title}</h2>
          {subtitle && <div className="coc-text text-sm mt-1 opacity-95">{subtitle}</div>}
        </div>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3">{children}</div>
    </section>
  );
}

interface HeroStatProps {
  icon: IconName;
  // An image from the API (e.g. a league icon) shown instead of the game icon
  imageUrl?: string;
  label: string;
  value: React.ReactNode;
  detail?: React.ReactNode;
}

export function HeroStat({ icon, imageUrl, label, value, detail }: HeroStatProps) {
  return (
    <div className="coc-plaque flex flex-col sm:flex-row items-start sm:items-center gap-1 sm:gap-3 p-2.5 sm:p-3 min-w-0">
      {imageUrl
        // eslint-disable-next-line @next/next/no-img-element -- remote API image
        ? <img src={imageUrl} alt="" width={36} height={36} className="shrink-0 object-contain" />
        : <GameIcon name={icon} size={36} />}
      <div className="min-w-0">
        <p className="coc-text text-xs opacity-90">{label}</p>
        <p className="coc-text text-base sm:text-xl leading-tight break-words">{value}</p>
        {detail && <p className="coc-text text-[11px] opacity-85 truncate">{detail}</p>}
      </div>
    </div>
  );
}
