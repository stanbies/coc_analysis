'use client';

import { Clan } from '../types';

interface ClanHeaderProps {
  clan: Clan;
  lastUpdated: string;
}

export default function ClanHeader({ clan, lastUpdated }: ClanHeaderProps) {
  const totalWars = clan.warWins + clan.warTies + clan.warLosses;
  const winRate = totalWars > 0 ? ((clan.warWins / totalWars) * 100).toFixed(1) : '0';
  
  return (
    <div className="card p-6 mb-6 glow-orange">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          {clan.badgeUrls?.large && (
            <img 
              src={clan.badgeUrls.large} 
              alt={clan.name}
              className="w-20 h-20 rounded-lg"
            />
          )}
          <div>
            <h1 className="text-3xl font-bold text-white">{clan.name}</h1>
            <p className="text-slate-400">{clan.tag}</p>
            <div className="flex items-center gap-2 mt-1">
              <span className="bg-orange-500/20 text-orange-400 text-sm px-2 py-0.5 rounded">
                Level {clan.clanLevel}
              </span>
              {clan.location && (
                <span className="bg-blue-500/20 text-blue-400 text-sm px-2 py-0.5 rounded">
                  📍 {clan.location.name}
                </span>
              )}
              {clan.warLeague && (
                <span className="bg-purple-500/20 text-purple-400 text-sm px-2 py-0.5 rounded">
                  ⚔️ {clan.warLeague.name}
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-white">{clan.members}/50</p>
            <p className="text-xs text-slate-400">Members</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-yellow-400">{clan.clanPoints.toLocaleString()}</p>
            <p className="text-xs text-slate-400">Clan Points</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-400">{clan.warWins}</p>
            <p className="text-xs text-slate-400">War Wins</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-cyan-400">{winRate}%</p>
            <p className="text-xs text-slate-400">Win Rate</p>
          </div>
        </div>
      </div>
      
      {clan.description && (
        <p className="text-slate-300 mt-4 text-sm border-t border-slate-700 pt-4">
          {clan.description}
        </p>
      )}
      
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-700">
        <div className="flex items-center gap-4">
          {clan.labels?.map((label, i) => (
            <div key={i} className="flex items-center gap-1">
              {label.iconUrls?.small && (
                <img src={label.iconUrls.small} alt={label.name} className="w-5 h-5" />
              )}
              <span className="text-xs text-slate-400">{label.name}</span>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-500">
          Last updated: {new Date(lastUpdated).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
