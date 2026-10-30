'use client';

import { useState } from 'react';
import { Bar, BarChart, CartesianGrid, LabelList, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { BenchmarkDot, ClanWeekPoint, MissedAttacks } from '../lib/ranked';
import { ChartCard, LIGHT, TooltipBox } from './ChartParts';
import { leagueName } from './LeagueBadge';

const tooltipFor = ({ active, payload }: { active?: boolean; payload?: readonly { payload?: unknown }[] }) => {
  const week = active ? (payload?.[0]?.payload as ClanWeekPoint | undefined) : undefined;
  if (!week) return null;
  return (
    <TooltipBox
      title={`Week of ${week.date}`}
      rows={[
        {
          name: week.avgLeague === null ? 'no ranked members' : `average · ${leagueName(Math.round(week.avgLeague))}`,
          value: week.avgLeague === null ? 'n/a' : `${week.avgLeague}`,
          color: LIGHT.us,
        },
        { name: `of ${week.measured} at or above benchmark`, value: `${week.atBenchmark}`, color: 'transparent' },
        { name: 'ranked members', value: `${week.ranked}`, color: 'transparent' },
      ]}
    />
  );
};

export function RankedTrendCard({ weeks }: { weeks: ClanWeekPoint[] }) {
  const values = weeks.flatMap(w => (w.avgLeague === null ? [] : [w.avgLeague]));
  const low = Math.floor(Math.min(...values)) - 1;
  const high = Math.ceil(Math.max(...values)) + 1;
  const last = weeks.length - 1;

  return (
    <ChartCard light icon="trophy" title="Average ranked league"
               subtitle={`League number averaged over ranked members · ${weeks.length} weeks`}>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={weeks} margin={{ top: 8, right: 44, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke={LIGHT.grid} />
            <XAxis dataKey="date" tickLine={false} axisLine={{ stroke: LIGHT.axisLine }} tick={LIGHT.tick} minTickGap={24} />
            <YAxis domain={[low, high]} allowDecimals={false} tickLine={false} axisLine={false} tick={LIGHT.tick} width={44} />
            <Tooltip cursor={{ stroke: 'rgba(0, 0, 0, 0.25)', strokeWidth: 1 }} content={tooltipFor} />
            <Line
              type="monotone"
              dataKey="avgLeague"
              stroke={LIGHT.us}
              strokeWidth={2}
              dot={{ r: 4, fill: LIGHT.us, stroke: LIGHT.surface, strokeWidth: 2 }}
              activeDot={{ r: 6, stroke: LIGHT.surface, strokeWidth: 2 }}
              isAnimationActive={false}
              label={({ x, y, index, value }) => (
                index === last
                  ? <text x={Number(x) + 10} y={Number(y)} dy={4} fill="#3b3b33" fontSize={12}>{value}</text>
                  : <g />
              )}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}

export function BenchmarkShareCard({ weeks }: { weeks: ClanWeekPoint[] }) {
  const last = weeks.length - 1;
  const best = weeks.reduce((bi, w, i) => ((w.atBenchmarkPct ?? 0) > (weeks[bi].atBenchmarkPct ?? 0) ? i : bi), 0);

  return (
    <ChartCard light icon="star" title="At or above benchmark"
               subtitle="Share of ranked members reaching the league we expect for their Town Hall">
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={weeks} margin={{ top: 20, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke={LIGHT.grid} />
            <XAxis dataKey="date" tickLine={false} axisLine={{ stroke: LIGHT.axisLine }} tick={LIGHT.tick} minTickGap={24} />
            <YAxis domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} tickFormatter={v => `${v}%`}
                   tickLine={false} axisLine={false} tick={LIGHT.tick} width={44} />
            <Tooltip cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }} content={tooltipFor} />
            <Bar dataKey="atBenchmarkPct" fill={LIGHT.us} maxBarSize={24} radius={[4, 4, 0, 0]} isAnimationActive={false}>
              <LabelList
                dataKey="atBenchmarkPct"
                content={(props: { x?: unknown; y?: unknown; width?: unknown; index?: number; value?: unknown }) => (
                  props.index === last || props.index === best
                    ? <text x={Number(props.x) + Number(props.width) / 2} y={Number(props.y) - 6} textAnchor="middle"
                            fill="#3b3b33" fontSize={12}>{Math.round(Number(props.value))}%</text>
                    : <g />
                )}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}

// One row per Town Hall: each member is a dot at their league, the dark tick is
// the benchmark. Dots at or above it are blue, below it red.
export function BenchmarkDotsCard({ dots }: { dots: BenchmarkDot[] }) {
  const [hovered, setHovered] = useState<BenchmarkDot | null>(null);
  const ranked = dots.filter(d => d.league > 0);
  const leagues = [...ranked.map(d => d.league), ...dots.map(d => d.benchmark)];
  const min = Math.max(1, Math.min(...leagues) - 1);
  const max = Math.min(36, Math.max(...leagues) + 1);
  const x = (league: number) => `${((league - min) / (max - min)) * 100}%`;
  const townHalls = [...new Set(dots.map(d => d.townHall))].sort((a, b) => b - a);
  // Axis ticks where a new creature league starts (1, 4, 7, ...)
  const ticks = Array.from({ length: 12 }, (_, i) => i * 3 + 1).filter(l => l >= min && l <= max);

  return (
    <ChartCard
      light
      icon="townHall"
      title="League against benchmark"
      subtitle="Every member at their ranked league, per Town Hall"
      legend={
        <>
          <span className="flex items-center gap-1.5 text-xs text-[#3b3b33]">
            <span className="w-3 h-3 rounded-full" style={{ background: LIGHT.us }} /> At or above
          </span>
          <span className="flex items-center gap-1.5 text-xs text-[#3b3b33]">
            <span className="w-3 h-3 rounded-full" style={{ background: LIGHT.behind }} /> Below
          </span>
          <span className="flex items-center gap-1.5 text-xs text-[#3b3b33]">
            <span className="w-0.5 h-3.5 bg-[#3b3b33]" /> Benchmark
          </span>
        </>
      }
    >
      <div className="space-y-1" onMouseLeave={() => setHovered(null)}>
        {townHalls.map(th => {
          const row = dots.filter(d => d.townHall === th);
          const unranked = row.filter(d => d.league === 0);
          const seen = new Map<number, number>();
          return (
            <div key={th} className="grid grid-cols-[4rem_1fr] items-center gap-2">
              <span className="text-right leading-tight">
                <span className="block text-sm text-[#3b3b33]">TH{th}</span>
                {unranked.length > 0 && (
                  <span className="block text-[10px] text-[#6b6a5c]">{unranked.length} unranked</span>
                )}
              </span>
              <div className="relative h-9 rounded-md bg-[#e7ecf2]">
                <span className="absolute top-1 bottom-1 w-0.5 bg-[#3b3b33]" style={{ left: x(row[0].benchmark) }}
                      title={`Benchmark for TH${th}: ${leagueName(row[0].benchmark)}`} />
                {row.filter(d => d.league > 0).map(d => {
                  // Members in the same league fan out a little so every dot stays visible
                  const n = seen.get(d.league) ?? 0;
                  seen.set(d.league, n + 1);
                  const offset = (n % 2 === 0 ? -1 : 1) * Math.ceil(n / 2) * 7;
                  const above = d.league >= d.benchmark;
                  return (
                    <button
                      key={d.tag}
                      type="button"
                      onMouseEnter={() => setHovered(d)}
                      onFocus={() => setHovered(d)}
                      aria-label={`${d.name}: ${leagueName(d.league)}, benchmark ${leagueName(d.benchmark)}`}
                      className="absolute w-6 h-6 -ml-3 flex items-center justify-center"
                      style={{ left: x(d.league), top: `calc(50% - 12px + ${offset}px)` }}
                    >
                      <span className={`w-3 h-3 rounded-full ring-2 ${hovered?.tag === d.tag ? 'ring-[#3b3b33]' : 'ring-[#e7ecf2]'}`}
                            style={{ background: above ? LIGHT.us : LIGHT.behind }} />
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
        <div className="grid grid-cols-[4rem_1fr] gap-2">
          <span />
          <div className="relative h-5">
            {ticks.map(l => (
              <span key={l} className="absolute -translate-x-1/2 text-[11px] text-[#6b6a5c]" style={{ left: x(l) }}>{l}</span>
            ))}
          </div>
        </div>
      </div>
      <p className="mt-2 text-sm text-[#3b3b33] min-h-5">
        {hovered
          ? `${hovered.name} · TH${hovered.townHall} · ${leagueName(hovered.league)} · benchmark ${leagueName(hovered.benchmark)} (${hovered.league - hovered.benchmark >= 0 ? '+' : ''}${hovered.league - hovered.benchmark})`
          : 'Hover a dot to see the member. League numbers along the bottom: 16-18 Witch, 19-21 Golem, 22-24 P.E.K.K.A, 25-27 Titan, 28-30 Dragon, 31-33 Electro.'}
      </p>
    </ChartCard>
  );
}

export function MissedAttacksCard({ date, played, complete, missed }: {
  date: string;
  played: number;
  complete: number;
  missed: MissedAttacks[];
}) {
  return (
    <ChartCard light icon="battle" title="Ranked attacks last week"
               subtitle={`Week of ${date} · ${complete} of ${played} members used all their ranked attacks`}>
      {missed.length === 0 ? (
        <p className="text-sm text-[#3b3b33]">Everyone used all their attacks. Nice work!</p>
      ) : (
        <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-1.5">
          {missed.map(m => (
            <li key={m.tag} className="flex items-center justify-between gap-2 rounded-lg bg-[#e7ecf2] px-3 py-1.5 text-sm">
              <span className="text-[#2d3340] truncate">{m.name}</span>
              <span className="flex items-center gap-1 text-xs text-amber-700 whitespace-nowrap">
                <span aria-hidden className="w-4 h-4 rounded-full bg-amber-400 text-slate-950 text-[10px] font-bold flex items-center justify-center">!</span>
                {m.attacks}/{m.maxAttacks}
              </span>
            </li>
          ))}
        </ul>
      )}
    </ChartCard>
  );
}

// League over the recorded weeks for the member table: grey line, latest week in blue
export function LeagueSparkline({ leagues }: { leagues: (number | null)[] }) {
  const points = leagues.map((l, i) => ({ i, l })).filter((p): p is { i: number; l: number } => p.l !== null && p.l > 0);
  if (points.length < 2) return <span className="text-xs text-[#9a998c]">–</span>;
  const width = 72;
  const height = 22;
  const lo = Math.min(...points.map(p => p.l));
  const hi = Math.max(...points.map(p => p.l));
  const span = Math.max(3, hi - lo); // at least 3 leagues, so one step isn't a cliff
  const px = (i: number) => 3 + (i / (leagues.length - 1)) * (width - 6);
  const py = (l: number) => height - 3 - ((l - lo) / span) * (height - 6);
  const last = points[points.length - 1];
  const first = points[0];
  return (
    <svg width={width} height={height} role="img" aria-label={`League ${first.l} to ${last.l} over ${points.length} weeks`}>
      <title>{`League ${first.l} → ${last.l}`}</title>
      <polyline points={points.map(p => `${px(p.i)},${py(p.l)}`).join(' ')} fill="none"
                stroke={LIGHT.context} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={px(last.i)} cy={py(last.l)} r={3.5} fill={LIGHT.us} stroke="#e7ecf2" strokeWidth={1.5} />
    </svg>
  );
}
