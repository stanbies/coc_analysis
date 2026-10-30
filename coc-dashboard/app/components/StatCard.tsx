'use client';

import GameIcon, { IconName } from './GameIcon';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: IconName;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export default function StatCard({ title, value, icon, subtitle, trend }: StatCardProps) {
  return (
    <div className="stat-card rounded-xl p-6 transition-all duration-300 hover:scale-[1.02]">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-white mt-1">
            {typeof value === 'number' ? value.toLocaleString('en-US') : value}
          </p>
          {subtitle && (
            <p className="text-slate-500 text-xs mt-1">{subtitle}</p>
          )}
        </div>
        <GameIcon name={icon} size={44} className="drop-shadow-[0_3px_0_rgba(0,0,0,0.4)]" />
      </div>
      {trend && (
        <div className={`mt-2 text-xs ${
          trend === 'up' ? 'text-green-400' : 
          trend === 'down' ? 'text-red-400' : 'text-slate-400'
        }`}>
          {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} 
        </div>
      )}
    </div>
  );
}
