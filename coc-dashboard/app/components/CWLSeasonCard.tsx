'use client';

import { CWLSeason } from '../types';

interface CWLSeasonCardProps {
  season: CWLSeason;
  onClick: () => void;
  isSelected: boolean;
}

export default function CWLSeasonCard({ season, onClick, isSelected }: CWLSeasonCardProps) {
  // Format season as readable date (e.g., "2026-02" -> "February 2026")
  const formatSeasonDate = (season: string) => {
    const [year, month] = season.split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1);
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case 'inWar':
        return 'bg-red-500';
      case 'preparation':
        return 'bg-yellow-500';
      case 'ended':
        return 'bg-green-500';
      default:
        return 'bg-slate-500';
    }
  };

  const getStateText = (state: string) => {
    switch (state) {
      case 'inWar':
        return 'In Progress';
      case 'preparation':
        return 'Preparation';
      case 'ended':
        return 'Completed';
      default:
        return state;
    }
  };

  return (
    <div
      onClick={onClick}
      className={`card p-4 cursor-pointer transition-all hover:scale-[1.02] ${
        isSelected ? 'ring-2 ring-orange-500 bg-slate-800/80' : 'hover:bg-slate-800/50'
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold text-white">
          🏆 {formatSeasonDate(season.season)}
        </h3>
        <span className={`px-2 py-1 rounded text-xs font-medium text-white ${getStateColor(season.state)}`}>
          {getStateText(season.state)}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="bg-slate-800/50 rounded-lg p-2">
          <p className="text-slate-400 text-xs">Total Stars</p>
          <p className="text-white font-bold text-lg">{season.totalStars} ⭐</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-2">
          <p className="text-slate-400 text-xs">Attacks</p>
          <p className="text-white font-bold text-lg">{season.totalAttacks}</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-2">
          <p className="text-slate-400 text-xs">Avg Stars</p>
          <p className="text-amber-400 font-bold text-lg">{season.averageStars.toFixed(2)}</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-2">
          <p className="text-slate-400 text-xs">3-Star Rate</p>
          <p className="text-green-400 font-bold text-lg">{season.threeStarRate.toFixed(1)}%</p>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-slate-700">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Rounds: {season.roundsCompleted}/{season.totalRounds}</span>
          <span>{season.playerStats.length} players</span>
        </div>
        {/* Progress bar for rounds */}
        <div className="mt-2 bg-slate-700 rounded-full h-2">
          <div
            className="bg-orange-500 h-2 rounded-full transition-all"
            style={{ width: `${(season.roundsCompleted / season.totalRounds) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
