export interface Player {
  tag: string;
  name: string;
  townHallLevel: number;
  townHallWeaponLevel?: number;
  expLevel: number;
  trophies: number;
  bestTrophies: number;
  warStars: number;
  attackWins: number;
  defenseWins: number;
  builderHallLevel?: number;
  builderBaseTrophies?: number;
  bestBuilderBaseTrophies?: number;
  role: string;
  warPreference?: string;
  donations: number;
  donationsReceived: number;
  clanCapitalContributions: number;
  clan?: {
    tag: string;
    name: string;
    clanLevel: number;
    badgeUrls: BadgeUrls;
  };
  league?: League;
  builderBaseLeague?: League;
  achievements: Achievement[];
  labels: Label[];
  heroes: HeroTroop[];
  troops: HeroTroop[];
  spells: HeroTroop[];
  heroEquipment: HeroEquipment[];
  rushAnalysis: RushAnalysis;
  warStats: WarStats;
}

export interface HeroTroop {
  name: string;
  level: number;
  maxLevel: number;
}

export interface HeroEquipment {
  name: string;
  level: number;
  maxLevel: number;
  village: string;
}

export interface RushAnalysis {
  isRushed: boolean;
  rushScore: number;
  rushPercentage: number;
  status: string;
  heroScore: number;
  troopScore: number;
  spellScore: number;
  totalMissingHeroLevels: number;
  rushedHeroes: RushedItem[];
  rushedTroops: RushedItem[];
  rushedSpells: RushedItem[];
}

export interface RushedItem {
  name: string;
  current: number;
  target: number;
  missing: number;
}

export interface WarStats {
  totalAttacks: number;
  totalStars: number;
  totalDestruction: number;
  threeStars: number;
  twoStars: number;
  oneStars: number;
  zeroStars: number;
  warsParticipated: number;
}

export interface League {
  id: number;
  name: string;
  iconUrls?: {
    small: string;
    tiny: string;
    medium?: string;
  };
}

export interface Label {
  id: number;
  name: string;
  iconUrls: {
    small: string;
    medium: string;
  };
}

export interface Achievement {
  name: string;
  stars: number;
  value: number;
  target: number;
  info: string;
  completionInfo?: string;
  village: string;
}

export interface BadgeUrls {
  small: string;
  large: string;
  medium: string;
}

export interface Clan {
  tag: string;
  name: string;
  description: string;
  type: string;
  location?: {
    id: number;
    name: string;
    isCountry: boolean;
    countryCode?: string;
  };
  chatLanguage?: {
    id: number;
    name: string;
    languageCode: string;
  };
  clanLevel: number;
  clanPoints: number;
  clanBuilderBasePoints: number;
  clanCapitalPoints: number;
  capitalLeague?: League;
  requiredTrophies: number;
  warFrequency: string;
  warWinStreak: number;
  warWins: number;
  warTies: number;
  warLosses: number;
  isWarLogPublic: boolean;
  warLeague?: League;
  members: number;
  labels: Label[];
  clanCapital?: {
    capitalHallLevel: number;
    districts: {
      id: number;
      name: string;
      districtHallLevel: number;
    }[];
  };
  badgeUrls: BadgeUrls;
}

export interface WarLogEntry {
  result: string;
  endTime: string;
  teamSize: number;
  attacksPerMember: number;
  clan: {
    tag: string;
    name: string;
    stars: number;
    destructionPercentage: number;
    expEarned: number;
  };
  opponent: {
    tag: string;
    name: string;
    stars: number;
    destructionPercentage: number;
  };
}

export interface CapitalRaid {
  state: string;
  startTime: string;
  endTime: string;
  capitalTotalLoot: number;
  raidsCompleted: number;
  totalAttacks: number;
  enemyDistrictsDestroyed: number;
  offensiveReward: number;
  defensiveReward: number;
  members: CapitalRaidMember[];
  attackLog: unknown[];
  defenseLog: unknown[];
}

export interface CapitalRaidMember {
  tag: string;
  name: string;
  attacks: number;
  attackLimit: number;
  bonusAttackLimit: number;
  capitalResourcesLooted: number;
}

export interface Statistics {
  thDistribution: Record<string, number>;
  roleDistribution: Record<string, number>;
  leagueDistribution: Record<string, number>;
  rushDistribution: Record<string, number>;
  totalWarStars: number;
  totalDonations: number;
  totalCapitalContributions: number;
  averageTrophies: number;
  rushedCount: number;
  averageRushScore: number;
}

export interface DashboardData {
  lastUpdated: string;
  clan: Clan;
  players: Player[];
  warLog: WarLogEntry[];
  currentWar: unknown | null;
  capitalRaids: CapitalRaid[];
  goldPass: {
    startTime: string;
    endTime: string;
  } | null;
  cwlGroup: unknown | null;
  historicalData: {
    cwlSeasons: Record<string, unknown>;
    lastUpdated: string;
  };
  statistics: Statistics;
}
