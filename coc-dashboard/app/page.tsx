'use client';

import { useState, useEffect } from 'react';
import { DashboardData, Player } from './types';
import ClanHeader from './components/ClanHeader';
import StatCard from './components/StatCard';
import PlayerCard from './components/PlayerCard';
import PlayerModal from './components/PlayerModal';
import PlayersTable from './components/PlayersTable';
import THDistributionChart from './components/THDistributionChart';
import RushAnalysisChart from './components/RushAnalysisChart';
import WarLogTable from './components/WarLogTable';
import CapitalRaidsCard from './components/CapitalRaidsCard';

export default function Home() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'players' | 'wars' | 'capital'>('overview');

  useEffect(() => {
    fetch('/clan_data.json')
      .then(res => {
        if (!res.ok) throw new Error('Data not found. Run the clan_analyzer.py script first.');
        return res.json();
      })
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading clan data...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="card p-8 max-w-md text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-white mb-2">No Data Available</h1>
          <p className="text-slate-400 mb-4">{error || 'Could not load clan data.'}</p>
          <div className="bg-slate-800 rounded-lg p-4 text-left">
            <p className="text-sm text-slate-300 mb-2">To generate data, run:</p>
            <code className="text-orange-400 text-sm">python api/clan_analyzer.py</code>
          </div>
        </div>
      </div>
    );
  }

  const { clan, players, statistics, warLog, capitalRaids } = data;
  const totalWars = clan.warWins + clan.warTies + clan.warLosses;
  const winRate = totalWars > 0 ? ((clan.warWins / totalWars) * 100).toFixed(1) : '0';

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <ClanHeader clan={clan} lastUpdated={data.lastUpdated} />
        
        {/* Navigation Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {[
            { id: 'overview', label: '📊 Overview', icon: '📊' },
            { id: 'players', label: '👥 Players', icon: '👥' },
            { id: 'wars', label: '⚔️ Wars', icon: '⚔️' },
            { id: 'capital', label: '🏛️ Capital', icon: '🏛️' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-orange-500 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
              <StatCard title="Members" value={clan.members} icon="👥" subtitle="/50" />
              <StatCard title="Clan Level" value={clan.clanLevel} icon="⭐" />
              <StatCard title="War Wins" value={clan.warWins} icon="🏆" />
              <StatCard title="Win Rate" value={`${winRate}%`} icon="📈" />
              <StatCard title="Rushed" value={statistics.rushedCount} icon="⚠️" subtitle={`of ${players.length}`} />
              <StatCard title="Avg Rush Score" value={statistics.averageRushScore.toFixed(1)} icon="🔍" />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <THDistributionChart statistics={statistics} />
              <RushAnalysisChart statistics={statistics} />
            </div>

            {/* Top Players Cards */}
            <div className="mb-6">
              <h2 className="text-xl font-bold text-white mb-4">🏆 Top Players</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {players
                  .sort((a, b) => b.trophies - a.trophies)
                  .slice(0, 4)
                  .map(player => (
                    <PlayerCard
                      key={player.tag}
                      player={player}
                      onClick={() => setSelectedPlayer(player)}
                    />
                  ))}
              </div>
            </div>

            {/* Most Rushed Players */}
            <div className="card p-6 mb-6">
              <h2 className="text-xl font-bold text-white mb-4">⚠️ Most Rushed Players</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-2 px-2 text-slate-400 text-sm">#</th>
                      <th className="text-left py-2 px-2 text-slate-400 text-sm">Player</th>
                      <th className="text-left py-2 px-2 text-slate-400 text-sm">TH</th>
                      <th className="text-left py-2 px-2 text-slate-400 text-sm">Rush Score</th>
                      <th className="text-left py-2 px-2 text-slate-400 text-sm">Missing Hero Lvls</th>
                      <th className="text-left py-2 px-2 text-slate-400 text-sm">Rushed Heroes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {players
                      .filter(p => p.rushAnalysis.isRushed)
                      .sort((a, b) => b.rushAnalysis.rushScore - a.rushAnalysis.rushScore)
                      .slice(0, 10)
                      .map((player, i) => (
                        <tr
                          key={player.tag}
                          className="border-b border-slate-800 table-row cursor-pointer"
                          onClick={() => setSelectedPlayer(player)}
                        >
                          <td className="py-2 px-2 text-slate-500">{i + 1}</td>
                          <td className="py-2 px-2 text-white">{player.name}</td>
                          <td className="py-2 px-2">
                            <span className="bg-orange-500 text-white text-xs px-2 py-0.5 rounded">
                              TH{player.townHallLevel}
                            </span>
                          </td>
                          <td className="py-2 px-2 text-orange-400 font-medium">
                            {player.rushAnalysis.rushScore.toFixed(1)}
                          </td>
                          <td className="py-2 px-2 text-red-400">
                            -{player.rushAnalysis.totalMissingHeroLevels}
                          </td>
                          <td className="py-2 px-2 text-xs text-slate-400">
                            {player.rushAnalysis.rushedHeroes
                              .slice(0, 3)
                              .map(h => `${h.name.substring(0, 2)}: ${h.current}/${h.target}`)
                              .join(', ')}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* Players Tab */}
        {activeTab === 'players' && (
          <PlayersTable players={players} onPlayerClick={setSelectedPlayer} />
        )}

        {/* Wars Tab */}
        {activeTab === 'wars' && (
          <div className="space-y-6">
            {/* War Stats Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard title="Total Wars" value={totalWars} icon="⚔️" />
              <StatCard title="Wins" value={clan.warWins} icon="✅" />
              <StatCard title="Losses" value={clan.warLosses} icon="❌" />
              <StatCard title="Win Streak" value={clan.warWinStreak} icon="🔥" />
            </div>
            
            <WarLogTable warLog={warLog} />
          </div>
        )}

        {/* Capital Tab */}
        {activeTab === 'capital' && (
          <div className="space-y-6">
            {/* Capital Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard 
                title="Capital Points" 
                value={clan.clanCapitalPoints?.toLocaleString() || 0} 
                icon="🏛️" 
              />
              <StatCard 
                title="Capital Hall" 
                value={clan.clanCapital?.capitalHallLevel || 0} 
                icon="🏰" 
              />
              <StatCard 
                title="Districts" 
                value={clan.clanCapital?.districts?.length || 0} 
                icon="🏘️" 
              />
              <StatCard 
                title="Total Contributions" 
                value={statistics.totalCapitalContributions.toLocaleString()} 
                icon="💰" 
              />
            </div>
            
            <CapitalRaidsCard capitalRaids={capitalRaids} />
            
            {/* Top Contributors */}
            <div className="card p-6">
              <h2 className="text-xl font-bold text-white mb-4">🏆 Top Capital Contributors</h2>
              <div className="space-y-2">
                {players
                  .sort((a, b) => b.clanCapitalContributions - a.clanCapitalContributions)
                  .slice(0, 10)
                  .map((player, i) => (
                    <div
                      key={player.tag}
                      className="flex items-center justify-between bg-slate-800/50 rounded-lg p-3 cursor-pointer hover:bg-slate-800"
                      onClick={() => setSelectedPlayer(player)}
                    >
                      <div className="flex items-center gap-3">
                        <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                          i === 0 ? 'bg-yellow-500 text-black' :
                          i === 1 ? 'bg-slate-300 text-black' :
                          i === 2 ? 'bg-amber-600 text-white' :
                          'bg-slate-700 text-white'
                        }`}>
                          {i + 1}
                        </span>
                        <div>
                          <p className="text-white font-medium">{player.name}</p>
                          <p className="text-xs text-slate-400">TH{player.townHallLevel}</p>
                        </div>
                      </div>
                      <p className="text-amber-400 font-bold">
                        {player.clanCapitalContributions.toLocaleString()}
                      </p>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* Player Modal */}
        {selectedPlayer && (
          <PlayerModal
            player={selectedPlayer}
            onClose={() => setSelectedPlayer(null)}
          />
        )}

        {/* Footer */}
        <footer className="text-center text-slate-500 text-sm mt-8 pb-4">
          <p>Clash of Clans Dashboard • Data from CoC API</p>
          <p className="text-xs mt-1">
            Run <code className="text-orange-400">python api/clan_analyzer.py</code> to update data
          </p>
        </footer>
      </div>
    </div>
  );
}
