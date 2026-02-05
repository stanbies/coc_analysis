'use client';

import { Player } from '../types';

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

function getRoleIcon(role: string): string {
  switch (role) {
    case 'leader': return '👑';
    case 'coLeader': return '⭐';
    case 'admin': return '🛡️';
    default: return '👤';
  }
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
          <span className="text-lg">{getRoleIcon(player.role)}</span>
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
      
      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className="bg-slate-800/50 rounded-lg p-2">
          <p className="text-lg font-bold text-yellow-400">🏆 {player.trophies.toLocaleString()}</p>
          <p className="text-xs text-slate-400">Trophies</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-2">
          <p className="text-lg font-bold text-purple-400">⭐ {player.warStars.toLocaleString()}</p>
          <p className="text-xs text-slate-400">War Stars</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-2">
          <p className="text-lg font-bold text-cyan-400">🦸 {totalHeroLevels}</p>
          <p className="text-xs text-slate-400">Hero Lvls</p>
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-green-400 text-sm">↑{player.donations}</span>
          <span className="text-slate-500">/</span>
          <span className="text-red-400 text-sm">↓{player.donationsReceived}</span>
        </div>
        <span className={`${rushClass} text-xs px-2 py-1 rounded-full text-white font-medium`}>
          {player.rushAnalysis.status.replace(/[✅🟢🟡🟠🔴]\s?/g, '')}
        </span>
      </div>
    </div>
  );
}
