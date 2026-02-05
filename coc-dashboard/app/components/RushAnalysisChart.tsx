'use client';

import { Statistics } from '../types';

interface RushAnalysisChartProps {
  statistics: Statistics;
}

export default function RushAnalysisChart({ statistics }: RushAnalysisChartProps) {
  const rushData = statistics.rushDistribution;
  const total = Object.values(rushData).reduce((sum, val) => sum + val, 0);
  
  const colors: Record<string, string> = {
    'Maxed': '#22c55e',
    'Slightly Behind': '#84cc16',
    'Moderately Rushed': '#eab308',
    'Rushed': '#f97316',
    'Severely Rushed': '#ef4444',
    'Other': '#64748b',
  };
  
  const sortOrder = ['Maxed', 'Slightly Behind', 'Moderately Rushed', 'Rushed', 'Severely Rushed', 'Other'];
  const sortedEntries = Object.entries(rushData).sort((a, b) => {
    return sortOrder.indexOf(a[0]) - sortOrder.indexOf(b[0]);
  });

  return (
    <div className="card p-6">
      <h2 className="text-xl font-bold text-white mb-4">🔍 Rush Analysis Distribution</h2>
      
      <div className="flex items-center gap-4 mb-6">
        <div className="text-center">
          <p className="text-3xl font-bold text-orange-400">{statistics.rushedCount}</p>
          <p className="text-xs text-slate-400">Rushed Players</p>
        </div>
        <div className="text-center">
          <p className="text-3xl font-bold text-cyan-400">{statistics.averageRushScore.toFixed(1)}</p>
          <p className="text-xs text-slate-400">Avg Rush Score</p>
        </div>
      </div>
      
      {/* Progress bar visualization */}
      <div className="h-8 rounded-full overflow-hidden flex mb-4">
        {sortedEntries.map(([status, count]) => {
          const percentage = (count / total) * 100;
          if (percentage === 0) return null;
          return (
            <div
              key={status}
              className="h-full transition-all duration-500"
              style={{
                width: `${percentage}%`,
                backgroundColor: colors[status] || '#64748b',
              }}
              title={`${status}: ${count} (${percentage.toFixed(1)}%)`}
            />
          );
        })}
      </div>
      
      {/* Legend */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {sortedEntries.map(([status, count]) => {
          const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : '0';
          return (
            <div key={status} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: colors[status] || '#64748b' }}
              />
              <span className="text-sm text-slate-300">
                {status}: <span className="text-white font-medium">{count}</span>
                <span className="text-slate-500 ml-1">({percentage}%)</span>
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
