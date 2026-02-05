'use client';

import { Statistics } from '../types';

interface THDistributionChartProps {
  statistics: Statistics;
}

export default function THDistributionChart({ statistics }: THDistributionChartProps) {
  const thData = statistics.thDistribution;
  const maxCount = Math.max(...Object.values(thData), 1);
  
  // Sort by TH level descending
  const sortedEntries = Object.entries(thData)
    .map(([th, count]) => ({ th: parseInt(th), count }))
    .sort((a, b) => b.th - a.th);

  const thColors: Record<number, string> = {
    17: '#ef4444',
    16: '#f97316',
    15: '#eab308',
    14: '#84cc16',
    13: '#22c55e',
    12: '#14b8a6',
    11: '#06b6d4',
    10: '#3b82f6',
    9: '#8b5cf6',
    8: '#a855f7',
    7: '#d946ef',
  };

  return (
    <div className="card p-6">
      <h2 className="text-xl font-bold text-white mb-4">🏠 Town Hall Distribution</h2>
      
      <div className="space-y-3">
        {sortedEntries.map(({ th, count }) => {
          const percentage = (count / maxCount) * 100;
          const color = thColors[th] || '#64748b';
          
          return (
            <div key={th} className="flex items-center gap-3">
              <div className="w-12 text-right">
                <span className="text-sm font-medium text-white">TH{th}</span>
              </div>
              <div className="flex-1 h-8 bg-slate-800 rounded-lg overflow-hidden">
                <div
                  className="h-full rounded-lg flex items-center justify-end pr-2 transition-all duration-500"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: color,
                    minWidth: count > 0 ? '2rem' : '0',
                  }}
                >
                  <span className="text-xs font-bold text-white drop-shadow">{count}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 pt-4 border-t border-slate-700">
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Total Members:</span>
          <span className="text-white font-medium">
            {Object.values(thData).reduce((sum, val) => sum + val, 0)}
          </span>
        </div>
      </div>
    </div>
  );
}
