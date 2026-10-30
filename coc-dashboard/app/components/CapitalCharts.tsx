'use client';

import { Bar, BarChart, CartesianGrid, LabelList, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { RaidMemberResult, RaidPoint } from '../lib/capital';
import { AXIS_LINE, COLORS, ChartCard, GRID, SURFACE, TICK, TooltipBox } from './ChartParts';

const fmt = (n: number) => n.toLocaleString('en-US');
const compact = (n: number) => (n >= 1000 ? `${Math.round(n / 1000)}K` : `${n}`);

function raidTooltip(raid: RaidPoint) {
  return (
    <TooltipBox
      title={`Raid weekend of ${raid.date}`}
      rows={[
        { name: 'capital gold looted', value: fmt(raid.loot), color: COLORS.us },
        { name: 'attacks', value: fmt(raid.attacks), color: 'transparent' },
        { name: 'loot per attack', value: fmt(raid.lootPerAttack), color: 'transparent' },
        { name: 'raids completed', value: `${raid.raidsCompleted}`, color: 'transparent' },
        { name: 'districts destroyed', value: `${raid.districtsDestroyed}`, color: 'transparent' },
      ]}
    />
  );
}

const tooltipFor = ({ active, payload }: { active?: boolean; payload?: readonly { payload?: unknown }[] }) => {
  const raid = active ? (payload?.[0]?.payload as RaidPoint | undefined) : undefined;
  return raid ? raidTooltip(raid) : null;
};

// Label only the latest weekend and the best one, never every bar
function selectiveLabel(raids: RaidPoint[], key: 'loot' | 'raidsCompleted', format: (n: number) => string) {
  const last = raids.length - 1;
  const best = raids.reduce((bi, r, i) => (r[key] > raids[bi][key] ? i : bi), 0);
  return function SelectiveLabel(props: { x?: unknown; y?: unknown; width?: unknown; index?: number; value?: unknown }) {
    const { index } = props;
    if (index !== last && index !== best) return <g />;
    const x = Number(props.x) + Number(props.width) / 2;
    return (
      <text x={x} y={Number(props.y) - 6} textAnchor="middle" fill="#e2e8f0" fontSize={12}>
        {format(Number(props.value))}
      </text>
    );
  };
}

export function CapitalLootCard({ raids }: { raids: RaidPoint[] }) {
  return (
    <ChartCard icon="capitalGold" title="Capital gold per raid weekend"
               subtitle={`Total loot of the clan · last ${raids.length} finished weekends`}>
      <div className="h-60">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={raids} margin={{ top: 20, right: 12, bottom: 0, left: -4 }}>
            <CartesianGrid vertical={false} stroke={GRID} />
            <XAxis dataKey="date" tickLine={false} axisLine={{ stroke: AXIS_LINE }} tick={TICK} />
            <YAxis tickFormatter={compact} tickLine={false} axisLine={false} tick={TICK} width={52} />
            <Tooltip cursor={{ fill: 'rgba(255, 255, 255, 0.06)' }} content={tooltipFor} />
            <Bar dataKey="loot" fill={COLORS.us} maxBarSize={24} radius={[4, 4, 0, 0]} isAnimationActive={false}>
              <LabelList dataKey="loot" content={selectiveLabel(raids, 'loot', compact)} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}

export function LootPerAttackCard({ raids }: { raids: RaidPoint[] }) {
  const last = raids.length - 1;
  return (
    <ChartCard icon="raid" title="Loot per attack" subtitle="Capital gold per raid attack, higher means better attacks">
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={raids} margin={{ top: 8, right: 52, bottom: 0, left: -4 }}>
            <CartesianGrid vertical={false} stroke={GRID} />
            <XAxis dataKey="date" tickLine={false} axisLine={{ stroke: AXIS_LINE }} tick={TICK} minTickGap={24} />
            <YAxis domain={['dataMin - 200', 'dataMax + 200']} tickFormatter={v => fmt(Math.round(v / 100) * 100)}
                   tickLine={false} axisLine={false} tick={TICK} width={52} />
            <Tooltip cursor={{ stroke: 'rgba(255, 255, 255, 0.3)', strokeWidth: 1 }} content={tooltipFor} />
            <Line
              type="monotone"
              dataKey="lootPerAttack"
              stroke={COLORS.us}
              strokeWidth={2}
              dot={{ r: 4, fill: COLORS.us, stroke: SURFACE, strokeWidth: 2 }}
              activeDot={{ r: 6, stroke: SURFACE, strokeWidth: 2 }}
              isAnimationActive={false}
              label={({ x, y, index, value }) => (
                index === last
                  ? <text x={Number(x) + 10} y={Number(y)} dy={4} fill="#e2e8f0" fontSize={12}>{fmt(Number(value))}</text>
                  : <g />
              )}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}

export function RaidsCompletedCard({ raids }: { raids: RaidPoint[] }) {
  return (
    <ChartCard icon="districtHall" title="Raids completed" subtitle="Enemy capitals fully destroyed per weekend">
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={raids} margin={{ top: 20, right: 12, bottom: 0, left: -4 }}>
            <CartesianGrid vertical={false} stroke={GRID} />
            <XAxis dataKey="date" tickLine={false} axisLine={{ stroke: AXIS_LINE }} tick={TICK} minTickGap={24} />
            <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={TICK} width={52} />
            <Tooltip cursor={{ fill: 'rgba(255, 255, 255, 0.06)' }} content={tooltipFor} />
            <Bar dataKey="raidsCompleted" fill={COLORS.us} maxBarSize={24} radius={[4, 4, 0, 0]} isAnimationActive={false}>
              <LabelList dataKey="raidsCompleted" content={selectiveLabel(raids, 'raidsCompleted', n => `${n}`)} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}

// Ranked bars of every raider's loot, with their attacks used, then who didn't raid
export function LastRaidCard({ date, raiders, absent }: {
  date: string;
  raiders: RaidMemberResult[];
  absent: string[];
}) {
  const best = Math.max(1, ...raiders.map(r => r.loot));
  return (
    <ChartCard icon="raid" title="Last raid weekend"
               subtitle={`Weekend of ${date} · ${raiders.length} raiders · bars show capital gold looted`}>
      <ol className="space-y-1.5">
        {raiders.map((r, i) => {
          const missed = r.attacks < r.maxAttacks;
          return (
            <li key={r.tag} className="grid grid-cols-[1.5rem_minmax(5rem,10rem)_1fr_auto] items-center gap-2 sm:gap-3 text-sm">
              <span className="text-slate-500 text-right">{i + 1}</span>
              <span className="text-white truncate">{r.name}</span>
              <span className="flex items-center gap-2 min-w-0">
                <span className="flex-1 min-w-0">
                  <span className="block h-3 rounded-r" style={{ width: `${(r.loot / best) * 100}%`, background: COLORS.us }} />
                </span>
                <span className="text-slate-200 whitespace-nowrap tabular-nums">{fmt(r.loot)}</span>
              </span>
              <span className={`flex items-center gap-1 text-xs whitespace-nowrap ${missed ? 'text-amber-400' : 'text-slate-400'}`}>
                {missed && (
                  <span aria-hidden className="w-4 h-4 rounded-full bg-amber-400 text-slate-950 text-[10px] font-bold flex items-center justify-center">!</span>
                )}
                {r.attacks}/{r.maxAttacks}<span className="hidden sm:inline"> attacks</span>
              </span>
            </li>
          );
        })}
      </ol>
      {absent.length > 0 && (
        <div className="mt-5 pt-4 border-t border-white/10">
          <p className="text-sm text-slate-300 mb-2">Didn&apos;t raid ({absent.length})</p>
          <div className="flex flex-wrap gap-1.5">
            {absent.map(name => (
              <span key={name} className="text-xs text-slate-300 bg-white/5 border border-white/10 rounded-full px-2.5 py-0.5">
                {name}
              </span>
            ))}
          </div>
        </div>
      )}
    </ChartCard>
  );
}
