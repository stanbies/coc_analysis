'use client';

import { Player } from '../types';

interface PlayerModalProps {
  player: Player;
  onClose: () => void;
}

function getRushStatusClass(status: string): string {
  if (status.includes('Maxed')) return 'rush-maxed';
  if (status.includes('Slightly')) return 'rush-slight';
  if (status.includes('Moderately')) return 'rush-moderate';
  if (status.includes('Severely')) return 'rush-severe';
  if (status.includes('Rushed')) return 'rush-rushed';
  return 'bg-slate-600';
}

function getRoleLabel(role: string): string {
  switch (role) {
    case 'leader': return '👑 Leader';
    case 'coLeader': return '⭐ Co-Leader';
    case 'admin': return '🛡️ Elder';
    default: return '👤 Member';
  }
}

export default function PlayerModal({ player, onClose }: PlayerModalProps) {
  const rushClass = getRushStatusClass(player.rushAnalysis.status);
  
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div 
        className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-600 to-amber-600 p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white">{player.name}</h2>
              <p className="text-orange-100">{player.tag}</p>
              <p className="text-orange-200 text-sm mt-1">{getRoleLabel(player.role)}</p>
            </div>
            <div className="text-right">
              <div className="bg-white/20 backdrop-blur text-white text-2xl font-bold px-4 py-2 rounded-xl">
                TH{player.townHallLevel}
              </div>
              <p className="text-orange-100 text-sm mt-1">Level {player.expLevel}</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 text-white/80 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-yellow-400">🏆 {player.trophies.toLocaleString()}</p>
              <p className="text-xs text-slate-400">Current Trophies</p>
              <p className="text-xs text-slate-500">Best: {player.bestTrophies.toLocaleString()}</p>
            </div>
            <div className="bg-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-purple-400">⭐ {player.warStars.toLocaleString()}</p>
              <p className="text-xs text-slate-400">War Stars</p>
            </div>
            <div className="bg-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-green-400">⚔️ {player.attackWins.toLocaleString()}</p>
              <p className="text-xs text-slate-400">Attack Wins</p>
            </div>
            <div className="bg-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-blue-400">🛡️ {player.defenseWins.toLocaleString()}</p>
              <p className="text-xs text-slate-400">Defense Wins</p>
            </div>
          </div>
          
          {/* Donations */}
          <div className="bg-slate-800 rounded-xl p-4">
            <h3 className="font-semibold text-white mb-3">📦 Donations</h3>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-green-400">Donated: {player.donations.toLocaleString()}</span>
                  <span className="text-red-400">Received: {player.donationsReceived.toLocaleString()}</span>
                </div>
                <div className="progress-bar h-3">
                  <div 
                    className="progress-fill h-full"
                    style={{ 
                      width: `${Math.min(100, (player.donations / Math.max(1, player.donations + player.donationsReceived)) * 100)}%` 
                    }}
                  />
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Ratio: {player.donationsReceived > 0 ? (player.donations / player.donationsReceived).toFixed(2) : player.donations}
                </p>
              </div>
            </div>
          </div>
          
          {/* Rush Analysis */}
          <div className="bg-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white">🔍 Rush Analysis</h3>
              <span className={`${rushClass} text-sm px-3 py-1 rounded-full text-white font-medium`}>
                {player.rushAnalysis.status.replace(/[✅🟢🟡🟠🔴]\s?/g, '')}
              </span>
            </div>
            
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-400">{player.rushAnalysis.rushScore.toFixed(1)}</p>
                <p className="text-xs text-slate-400">Rush Score</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-400">-{player.rushAnalysis.totalMissingHeroLevels}</p>
                <p className="text-xs text-slate-400">Missing Hero Lvls</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-yellow-400">{player.rushAnalysis.rushPercentage.toFixed(1)}%</p>
                <p className="text-xs text-slate-400">Behind Target</p>
              </div>
            </div>
            
            {player.rushAnalysis.rushedHeroes.length > 0 && (
              <div className="mt-4">
                <p className="text-sm text-slate-400 mb-2">Rushed Heroes:</p>
                <div className="flex flex-wrap gap-2">
                  {player.rushAnalysis.rushedHeroes.map((hero, i) => (
                    <span key={i} className="bg-red-500/20 text-red-300 text-xs px-2 py-1 rounded">
                      {hero.name}: {hero.current}/{hero.target} (-{hero.missing})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Heroes */}
          <div className="bg-slate-800 rounded-xl p-4">
            <h3 className="font-semibold text-white mb-3">🦸 Heroes</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {player.heroes.map((hero, i) => (
                <div key={i} className="bg-slate-700/50 rounded-lg p-3">
                  <p className="text-sm font-medium text-white truncate">{hero.name}</p>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-lg font-bold text-cyan-400">{hero.level}</span>
                    <span className="text-xs text-slate-400">/ {hero.maxLevel}</span>
                  </div>
                  <div className="progress-bar h-2 mt-2">
                    <div 
                      className="progress-fill h-full"
                      style={{ width: `${(hero.level / hero.maxLevel) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* War Performance */}
          {player.warStats.totalAttacks > 0 && (
            <div className="bg-slate-800 rounded-xl p-4">
              <h3 className="font-semibold text-white mb-3">⚔️ War Performance</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-xl font-bold text-white">{player.warStats.totalAttacks}</p>
                  <p className="text-xs text-slate-400">Total Attacks</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-yellow-400">{player.warStats.totalStars}</p>
                  <p className="text-xs text-slate-400">Total Stars</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-green-400">{player.warStats.threeStars}</p>
                  <p className="text-xs text-slate-400">3-Stars</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-cyan-400">
                    {(player.warStats.totalStars / player.warStats.totalAttacks).toFixed(2)}
                  </p>
                  <p className="text-xs text-slate-400">Avg Stars</p>
                </div>
              </div>
            </div>
          )}
          
          {/* Capital Contributions */}
          <div className="bg-slate-800 rounded-xl p-4">
            <h3 className="font-semibold text-white mb-2">🏛️ Clan Capital</h3>
            <p className="text-2xl font-bold text-amber-400">
              {player.clanCapitalContributions.toLocaleString()}
              <span className="text-sm text-slate-400 font-normal ml-2">Gold Contributed</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
