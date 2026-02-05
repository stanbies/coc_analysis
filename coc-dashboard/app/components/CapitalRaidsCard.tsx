'use client';

import { CapitalRaid } from '../types';

interface CapitalRaidsCardProps {
  capitalRaids: CapitalRaid[];
}

export default function CapitalRaidsCard({ capitalRaids }: CapitalRaidsCardProps) {
  if (!capitalRaids || capitalRaids.length === 0) {
    return (
      <div className="card p-6">
        <h2 className="text-xl font-bold text-white mb-4">🏛️ Capital Raids</h2>
        <p className="text-slate-400">No capital raid data available.</p>
      </div>
    );
  }

  const latestRaid = capitalRaids[0];
  
  // Sort members by loot
  const topRaiders = [...(latestRaid.members || [])]
    .sort((a, b) => b.capitalResourcesLooted - a.capitalResourcesLooted)
    .slice(0, 10);

  return (
    <div className="card p-6">
      <h2 className="text-xl font-bold text-white mb-4">🏛️ Capital Raids</h2>
      
      {/* Latest Raid Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-800 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-amber-400">
            {latestRaid.capitalTotalLoot?.toLocaleString() || 0}
          </p>
          <p className="text-xs text-slate-400">Total Loot</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-green-400">
            {latestRaid.raidsCompleted || 0}
          </p>
          <p className="text-xs text-slate-400">Raids Completed</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-cyan-400">
            {latestRaid.totalAttacks || 0}
          </p>
          <p className="text-xs text-slate-400">Total Attacks</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-purple-400">
            {latestRaid.enemyDistrictsDestroyed || 0}
          </p>
          <p className="text-xs text-slate-400">Districts Destroyed</p>
        </div>
      </div>
      
      {/* Top Raiders */}
      {topRaiders.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-slate-400 mb-3">Top Raiders (Latest Weekend)</h3>
          <div className="space-y-2">
            {topRaiders.map((member, i) => (
              <div key={member.tag} className="flex items-center justify-between bg-slate-800/50 rounded-lg p-2">
                <div className="flex items-center gap-2">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    i === 0 ? 'bg-yellow-500 text-black' :
                    i === 1 ? 'bg-slate-300 text-black' :
                    i === 2 ? 'bg-amber-600 text-white' :
                    'bg-slate-700 text-white'
                  }`}>
                    {i + 1}
                  </span>
                  <span className="text-white text-sm">{member.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-slate-400">
                    {member.attacks}/{member.attackLimit + member.bonusAttackLimit} attacks
                  </span>
                  <span className="text-amber-400 font-medium">
                    {member.capitalResourcesLooted.toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Rewards */}
      <div className="mt-4 pt-4 border-t border-slate-700 flex justify-between">
        <div>
          <span className="text-slate-400 text-sm">Offensive Reward: </span>
          <span className="text-green-400 font-medium">{latestRaid.offensiveReward || 0}</span>
        </div>
        <div>
          <span className="text-slate-400 text-sm">Defensive Reward: </span>
          <span className="text-blue-400 font-medium">{latestRaid.defensiveReward || 0}</span>
        </div>
      </div>
    </div>
  );
}
