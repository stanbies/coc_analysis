import GameIcon, { IconName } from './GameIcon';

// Pieces shared by the Wars and Capital graphs
// Series colours checked with the dataviz palette validator against the card
// surface: colour-blind safe and >= 3:1 contrast.
export const SURFACE = '#1e293b';
export const COLORS = { us: '#3987e5', behind: '#e66767', context: '#64748b' };
export const GRID = 'rgba(255, 255, 255, 0.08)';
export const AXIS_LINE = 'rgba(255, 255, 255, 0.15)';
export const TICK = { fill: '#94a3b8', fontSize: 12 };

// The same roles on the light panels of the Players tab (light steps of the
// same hues, validated against #f4f3ec)
export const LIGHT = {
  us: '#2a78d6',
  behind: '#e34948',
  context: '#9a998c',
  surface: '#f4f3ec',
  grid: 'rgba(0, 0, 0, 0.08)',
  axisLine: 'rgba(0, 0, 0, 0.2)',
  tick: { fill: '#6b6a5c', fontSize: 12 },
};

export interface TooltipRow { name: string; value: string; color: string }

// Values lead, series names follow, each keyed with a short line in its colour
export function TooltipBox({ title, rows }: { title: string; rows: TooltipRow[] }) {
  return (
    <div className="rounded-lg border border-white/10 bg-slate-950/95 px-3 py-2 text-sm shadow-lg">
      <p className="text-slate-400 text-xs mb-1">{title}</p>
      {rows.map(row => (
        <div key={row.name} className="flex items-center gap-2">
          <span className="inline-block w-3 h-0.5 rounded" style={{ background: row.color }} />
          <span className="text-white font-bold">{row.value}</span>
          <span className="text-slate-400 text-xs">{row.name}</span>
        </div>
      ))}
    </div>
  );
}

export function LineKey({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1.5 text-xs">
      <span className="inline-block w-4 h-0.5 rounded" style={{ background: color }} />
      {label}
    </span>
  );
}

export function ChartCard({ icon, title, subtitle, legend, light = false, children }: {
  icon: IconName;
  title: string;
  subtitle: string;
  legend?: React.ReactNode;
  // White panel like the Players tab instead of the dark card
  light?: boolean;
  children: React.ReactNode;
}) {
  return (
    <section className={light ? 'coc-panel-light p-5 md:p-6' : 'card p-5 md:p-6'}>
      <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2 mb-4">
        <div>
          <h2 className={`flex items-center gap-2 ${light ? 'coc-text text-2xl' : 'text-xl font-bold text-white'}`}>
            <GameIcon name={icon} size={28} /> {title}
          </h2>
          <p className={`text-sm mt-1 ${light ? 'text-[#6b6a5c]' : 'text-slate-400'}`}>{subtitle}</p>
        </div>
        {legend && <div className="flex flex-wrap items-center gap-x-4 gap-y-1 pt-1">{legend}</div>}
      </div>
      {children}
    </section>
  );
}
