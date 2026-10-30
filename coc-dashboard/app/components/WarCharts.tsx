'use client';

import { useState } from 'react';
import {
  Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { WarPoint, WarResult } from '../lib/wars';
import { IconName } from './GameIcon';
import { AXIS_LINE, COLORS, ChartCard, GRID, LineKey, SURFACE, TICK, TooltipBox } from './ChartParts';

// Result colours are the status palette and always come with a W/L/T letter,
// never colour alone.
const RESULT_STYLE: Record<WarResult, { fill: string; ink: string; letter: string; label: string }> = {
  win: { fill: '#0ca30c', ink: '#ffffff', letter: 'W', label: 'Win' },
  lose: { fill: '#d03b3b', ink: '#ffffff', letter: 'L', label: 'Loss' },
  tie: { fill: '#fab219', ink: '#0b0b0b', letter: 'T', label: 'Tie' },
};

const warTitle = (war: WarPoint) => `${war.date} · vs ${war.opponent} · ${war.teamSize}v${war.teamSize}`;

// One block per war, oldest first; hover or focus a block to read that war
function ResultStrip({ wars }: { wars: WarPoint[] }) {
  const latest = wars.length - 1;
  const [active, setActive] = useState(latest);
  const war = wars[active] ?? wars[latest];
  const style = war.result ? RESULT_STYLE[war.result] : null;

  return (
    <div className="mt-5">
      <div className="flex flex-wrap gap-0.5" onMouseLeave={() => setActive(latest)}>
        {wars.map((w, i) => {
          const s = w.result ? RESULT_STYLE[w.result] : null;
          return (
            <button
              key={w.key}
              type="button"
              onMouseEnter={() => setActive(i)}
              onFocus={() => setActive(i)}
              aria-label={`${warTitle(w)}: ${s?.label ?? 'no result'}, ${w.ourStars} to ${w.theirStars} stars`}
              className={`w-5 h-6 rounded text-[10px] leading-none font-bold flex items-center justify-center transition-transform ${
                i === active ? '-translate-y-0.5 ring-2 ring-white/80' : 'hover:brightness-110'
              }`}
              style={{ background: s?.fill ?? '#475569', color: s?.ink ?? '#ffffff' }}
            >
              {s?.letter ?? '?'}
            </button>
          );
        })}
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
        {style && (
          <span className="coc-text text-xs px-2 py-0.5 rounded-full border-2 border-black/40"
                style={{ background: style.fill }}>
            {style.label}
          </span>
        )}
        <span className="text-slate-200">{warTitle(war)}</span>
        <span className="text-slate-400">
          {war.ourStars} - {war.theirStars} stars · {war.ourDestruction}% - {war.theirDestruction}% destruction
        </span>
      </div>
      <div className="mt-3 flex items-center gap-4 text-xs text-slate-300">
        {Object.values(RESULT_STYLE).map(s => (
          <span key={s.letter} className="flex items-center gap-1.5">
            <span className="w-3.5 h-3.5 rounded-sm text-[9px] font-bold flex items-center justify-center"
                  style={{ background: s.fill, color: s.ink }}>{s.letter}</span>
            {s.label}
          </span>
        ))}
      </div>
    </div>
  );
}

export function WarResultsCard({ wars }: { wars: WarPoint[] }) {
  const last = wars.length - 1;

  return (
    <ChartCard
      icon="threeStars"
      title="Results over time"
      subtitle={`Share of the last 10 wars won · ${wars.length} wars since ${wars[0].date}`}
    >
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={wars} margin={{ top: 8, right: 44, bottom: 0, left: -8 }}>
            <CartesianGrid vertical={false} stroke={GRID} />
            <XAxis dataKey="date" tickLine={false} axisLine={{ stroke: AXIS_LINE }} tick={TICK} minTickGap={32} />
            <YAxis domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} tickFormatter={v => `${v}%`}
                   tickLine={false} axisLine={false} tick={TICK} width={48} />
            <ReferenceLine y={50} stroke="rgba(255, 255, 255, 0.35)" />
            <Tooltip
              cursor={{ stroke: 'rgba(255, 255, 255, 0.3)', strokeWidth: 1 }}
              content={({ active, payload }) => {
                const war = active ? (payload?.[0]?.payload as WarPoint | undefined) : undefined;
                if (!war) return null;
                return (
                  <TooltipBox
                    title={warTitle(war)}
                    rows={[{
                      name: 'of the last 10 wars won',
                      value: war.winRate10 === null ? 'n/a' : `${war.winRate10}%`,
                      color: COLORS.us,
                    }]}
                  />
                );
              }}
            />
            <Line
              type="monotone"
              dataKey="winRate10"
              stroke={COLORS.us}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5, stroke: SURFACE, strokeWidth: 2 }}
              isAnimationActive={false}
              label={({ x, y, index, value }) => (
                index === last
                  ? <text x={Number(x) + 8} y={Number(y)} dy={4} fill="#e2e8f0" fontSize={12}>{value}%</text>
                  : <g />
              )}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <ResultStrip wars={wars} />
    </ChartCard>
  );
}

interface WarCompareCardProps {
  wars: WarPoint[];
  clanName: string;
  icon: IconName;
  title: string;
  subtitle: string;
  ourKey: 'ourDestruction';
  theirKey: 'theirDestruction';
}

// Our clan (accent) against each opponent (grey context) on one percentage scale
export function WarCompareCard({ wars, clanName, icon, title, subtitle, ourKey, theirKey }: WarCompareCardProps) {
  // Start the axis at the nearest 10 below the lowest value so the lines use the height
  const lowest = Math.min(...wars.flatMap(w => [w[ourKey], w[theirKey]]));
  const floor = Math.max(0, Math.floor(lowest / 10) * 10);

  return (
    <ChartCard
      icon={icon}
      title={title}
      subtitle={subtitle}
      legend={<><LineKey color={COLORS.us} label={clanName} /><LineKey color={COLORS.context} label="Opponent" /></>}
    >
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={wars} margin={{ top: 8, right: 12, bottom: 0, left: -8 }}>
            <CartesianGrid vertical={false} stroke={GRID} />
            <XAxis dataKey="date" tickLine={false} axisLine={{ stroke: AXIS_LINE }} tick={TICK} minTickGap={32} />
            <YAxis domain={[floor, 100]} tickFormatter={v => `${v}%`} tickLine={false} axisLine={false}
                   tick={TICK} width={48} />
            <Tooltip
              cursor={{ stroke: 'rgba(255, 255, 255, 0.3)', strokeWidth: 1 }}
              content={({ active, payload }) => {
                const war = active ? (payload?.[0]?.payload as WarPoint | undefined) : undefined;
                if (!war) return null;
                return (
                  <TooltipBox
                    title={warTitle(war)}
                    rows={[
                      { name: clanName, value: `${war[ourKey]}%`, color: COLORS.us },
                      { name: war.opponent, value: `${war[theirKey]}%`, color: COLORS.context },
                    ]}
                  />
                );
              }}
            />
            <Line type="monotone" dataKey={theirKey} name="Opponent" stroke={COLORS.context} strokeWidth={2}
                  dot={false} activeDot={{ r: 5, stroke: SURFACE, strokeWidth: 2 }} isAnimationActive={false} />
            <Line type="monotone" dataKey={ourKey} name={clanName} stroke={COLORS.us} strokeWidth={2}
                  dot={false} activeDot={{ r: 5, stroke: SURFACE, strokeWidth: 2 }} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}

// A column with a 4px rounded end away from the zero line and a square base on it
function MarginBar(props: { x?: number; y?: number; width?: number; height?: number; fill?: string; payload?: WarPoint }) {
  const { x = 0, y = 0, width = 0, height = 0, fill, payload } = props;
  if (!height) return <g />;
  const top = Math.min(y, y + height);
  const bottom = top + Math.abs(height);
  const right = x + width;
  const r = Math.min(4, width / 2, bottom - top);
  const path = (payload?.starMargin ?? 0) >= 0
    ? `M${x},${bottom} V${top + r} Q${x},${top} ${x + r},${top} H${right - r} Q${right},${top} ${right},${top + r} V${bottom} Z`
    : `M${x},${top} V${bottom - r} Q${x},${bottom} ${x + r},${bottom} H${right - r} Q${right},${bottom} ${right},${bottom - r} V${top} Z`;
  return <path d={path} fill={fill} />;
}

// Our stars minus the opponent's, one column per war: above zero we out-starred them
export function WarMarginCard({ wars, clanName }: { wars: WarPoint[]; clanName: string }) {
  // Symmetric axis in clean steps of 5, e.g. -50 / -25 / 0 / 25 / 50
  const step = Math.max(5, Math.ceil(Math.max(...wars.map(w => Math.abs(w.starMargin))) / 2 / 5) * 5);
  const ticks = [-2 * step, -step, 0, step, 2 * step];

  return (
    <ChartCard
      icon="star"
      title="Star difference per war"
      subtitle={`${clanName}'s stars minus the opponent's`}
      legend={
        <>
          <span className="flex items-center gap-1.5 text-xs text-slate-300">
            <span className="w-3 h-3 rounded-sm" style={{ background: COLORS.us }} /> More stars
          </span>
          <span className="flex items-center gap-1.5 text-xs text-slate-300">
            <span className="w-3 h-3 rounded-sm" style={{ background: COLORS.behind }} /> Fewer stars
          </span>
        </>
      }
    >
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={wars} margin={{ top: 8, right: 12, bottom: 0, left: -8 }} barCategoryGap={2}>
            <CartesianGrid vertical={false} stroke={GRID} />
            <XAxis dataKey="date" tickLine={false} axisLine={false} tick={TICK} minTickGap={32} />
            <YAxis domain={[ticks[0], ticks[4]]} ticks={ticks} tickLine={false} axisLine={false}
                   tick={TICK} width={48} />
            <ReferenceLine y={0} stroke={AXIS_LINE} />
            <Tooltip
              cursor={{ fill: 'rgba(255, 255, 255, 0.06)' }}
              content={({ active, payload }) => {
                const war = active ? (payload?.[0]?.payload as WarPoint | undefined) : undefined;
                if (!war) return null;
                const sign = war.starMargin > 0 ? '+' : '';
                return (
                  <TooltipBox
                    title={warTitle(war)}
                    rows={[
                      { name: 'star difference', value: `${sign}${war.starMargin}`, color: war.starMargin >= 0 ? COLORS.us : COLORS.behind },
                      { name: `${clanName} - opponent`, value: `${war.ourStars} - ${war.theirStars}`, color: 'transparent' },
                    ]}
                  />
                );
              }}
            />
            <Bar dataKey="starMargin" maxBarSize={24} isAnimationActive={false} shape={MarginBar}>
              {wars.map(w => <Cell key={w.key} fill={w.starMargin >= 0 ? COLORS.us : COLORS.behind} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
