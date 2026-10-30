import { CapitalRaid, Clan, CurrentWar, Player } from '../types';
import { getLeagueIcon, leagueName, leagueNumber } from './LeagueBadge';
import TabHero, { HeroStat } from './TabHero';

const fmt = (n: number) => n.toLocaleString('en-US');

export function PlayersHero({ players }: { players: Player[] }) {
  const count = (role: string) => players.filter(p => p.role === role).length;
  const townHalls = players.map(p => p.townHallLevel);
  const avgTownHall = townHalls.reduce((a, b) => a + b, 0) / (townHalls.length || 1);
  const ranked = players.map(p => leagueNumber(p.leagueTier)).filter(n => n > 0);
  const avgLeague = Math.round(ranked.reduce((a, b) => a + b, 0) / (ranked.length || 1));
  // League icons only come with the API data, so borrow one from the member
  // whose league is closest to the average (usually exactly it)
  const closest = players
    .filter(p => leagueNumber(p.leagueTier) > 0)
    .sort((a, b) => Math.abs(leagueNumber(a.leagueTier) - avgLeague) - Math.abs(leagueNumber(b.leagueTier) - avgLeague))[0];
  const donations = players.reduce((sum, p) => sum + p.donations, 0);

  return (
    <TabHero
      variant="players"
      icon="barbarian"
      title="Members"
      subtitle={`${count('leader')} leader · ${count('coLeader')} co-leaders · ${count('admin')} elders`}
    >
      <HeroStat icon="barbarian" label="Members" value={`${players.length}/50`} />
      <HeroStat
        icon="townHall"
        label="Average Town Hall"
        value={`TH${avgTownHall.toFixed(1)}`}
        detail={`TH${Math.min(...townHalls)} to TH${Math.max(...townHalls)}`}
      />
      <HeroStat
        icon="trophy"
        imageUrl={getLeagueIcon(closest?.leagueTier)}
        label="Average ranked league"
        value={ranked.length ? leagueName(avgLeague) : 'Unranked'}
        detail={`${players.length - ranked.length} unranked`}
      />
      <HeroStat icon="troops" label="Donations" value={fmt(donations)} detail="this season" />
    </TabHero>
  );
}

function currentWarStat(war: CurrentWar | null) {
  if (!war) return { value: 'No war', detail: 'waiting for the next one' };
  const against = `vs ${war.opponent.name} · ${war.teamSize}v${war.teamSize}`;
  switch (war.state) {
    case 'preparation': return { value: 'Preparation day', detail: against };
    case 'inWar': return { value: `${war.clan.stars} - ${war.opponent.stars} stars`, detail: `Battle day ${against}` };
    case 'warEnded': return { value: `${war.clan.stars} - ${war.opponent.stars} stars`, detail: `Ended ${against}` };
    default: return { value: war.state, detail: against };
  }
}

export function WarsHero({ clan, currentWar }: { clan: Clan; currentWar: CurrentWar | null }) {
  const totalWars = clan.warWins + clan.warTies + clan.warLosses;
  const winRate = totalWars > 0 ? (clan.warWins / totalWars) * 100 : 0;
  const now = currentWarStat(currentWar);

  return (
    <TabHero variant="wars" icon="clanWar" title="Clan Wars" subtitle={clan.warLeague?.name}>
      <HeroStat icon="clanWar" label="Current war" value={now.value} detail={now.detail} />
      <HeroStat
        icon="threeStars"
        label="Record"
        value={`${clan.warWins} - ${clan.warLosses} - ${clan.warTies}`}
        detail="wins - losses - ties"
      />
      <HeroStat icon="star" label="Win rate" value={`${winRate.toFixed(1)}%`} detail={`${totalWars} wars`} />
      <HeroStat icon="battle" label="Win streak" value={clan.warWinStreak} />
    </TabHero>
  );
}

export function CapitalHero({ clan, capitalRaids, players }: {
  clan: Clan;
  capitalRaids: CapitalRaid[];
  players: Player[];
}) {
  // The newest weekend is often still running (or just started), so show the last finished one
  const raid = capitalRaids.find(r => r.state === 'ended');
  const contributions = players.reduce((sum, p) => sum + p.clanCapitalContributions, 0);

  return (
    <TabHero variant="capital" icon="capitalHall" title="Clan Capital" subtitle={clan.capitalLeague?.name}>
      <HeroStat
        icon="capitalHall"
        label="Capital Hall"
        value={`Level ${clan.clanCapital?.capitalHallLevel ?? 0}`}
        detail={`${clan.clanCapital?.districts?.length ?? 0} districts`}
      />
      <HeroStat icon="capitalTrophy" label="Capital points" value={fmt(clan.clanCapitalPoints ?? 0)} />
      {raid && (
        <HeroStat
          icon="raid"
          label="Last raid weekend"
          value={`${fmt(raid.capitalTotalLoot)} loot`}
          detail={`${raid.totalAttacks} attacks · ${raid.raidsCompleted} raids`}
        />
      )}
      <HeroStat icon="capitalGold" label="Contributions" value={fmt(contributions)} detail="all members, all time" />
    </TabHero>
  );
}
