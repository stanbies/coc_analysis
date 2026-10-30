// Official Clash of Clans art from Supercell's fan kit (fankit.supercell.com),
// trimmed and scaled to 128px in public/icons. Used unmodified otherwise, as
// the Fan Content Policy requires; the footer carries the required notice.
// The one exception is trophy.svg, which we drew ourselves.
const ICONS = {
  barbarian: 'barbarian.png',
  barbarianKing: 'barbarian-king.png',
  battle: 'battle.png',
  capitalGold: 'capital-gold.png',
  capitalHall: 'capital-hall.png',
  capitalTrophy: 'capital-trophy.png',
  clanWar: 'clan-war.png',
  crown: 'crown.png',
  cwl: 'cwl.png',
  districtHall: 'district-hall.png',
  legendShield: 'legend-shield.png',
  magnifier: 'magnifier.png',
  raid: 'raid.png',
  spells: 'spells.png',
  standardShield: 'standard-shield.png',
  star: 'star.png',
  threeStars: 'three-stars.png',
  townHall: 'town-hall.png',
  troops: 'troops.png',
  trophy: 'trophy.svg', // our own drawing: the fan kit has no regular trophy
  upgradeHammer: 'upgrade-hammer.png',
} as const;

export type IconName = keyof typeof ICONS;

interface GameIconProps {
  name: IconName;
  // Rendered size in pixels (square)
  size?: number;
  className?: string;
  // Leave empty when the icon sits next to text that says the same thing
  alt?: string;
}

export default function GameIcon({ name, size = 24, className = '', alt = '' }: GameIconProps) {
  return (
    // eslint-disable-next-line @next/next/no-img-element -- tiny static PNGs, next/image adds nothing here
    <img
      src={`/icons/${ICONS[name]}`}
      alt={alt}
      width={size}
      height={size}
      className={`inline-block shrink-0 object-contain align-middle ${className}`}
      draggable={false}
    />
  );
}

// Clan role → icon and label; shared by the player card, table and modal
export function roleIcon(role: string): { icon: IconName; label: string } {
  switch (role) {
    case 'leader': return { icon: 'crown', label: 'Leader' };
    case 'coLeader': return { icon: 'legendShield', label: 'Co-Leader' };
    case 'admin': return { icon: 'standardShield', label: 'Elder' };
    default: return { icon: 'barbarian', label: 'Member' };
  }
}
