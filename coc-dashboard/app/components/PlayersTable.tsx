'use client';

import { useState } from 'react';
import { Player, RankedWeek } from '../types';
import LeagueBadge, { compareByLeague } from './LeagueBadge';
import GameIcon, { roleIcon } from './GameIcon';
import { LeagueSparkline } from './RankedCharts';
import { playerLeagues } from '../lib/ranked';

interface PlayersTableProps {
  players: Player[];
  // Weekly ranked history, for the per-member trend column
  rankedHistory?: RankedWeek[];
  onPlayerClick: (player: Player) => void;
}

type SortField = 'name' | 'townHallLevel' | 'league' | 'warStars' | 'donations' | 'rushScore' | 'heroLevels';
type SortDirection = 'asc' | 'desc';

function getRushStatusClass(status: string): string {
  if (status.includes('Maxed')) return 'rush-maxed';
  if (status.includes('Slightly')) return 'rush-slight';
  if (status.includes('Moderately')) return 'rush-moderate';
  if (status.includes('Severely')) return 'rush-severe';
  if (status.includes('Rushed')) return 'rush-rushed';
  return 'bg-slate-600';
}

interface SortHeaderProps {
  field: SortField;
  sortField: SortField;
  sortDirection: SortDirection;
  onSort: (field: SortField) => void;
  children: React.ReactNode;
}

function SortHeader({ field, sortField, sortDirection, onSort, children }: SortHeaderProps) {
  return (
    <th
      className="text-left pt-1 pb-0.5 px-2 text-[#6b6a5c] text-sm font-medium cursor-pointer hover:text-[#2b2b25] transition-colors whitespace-nowrap"
      onClick={() => onSort(field)}
    >
      <div className="flex items-center gap-1">
        {children}
        {sortField === field && (
          <span className="text-[#2266c2]">{sortDirection === 'asc' ? '↑' : '↓'}</span>
        )}
      </div>
    </th>
  );
}

export default function PlayersTable({ players, rankedHistory = [], onPlayerClick }: PlayersTableProps) {
  const showTrend = rankedHistory.length > 1;
  const [sortField, setSortField] = useState<SortField>('townHallLevel');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [filter, setFilter] = useState('');
  const [rushFilter, setRushFilter] = useState<string>('all');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const filteredPlayers = players
    .filter(p => {
      const matchesSearch = p.name.toLowerCase().includes(filter.toLowerCase()) ||
                           p.tag.toLowerCase().includes(filter.toLowerCase());
      const matchesRush = rushFilter === 'all' ||
                         (rushFilter === 'rushed' && p.rushAnalysis.isRushed) ||
                         (rushFilter === 'notRushed' && !p.rushAnalysis.isRushed);
      return matchesSearch && matchesRush;
    })
    .sort((a, b) => {
      if (sortField === 'league') {
        return sortDirection === 'desc' ? compareByLeague(a, b) : compareByLeague(b, a);
      }

      let aVal: number | string;
      let bVal: number | string;

      switch (sortField) {
        case 'name':
          aVal = a.name.toLowerCase();
          bVal = b.name.toLowerCase();
          break;
        case 'townHallLevel':
          aVal = a.townHallLevel;
          bVal = b.townHallLevel;
          break;
        case 'warStars':
          aVal = a.warStars;
          bVal = b.warStars;
          break;
        case 'donations':
          aVal = a.donations;
          bVal = b.donations;
          break;
        case 'rushScore':
          aVal = a.rushAnalysis.rushScore;
          bVal = b.rushAnalysis.rushScore;
          break;
        case 'heroLevels':
          aVal = a.heroes.reduce((sum, h) => sum + h.level, 0);
          bVal = b.heroes.reduce((sum, h) => sum + h.level, 0);
          break;
        default:
          aVal = 0;
          bVal = 0;
      }
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return sortDirection === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
    });

  const sortProps = { sortField, sortDirection, onSort: handleSort };

  return (
    <div className="coc-panel-light p-4 md:p-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
        <h2 className="coc-text text-2xl flex items-center gap-2"><GameIcon name="barbarian" size={28} /> All Members ({filteredPlayers.length})</h2>
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <input
            type="text"
            placeholder="Search players..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="coc-input px-3 py-2 text-sm placeholder-[#9a998c]"
          />
          <select
            value={rushFilter}
            onChange={(e) => setRushFilter(e.target.value)}
            className="coc-input px-3 py-2 text-sm"
          >
            <option value="all">All Players</option>
            <option value="rushed">Rushed Only</option>
            <option value="notRushed">Not Rushed</option>
          </select>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full border-separate border-spacing-y-1.5">
          <thead>
            <tr>
              <th className="text-left pt-1 pb-0.5 px-2 text-[#6b6a5c] text-sm font-medium">#</th>
              <SortHeader field="name" {...sortProps}>Name</SortHeader>
              <SortHeader field="townHallLevel" {...sortProps}>TH</SortHeader>
              <SortHeader field="league" {...sortProps}>League</SortHeader>
              {showTrend && (
                <th className="text-left pt-1 pb-0.5 px-2 text-[#6b6a5c] text-sm font-medium whitespace-nowrap">
                  Last {rankedHistory.length} weeks
                </th>
              )}
              <SortHeader field="warStars" {...sortProps}>War Stars</SortHeader>
              <SortHeader field="heroLevels" {...sortProps}>Heroes</SortHeader>
              <SortHeader field="donations" {...sortProps}>Donations</SortHeader>
              <SortHeader field="rushScore" {...sortProps}>Rush Score</SortHeader>
              <th className="text-left pt-1 pb-0.5 px-2 text-[#6b6a5c] text-sm font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredPlayers.map((player, i) => {
              const totalHeroLevels = player.heroes.reduce((sum, h) => sum + h.level, 0);
              const rushClass = getRushStatusClass(player.rushAnalysis.status);
              
              return (
                <tr
                  key={player.tag}
                  className="coc-row cursor-pointer"
                  onClick={() => onPlayerClick(player)}
                >
                  <td className="py-2 px-2">
                    <span className="coc-text inline-flex w-8 h-8 items-center justify-center rounded-lg bg-[#5d6b80] border-2 border-black/40 text-sm">{i + 1}</span>
                  </td>
                  <td className="py-2 px-2">
                    <div className="flex items-center gap-2">
                      <GameIcon name={roleIcon(player.role).icon} size={22} alt={roleIcon(player.role).label} />
                      <span className="coc-text text-base whitespace-nowrap">{player.name}</span>
                    </div>
                  </td>
                  <td className="py-2 px-2">
                    <span className="bg-gradient-to-r from-orange-500 to-amber-500 text-white text-xs font-bold px-2 py-1 rounded">
                      {player.townHallLevel}
                    </span>
                  </td>
                  <td className="py-2 px-2">
                    <div className="flex items-center gap-2 whitespace-nowrap">
                      <LeagueBadge league={player.leagueTier} showName={false} />
                      <div className="leading-tight">
                        <p className={`text-sm ${player.leagueTier ? 'text-[#2d3340]' : 'text-[#8a897c]'}`}>
                          {player.leagueTier?.name ?? 'Unranked'}
                        </p>
                        <p className="text-xs text-amber-700 flex items-center gap-1"><GameIcon name="trophy" size={14} /> {player.trophies.toLocaleString('en-US')}</p>
                      </div>
                    </div>
                  </td>
                  {showTrend && (
                    <td className="py-2 px-2">
                      <LeagueSparkline leagues={playerLeagues(rankedHistory, player.tag)} />
                    </td>
                  )}
                  <td className="py-2 px-2 text-purple-700">{player.warStars.toLocaleString('en-US')}</td>
                  <td className="py-2 px-2 text-sky-700">{totalHeroLevels}</td>
                  <td className="py-2 px-2 whitespace-nowrap">
                    <span className="text-green-700">↑{player.donations}</span>
                    <span className="text-[#9a998c] mx-1">/</span>
                    <span className="text-red-600">↓{player.donationsReceived}</span>
                  </td>
                  <td className="py-2 px-2 text-orange-600">{player.rushAnalysis.rushScore.toFixed(1)}</td>
                  <td className="py-2 px-2">
                    <span className={`${rushClass} coc-text text-xs px-2.5 py-1 rounded-full border-2 border-black/40 whitespace-nowrap`}>
                      {player.rushAnalysis.status.replace(/[✅🟢🟡🟠🔴]\s?/g, '')}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
