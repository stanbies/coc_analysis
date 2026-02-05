'use client';

import { useState } from 'react';
import { CWLSeason, CWLPlayerStats } from '../types';

interface CWLSeasonDetailProps {
  season: CWLSeason;
}

type SortKey = 'totalStars' | 'averageStars' | 'threeStars' | 'attacksUsed' | 'averageDestruction' | 'name';
type SortDirection = 'asc' | 'desc';

export default function CWLSeasonDetail({ season }: CWLSeasonDetailProps) {
  const [sortKey, setSortKey] = useState<SortKey>('totalStars');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [expandedPlayer, setExpandedPlayer] = useState<string | null>(null);

  // Format season as readable date
  const formatSeasonDate = (seasonStr: string) => {
    const [year, month] = seasonStr.split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1);
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('desc');
    }
  };

  const sortedPlayers = [...season.playerStats].sort((a, b) => {
    let aVal: number | string = a[sortKey];
    let bVal: number | string = b[sortKey];
    
    if (sortKey === 'name') {
      return sortDirection === 'asc' 
        ? (aVal as string).localeCompare(bVal as string)
        : (bVal as string).localeCompare(aVal as string);
    }
    
    return sortDirection === 'asc' 
      ? (aVal as number) - (bVal as number) 
      : (bVal as number) - (aVal as number);
  });

  const SortHeader = ({ label, sortKeyName }: { label: string; sortKeyName: SortKey }) => (
    <th
      className="text-left py-3 px-3 text-slate-400 text-sm cursor-pointer hover:text-white transition-colors"
      onClick={() => handleSort(sortKeyName)}
    >
      <div className="flex items-center gap-1">
        {label}
        {sortKey === sortKeyName && (
          <span className="text-orange-400">{sortDirection === 'asc' ? '↑' : '↓'}</span>
        )}
      </div>
    </th>
  );

  const getHitTypeEmoji = (hitType: string) => {
    if (hitType.includes('UP')) return '↑';
    if (hitType.includes('DOWN')) return '↓';
    return '=';
  };

  const getStarDisplay = (stars: number) => {
    if (stars === 3) return <span className="text-yellow-400">⭐⭐⭐</span>;
    if (stars === 2) return <span className="text-yellow-400">⭐⭐</span>;
    if (stars === 1) return <span className="text-yellow-400">⭐</span>;
    return <span className="text-red-400">✗</span>;
  };

  // Calculate top performers
  const topByStars = [...season.playerStats].sort((a, b) => b.totalStars - a.totalStars).slice(0, 3);
  const topByAvg = [...season.playerStats]
    .filter(p => p.attacksUsed >= 2)
    .sort((a, b) => b.averageStars - a.averageStars)
    .slice(0, 3);
  const topBy3Stars = [...season.playerStats].sort((a, b) => b.threeStars - a.threeStars).slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Season Header */}
      <div className="card p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-white">
              🏆 CWL {formatSeasonDate(season.season)}
            </h2>
            <p className="text-slate-400 mt-1">
              {season.state === 'inWar' ? 'Currently in progress' : 
               season.state === 'ended' ? 'Season completed' : 'In preparation'}
            </p>
          </div>
          <div className="flex gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{season.totalStars}</p>
              <p className="text-xs text-slate-400">Total Stars</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-amber-400">{season.averageStars.toFixed(2)}</p>
              <p className="text-xs text-slate-400">Avg Stars</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-green-400">{season.threeStarRate.toFixed(1)}%</p>
              <p className="text-xs text-slate-400">3-Star Rate</p>
            </div>
          </div>
        </div>

        {/* Progress */}
        <div className="mt-4">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Progress</span>
            <span className="text-white">{season.roundsCompleted} / {season.totalRounds} rounds</span>
          </div>
          <div className="bg-slate-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-orange-500 to-amber-500 h-3 rounded-full transition-all"
              style={{ width: `${(season.roundsCompleted / season.totalRounds) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Top Performers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Most Stars */}
        <div className="card p-4">
          <h3 className="text-lg font-bold text-white mb-3">⭐ Most Stars</h3>
          <div className="space-y-2">
            {topByStars.map((player, i) => (
              <div key={player.tag} className="flex items-center justify-between bg-slate-800/50 rounded-lg p-2">
                <div className="flex items-center gap-2">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    i === 0 ? 'bg-yellow-500 text-black' :
                    i === 1 ? 'bg-slate-300 text-black' :
                    'bg-amber-600 text-white'
                  }`}>
                    {i + 1}
                  </span>
                  <div>
                    <p className="text-white text-sm font-medium">{player.name}</p>
                    <p className="text-xs text-slate-400">TH{player.townHallLevel}</p>
                  </div>
                </div>
                <p className="text-yellow-400 font-bold">{player.totalStars}⭐</p>
              </div>
            ))}
          </div>
        </div>

        {/* Best Average */}
        <div className="card p-4">
          <h3 className="text-lg font-bold text-white mb-3">📈 Best Average</h3>
          <div className="space-y-2">
            {topByAvg.map((player, i) => (
              <div key={player.tag} className="flex items-center justify-between bg-slate-800/50 rounded-lg p-2">
                <div className="flex items-center gap-2">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    i === 0 ? 'bg-yellow-500 text-black' :
                    i === 1 ? 'bg-slate-300 text-black' :
                    'bg-amber-600 text-white'
                  }`}>
                    {i + 1}
                  </span>
                  <div>
                    <p className="text-white text-sm font-medium">{player.name}</p>
                    <p className="text-xs text-slate-400">{player.attacksUsed} attacks</p>
                  </div>
                </div>
                <p className="text-amber-400 font-bold">{player.averageStars.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Most 3-Stars */}
        <div className="card p-4">
          <h3 className="text-lg font-bold text-white mb-3">🌟 Most 3-Stars</h3>
          <div className="space-y-2">
            {topBy3Stars.map((player, i) => (
              <div key={player.tag} className="flex items-center justify-between bg-slate-800/50 rounded-lg p-2">
                <div className="flex items-center gap-2">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    i === 0 ? 'bg-yellow-500 text-black' :
                    i === 1 ? 'bg-slate-300 text-black' :
                    'bg-amber-600 text-white'
                  }`}>
                    {i + 1}
                  </span>
                  <div>
                    <p className="text-white text-sm font-medium">{player.name}</p>
                    <p className="text-xs text-slate-400">TH{player.townHallLevel}</p>
                  </div>
                </div>
                <p className="text-green-400 font-bold">{player.threeStars}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Full Player Stats Table */}
      <div className="card p-6">
        <h3 className="text-xl font-bold text-white mb-4">📊 All Player Statistics</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-3 text-slate-400 text-sm">#</th>
                <SortHeader label="Player" sortKeyName="name" />
                <th className="text-left py-3 px-3 text-slate-400 text-sm">TH</th>
                <SortHeader label="Attacks" sortKeyName="attacksUsed" />
                <SortHeader label="Stars" sortKeyName="totalStars" />
                <SortHeader label="Avg ⭐" sortKeyName="averageStars" />
                <SortHeader label="3-Stars" sortKeyName="threeStars" />
                <SortHeader label="Avg %" sortKeyName="averageDestruction" />
                <th className="text-left py-3 px-3 text-slate-400 text-sm">Hit Dir.</th>
                <th className="text-left py-3 px-3 text-slate-400 text-sm"></th>
              </tr>
            </thead>
            <tbody>
              {sortedPlayers.map((player, i) => (
                <>
                  <tr
                    key={player.tag}
                    className="border-b border-slate-800 hover:bg-slate-800/30 cursor-pointer"
                    onClick={() => setExpandedPlayer(expandedPlayer === player.tag ? null : player.tag)}
                  >
                    <td className="py-3 px-3 text-slate-500">{i + 1}</td>
                    <td className="py-3 px-3">
                      <span className="text-white font-medium">{player.name}</span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="bg-orange-500 text-white text-xs px-2 py-0.5 rounded">
                        TH{player.townHallLevel}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-white">{player.attacksUsed}</td>
                    <td className="py-3 px-3 text-yellow-400 font-bold">{player.totalStars}⭐</td>
                    <td className="py-3 px-3 text-amber-400 font-medium">{player.averageStars.toFixed(2)}</td>
                    <td className="py-3 px-3 text-green-400">{player.threeStars}</td>
                    <td className="py-3 px-3 text-slate-300">{player.averageDestruction.toFixed(1)}%</td>
                    <td className="py-3 px-3 text-xs">
                      <span className="text-green-400" title="Hit Up">↑{player.hitUp}</span>
                      {' '}
                      <span className="text-slate-400" title="Hit Same">={player.hitSame}</span>
                      {' '}
                      <span className="text-red-400" title="Hit Down">↓{player.hitDown}</span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-slate-400 text-sm">
                        {expandedPlayer === player.tag ? '▼' : '▶'}
                      </span>
                    </td>
                  </tr>
                  {/* Expanded attack details */}
                  {expandedPlayer === player.tag && (
                    <tr className="bg-slate-800/50">
                      <td colSpan={10} className="py-4 px-6">
                        <div className="text-sm">
                          <p className="text-slate-400 mb-2">Attack History:</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                            {player.attacks.map((attack, idx) => (
                              <div
                                key={idx}
                                className="bg-slate-900/50 rounded-lg p-3 flex items-center justify-between"
                              >
                                <div>
                                  <span className="text-slate-400 text-xs">Round {attack.round}</span>
                                  <div className="flex items-center gap-2 mt-1">
                                    <span className="text-white">TH{attack.attackerTh}</span>
                                    <span className="text-slate-500">→</span>
                                    <span className="text-slate-300">TH{attack.defenderTh}</span>
                                    <span className={`text-xs ${
                                      attack.hitType.includes('UP') ? 'text-green-400' :
                                      attack.hitType.includes('DOWN') ? 'text-red-400' :
                                      'text-slate-400'
                                    }`}>
                                      {getHitTypeEmoji(attack.hitType)}
                                    </span>
                                  </div>
                                </div>
                                <div className="text-right">
                                  {getStarDisplay(attack.stars)}
                                  <p className="text-xs text-slate-400 mt-1">{attack.destruction}%</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Star Distribution */}
      <div className="card p-6">
        <h3 className="text-xl font-bold text-white mb-4">📊 Star Distribution</h3>
        <div className="grid grid-cols-4 gap-4">
          {[3, 2, 1, 0].map(stars => {
            const count = season.playerStats.reduce((sum, p) => {
              if (stars === 3) return sum + p.threeStars;
              if (stars === 2) return sum + p.twoStars;
              if (stars === 1) return sum + p.oneStars;
              return sum + p.zeroStars;
            }, 0);
            const percentage = season.totalAttacks > 0 ? (count / season.totalAttacks * 100) : 0;
            
            return (
              <div key={stars} className="bg-slate-800/50 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">
                  {stars === 3 ? '⭐⭐⭐' : stars === 2 ? '⭐⭐' : stars === 1 ? '⭐' : '❌'}
                </div>
                <p className="text-2xl font-bold text-white">{count}</p>
                <p className="text-sm text-slate-400">{percentage.toFixed(1)}%</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
