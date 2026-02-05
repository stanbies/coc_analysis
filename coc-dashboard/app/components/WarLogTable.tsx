'use client';

import { WarLogEntry } from '../types';

interface WarLogTableProps {
  warLog: WarLogEntry[];
}

function getResultIcon(result: string): string {
  switch (result) {
    case 'win': return '✅';
    case 'lose': return '❌';
    case 'tie': return '➖';
    default: return '❓';
  }
}

function getResultClass(result: string): string {
  switch (result) {
    case 'win': return 'text-green-400';
    case 'lose': return 'text-red-400';
    case 'tie': return 'text-yellow-400';
    default: return 'text-slate-400';
  }
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

  const wins = warLog.filter(w => w.result === 'win').length;
  const losses = warLog.filter(w => w.result === 'lose').length;
  const ties = warLog.filter(w => w.result === 'tie').length;

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
            {warLog.slice(0, 20).map((war, i) => (
              <tr key={i} className="border-b border-slate-800 table-row transition-colors">
                <td className="py-3 px-2">
                  <span className={`font-medium ${getResultClass(war.result)}`}>
                    {getResultIcon(war.result)} {war.result?.toUpperCase()}
                  </span>
                </td>
                <td className="py-3 px-2">
                  <span className="text-white">{war.opponent.name}</span>
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
