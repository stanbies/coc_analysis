import GameIcon, { IconName } from './GameIcon';

interface ResourceBarProps {
  icon: IconName;
  label: string;
  value: string;
  color: string;
  // Share of the bar that's filled, 0-100; a full bar when there's no maximum
  fill?: number;
}

// A stat shown like the in-game gold/elixir storage bars
export default function ResourceBar({ icon, label, value, color, fill = 100 }: ResourceBarProps) {
  return (
    <div className="min-w-0">
      <p className="coc-text text-xs mb-1 pl-11">{label}</p>
      <div className="relative pl-4">
        <span className="coc-resource-icon"><GameIcon name={icon} size={30} /></span>
        <div className="coc-resource" style={{ '--fill': color } as React.CSSProperties}>
          <div className="coc-resource-fill" style={{ width: `${Math.min(100, Math.max(0, fill))}%` }} />
          <span className="coc-text relative flex h-full items-center justify-end pr-3 text-lg">
            {value}
          </span>
        </div>
      </div>
    </div>
  );
}
