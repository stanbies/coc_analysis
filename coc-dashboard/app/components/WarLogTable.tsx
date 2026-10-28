'use client';

import { WarLogEntry } from '../types';

interface WarLogTableProps {
  warLog: WarLogEntry[];
}

// CWL rounds appear in the war log without a result or opponent
function getResultIcon(result: string | null): string {
  switch (result) {
    case 'win': return '✅';
    case 'lose': return '❌';
    case 'tie': return '➖';
    case null: return '🏆';
    default: return '❓';
  }
}

function getResultClass(result: string | null): string {
  switch (result) {
    case 'win': return 'text-green-400';
    case 'lose': return 'text-red-400';
    case 'tie': return 'text-yellow-400';
    default: return 'text-slate-400';
  }
}

// The API mixes Clan War League seasons into the war log: no opponent, stars and
// destruction summed over all league rounds, and a result that is often missing.
function isCwlEntry(war: WarLogEntry): boolean {
  return !war.opponent?.tag;
}

function cwlSeasonLabel(endTime: string): string {
  // endTime looks like 20261010T131722.000Z
  const date = new Date(Date.UTC(Number(endTime.slice(0, 4)), Number(endTime.slice(4, 6)) - 1, 1));
  return date.toLocaleString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' });
}

export default function WarLogTable({ warLog }: WarLogTableProps) {
  if (!warLog || warLog.length === 0) {
    return (
      <div className="card p-6">
        <h2 className="text-xl font-bold text-white mb-4">📜 War Log</h2>
        <p className="text-slate-400">No war log data available or war log is private.</p>
      </div>
    );
  }

  const regularWars = warLog.filter(w => !isCwlEntry(w));
  const wins = regularWars.filter(w => w.result === 'win').length;
  const losses = regularWars.filter(w => w.result === 'lose').length;
  const ties = regularWars.filter(w => w.result === 'tie').length;

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">📜 War Log</h2>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-green-400">✅ {wins}W</span>
          <span className="text-red-400">❌ {losses}L</span>
          <span className="text-yellow-400">➖ {ties}T</span>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3 px-2 text-slate-400 text-sm font-medium">Result</th>
              <th className="text-left py-3 px-2 text-slate-400 text-sm font-medium">Opponent</th>
              <th className="text-center py-3 px-2 text-slate-400 text-sm font-medium">Size</th>
              <th className="text-center py-3 px-2 text-slate-400 text-sm font-medium">Stars</th>
              <th className="text-center py-3 px-2 text-slate-400 text-sm font-medium">Destruction</th>
            </tr>
          </thead>
          <tbody>
            {warLog.slice(0, 20).map((war, i) => isCwlEntry(war) ? (
              <tr key={i} className="border-b border-slate-800 table-row transition-colors">
                <td className="py-3 px-2">
                  <span className="font-medium text-purple-400">🏆 CWL</span>
                </td>
                <td className="py-3 px-2">
                  <span className="text-white">Clan War League</span>
                  {war.endTime && (
                    <span className="text-slate-500 text-sm"> · {cwlSeasonLabel(war.endTime)}</span>
                  )}
                </td>
                <td className="py-3 px-2 text-center text-slate-300">
                  {war.teamSize}v{war.teamSize}
                </td>
                <td className="py-3 px-2 text-center">
                  <span className="text-yellow-400">{war.clan.stars}</span>
                  <span className="text-slate-500"> - </span>
                  <span className="text-slate-400">{war.opponent.stars}</span>
                  <span className="block text-xs text-slate-500">season total</span>
                </td>
                <td className="py-3 px-2 text-center text-slate-500">—</td>
              </tr>
            ) : (
              <tr key={i} className="border-b border-slate-800 table-row transition-colors">
                <td className="py-3 px-2">
                  <span className={`font-medium ${getResultClass(war.result)}`}>
                    {getResultIcon(war.result)} {war.result?.toUpperCase() ?? 'CWL'}
                  </span>
                </td>
                <td className="py-3 px-2">
                  <span className="text-white">{war.opponent.name ?? <span className="text-slate-400">Clan War League</span>}</span>
                </td>
                <td className="py-3 px-2 text-center text-slate-300">
                  {war.teamSize}v{war.teamSize}
                </td>
                <td className="py-3 px-2 text-center">
                  <span className="text-yellow-400">{war.clan.stars}</span>
                  <span className="text-slate-500"> - </span>
                  <span className="text-slate-400">{war.opponent.stars}</span>
                </td>
                <td className="py-3 px-2 text-center">
                  <span className="text-cyan-400">{war.clan.destructionPercentage?.toFixed(1)}%</span>
                  <span className="text-slate-500"> - </span>
                  <span className="text-slate-400">{war.opponent.destructionPercentage?.toFixed(1)}%</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
