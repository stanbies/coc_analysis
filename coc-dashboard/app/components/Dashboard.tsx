'use client';

import { useState, useSyncExternalStore } from 'react';
import Link from 'next/link';
import { DashboardData, Player } from '../types';
import ClanHeader from './ClanHeader';
import CompactHeader from './CompactHeader';
import { CapitalHero, PlayersHero, WarsHero } from './TabHeroes';
import { WarCompareCard, WarMarginCard, WarResultsCard } from './WarCharts';
import { warSeries } from '../lib/wars';
import { lastRaidResults, raidSeries } from '../lib/capital';
import { benchmarkDots, clanRankedSeries, lastFinishedWeek, zwegersOfTheWeek } from '../lib/ranked';
import ZwegersOfTheWeek from './ZwegersOfTheWeek';
import { BenchmarkDotsCard, BenchmarkShareCard, MissedAttacksCard, RankedTrendCard } from './RankedCharts';
import StatCard from './StatCard';
import PlayerCard from './PlayerCard';
import { compareByLeague } from './LeagueBadge';
import PlayerModal from './PlayerModal';
import PlayersTable from './PlayersTable';
import THDistributionChart from './THDistributionChart';
import RushAnalysisChart from './RushAnalysisChart';
import WarLogTable from './WarLogTable';
import { CapitalLootCard, LastRaidCard, LootPerAttackCard, RaidsCompletedCard } from './CapitalCharts';
import GameIcon, { IconName } from './GameIcon';

type Tab = 'overview' | 'players' | 'wars' | 'capital';
const TABS: Tab[] = ['overview', 'players', 'wars', 'capital'];

// The active tab lives in the URL hash (#wars), so tabs can be linked to and
// the back button moves between them. The server always renders the overview.
function subscribeToHash(onChange: () => void) {
  window.addEventListener('hashchange', onChange);
  return () => window.removeEventListener('hashchange', onChange);
}

function tabFromHash(): Tab {
  const hash = window.location.hash.slice(1);
  return TABS.find(tab => tab === hash) ?? 'overview';
}

function setActiveTab(tab: Tab) {
  window.location.hash = tab;
}

export default function Dashboard({ data }: { data: DashboardData }) {
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const activeTab = useSyncExternalStore(subscribeToHash, tabFromHash, () => 'overview' as Tab);

  const { clan, players, statistics, warLog, capitalRaids, currentWar } = data;
  const totalWars = clan.warWins + clan.warTies + clan.warLosses;
  const winRate = totalWars > 0 ? ((clan.warWins / totalWars) * 100).toFixed(1) : '0';
  const wars = warSeries(warLog);
  const raids = raidSeries(capitalRaids);
  const lastRaid = lastRaidResults(capitalRaids, players);
  const rankedHistory = data.rankedHistory ?? [];
  const benchmarks = data.rankedBenchmarks ?? {};
  const rankedWeeks = clanRankedSeries(rankedHistory, players, benchmarks);
  const dots = benchmarkDots(players, benchmarks);
  const lastRanked = lastFinishedWeek(rankedHistory, players);
  const weekStars = zwegersOfTheWeek(players, rankedHistory, benchmarks);

  return (
    <div className={`scene scene-${activeTab} min-h-screen p-4 md:p-8`}>
      <div className="max-w-7xl mx-auto">
        {/* Full clan banner on the overview, a slim bar on the other tabs */}
        {activeTab === 'overview'
          ? <ClanHeader clan={clan} lastUpdated={data.lastUpdated} />
          : <CompactHeader clan={clan} />}

        {/* Navigation Tabs */}
        <nav className="grid grid-cols-4 gap-2 sm:flex sm:gap-3 mb-6 px-1 pt-1 pb-3">
          {([
            { id: 'overview', label: 'Overview', icon: 'townHall' },
            { id: 'players', label: 'Players', icon: 'barbarian' },
            { id: 'wars', label: 'Wars', icon: 'clanWar' },
            { id: 'capital', label: 'Capital', icon: 'capitalHall' },
          ] satisfies { id: Tab; label: string; icon: IconName }[]).map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              aria-current={activeTab === tab.id ? 'page' : undefined}
              className={`coc-btn ${activeTab === tab.id ? 'coc-btn-gold' : ''} flex flex-col sm:flex-row items-center gap-0.5 sm:gap-2 px-1 sm:px-5 py-1.5 sm:py-2 whitespace-nowrap`}
            >
              <GameIcon name={tab.icon} size={28} />
              <span className="coc-text text-sm sm:text-lg">{tab.label}</span>
            </button>
          ))}
        </nav>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
              <StatCard title="Members" value={clan.members} icon="barbarian" subtitle="/50" />
              <StatCard title="Clan Level" value={clan.clanLevel} icon="star" />
              <StatCard title="War Wins" value={clan.warWins} icon="clanWar" />
              <StatCard title="Win Rate" value={`${winRate}%`} icon="threeStars" />
              <StatCard title="Rushed" value={statistics.rushedCount} icon="upgradeHammer" subtitle={`of ${players.length}`} />
              <StatCard title="Avg Rush Score" value={statistics.averageRushScore.toFixed(1)} icon="magnifier" />
            </div>

            {/* Only once the export carries ranked history and benchmarks (Nov 2026 onwards) */}
            {weekStars && Object.keys(benchmarks).length > 0 && <ZwegersOfTheWeek {...weekStars} />}

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <THDistributionChart statistics={statistics} />
              <RushAnalysisChart statistics={statistics} />
            </div>

            {/* Top Players Cards */}
            <div className="mb-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><GameIcon name="crown" size={28} /> Top Players</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[...players]
                  .sort(compareByLeague)
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
              <div className="flex items-center justify-between gap-4 mb-4">
                <h2 className="text-xl font-bold text-white flex items-center gap-2"><GameIcon name="upgradeHammer" size={28} /> Most Rushed Players</h2>
                <Link href="/rush-score" className="text-sm font-normal text-orange-400 hover:text-orange-300">How is this calculated?</Link>
              </div>
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
          <div className="space-y-6">
            <PlayersHero players={players} />
            {rankedWeeks.length > 1 && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <RankedTrendCard weeks={rankedWeeks} />
                <BenchmarkShareCard weeks={rankedWeeks} />
              </div>
            )}
            {dots.length > 0 && <BenchmarkDotsCard dots={dots} />}
            {lastRanked && <MissedAttacksCard {...lastRanked} />}
            <PlayersTable players={players} rankedHistory={rankedHistory} onPlayerClick={setSelectedPlayer} />
          </div>
        )}

        {/* Wars Tab */}
        {activeTab === 'wars' && (
          <div className="space-y-6">
            <WarsHero clan={clan} currentWar={currentWar} />
            {wars.length > 0 && (
              <>
                <WarResultsCard wars={wars} />
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <WarMarginCard wars={wars} clanName={clan.name} />
                  <WarCompareCard
                    wars={wars}
                    clanName={clan.name}
                    icon="battle"
                    title="Destruction per war"
                    subtitle="Average destruction over all bases"
                    ourKey="ourDestruction"
                    theirKey="theirDestruction"
                  />
                </div>
              </>
            )}

            <WarLogTable warLog={warLog} />
          </div>
        )}

        {/* Capital Tab */}
        {activeTab === 'capital' && (
          <div className="space-y-6">
            <CapitalHero clan={clan} capitalRaids={capitalRaids} players={players} />

            {raids.length > 0 && (
              <>
                <CapitalLootCard raids={raids} />
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <LootPerAttackCard raids={raids} />
                  <RaidsCompletedCard raids={raids} />
                </div>
              </>
            )}
            {lastRaid && <LastRaidCard {...lastRaid} />}

            {/* Top Contributors */}
            <div className="card p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2"><GameIcon name="capitalGold" size={28} /> Top Capital Contributors</h2>
              <div className="space-y-2">
                {[...players]
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
                        {player.clanCapitalContributions.toLocaleString('en-US')}
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
        <footer className="text-center text-slate-300 text-sm mt-8 pb-4">
          <p>Clash of Clans Dashboard • Data from CoC API</p>
          <p className="text-xs mt-1">Data updates automatically every 6 hours</p>
          <p className="text-xs mt-3 text-slate-400">
            This material is unofficial and is not endorsed by Supercell. For more information see{' '}
            <a href="https://www.supercell.com/fan-content-policy" className="underline hover:text-white">
              Supercell&apos;s Fan Content Policy
            </a>.
          </p>
        </footer>
      </div>
    </div>
  );
}
