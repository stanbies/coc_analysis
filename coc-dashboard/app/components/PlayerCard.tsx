'use client';

import { Player } from '../types';
import LeagueBadge from './LeagueBadge';
import GameIcon, { roleIcon } from './GameIcon';

interface PlayerCardProps {
  player: Player;
  onClick?: () => void;
}

function getRushStatusClass(status: string): string {
  if (status.includes('Maxed')) return 'rush-maxed';
  if (status.includes('Slightly')) return 'rush-slight';
  if (status.includes('Moderately')) return 'rush-moderate';
  if (status.includes('Severely')) return 'rush-severe';
  if (status.includes('Rushed')) return 'rush-rushed';
  return 'bg-slate-600';
}

export default function PlayerCard({ player, onClick }: PlayerCardProps) {
  const rushClass = getRushStatusClass(player.rushAnalysis.status);
  const totalHeroLevels = player.heroes.reduce((sum, h) => sum + h.level, 0);
  
  return (
    <div 
      className="card p-4 cursor-pointer hover:border-orange-500/50 transition-all duration-300"
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <GameIcon name={roleIcon(player.role).icon} size={28} alt={roleIcon(player.role).label} />
          <div>
            <h3 className="font-semibold text-white">{player.name}</h3>
            <p className="text-xs text-slate-400">{player.tag}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="bg-gradient-to-r from-orange-500 to-amber-500 text-white text-sm font-bold px-3 py-1 rounded-full">
            TH{player.townHallLevel}
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-2 mb-3 bg-slate-800/50 rounded-lg px-2 py-1.5">
        <LeagueBadge league={player.leagueTier} />
        <span className="ml-auto text-sm font-bold whitespace-nowrap text-yellow-400 flex items-center gap-1"><GameIcon name="trophy" size={18} /> {player.trophies.toLocaleString('en-US')}</span>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3 text-center">
        <div className="bg-slate-800/50 rounded-lg px-1 py-2 min-w-0">
          <p className="text-base font-bold whitespace-nowrap text-purple-400 flex items-center justify-center gap-1"><GameIcon name="star" size={18} /> {player.warStars.toLocaleString('en-US')}</p>
          <p className="text-xs text-slate-400">War Stars</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg px-1 py-2 min-w-0">
          <p className="text-base font-bold whitespace-nowrap text-cyan-400 flex items-center justify-center gap-1"><GameIcon name="barbarianKing" size={20} /> {totalHeroLevels}</p>
          <p className="text-xs text-slate-400">Hero Lvls</p>
        </div>
      </div>
      
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 whitespace-nowrap">
          <span className="text-green-400 text-sm">↑{player.donations}</span>
          <span className="text-slate-500">/</span>
          <span className="text-red-400 text-sm">↓{player.donationsReceived}</span>
        </div>
        <span className={`${rushClass} text-xs px-2 py-1 rounded-full text-white font-medium whitespace-nowrap`}>
          {player.rushAnalysis.status.replace(/[✅🟢🟡🟠🔴]\s?/g, '')}
        </span>
      </div>
    </div>
  );
}
