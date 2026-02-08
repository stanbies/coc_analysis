import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { CoC, getRushColor, getRoleIcon } from '@/constants/theme';
import { useData } from '@/context/DataContext';
import ClanHeader from '@/components/ClanHeader';
import StatCard from '@/components/StatCard';
import PlayerCard from '@/components/PlayerCard';
import THDistributionChart from '@/components/THDistributionChart';
import RushAnalysisChart from '@/components/RushAnalysisChart';

export default function OverviewScreen() {
  const { data, loading, error, setSelectedPlayer } = useData();
  const router = useRouter();

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={CoC.primary} />
        <Text style={styles.loadingText}>Loading clan data...</Text>
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorIcon}>⚠️</Text>
        <Text style={styles.errorTitle}>No Data Available</Text>
        <Text style={styles.errorText}>{error || 'Could not load clan data.'}</Text>
      </View>
    );
  }

  const { clan, players, statistics } = data;
  const totalWars = clan.warWins + clan.warTies + clan.warLosses;
  const winRate = totalWars > 0 ? ((clan.warWins / totalWars) * 100).toFixed(1) : '0';

  const handlePlayerPress = (player: typeof players[0]) => {
    setSelectedPlayer(player);
    router.push('/modal');
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <ClanHeader clan={clan} lastUpdated={data.lastUpdated} />

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <View style={styles.statHalf}>
          <StatCard title="Members" value={clan.members} icon="👥" subtitle="/50" />
        </View>
        <View style={styles.statHalf}>
          <StatCard title="Clan Level" value={clan.clanLevel} icon="⭐" />
        </View>
        <View style={styles.statHalf}>
          <StatCard title="War Wins" value={clan.warWins} icon="🏆" />
        </View>
        <View style={styles.statHalf}>
          <StatCard title="Win Rate" value={`${winRate}%`} icon="📈" />
        </View>
        <View style={styles.statHalf}>
          <StatCard title="Rushed" value={statistics.rushedCount} icon="⚠️" subtitle={`of ${players.length}`} />
        </View>
        <View style={styles.statHalf}>
          <StatCard title="Avg Rush Score" value={statistics.averageRushScore.toFixed(1)} icon="🔍" />
        </View>
      </View>

      {/* Charts */}
      <THDistributionChart statistics={statistics} />
      <View style={{ height: 12 }} />
      <RushAnalysisChart statistics={statistics} />

      {/* Top Players */}
      <Text style={styles.sectionTitle}>🏆 Top Players</Text>
      <View style={styles.playerCardsGrid}>
        {players
          .sort((a, b) => b.trophies - a.trophies)
          .slice(0, 4)
          .map(player => (
            <View key={player.tag} style={styles.playerCardHalf}>
              <PlayerCard player={player} onPress={() => handlePlayerPress(player)} />
            </View>
          ))}
      </View>

      {/* Most Rushed Players */}
      <View style={styles.card}>
        <Text style={styles.sectionTitleInCard}>⚠️ Most Rushed Players</Text>
        {players
          .filter(p => p.rushAnalysis.isRushed)
          .sort((a, b) => b.rushAnalysis.rushScore - a.rushAnalysis.rushScore)
          .slice(0, 10)
          .map((player, i) => (
            <TouchableOpacity
              key={player.tag}
              style={styles.rushedRow}
              onPress={() => handlePlayerPress(player)}
              activeOpacity={0.7}
            >
              <Text style={styles.rushedRank}>{i + 1}</Text>
              <View style={styles.rushedInfo}>
                <Text style={styles.rushedName}>{player.name}</Text>
                <View style={styles.rushedMeta}>
                  <View style={styles.thPill}>
                    <Text style={styles.thPillText}>TH{player.townHallLevel}</Text>
                  </View>
                  <Text style={[styles.rushScore, { color: CoC.primary }]}>
                    {player.rushAnalysis.rushScore.toFixed(1)}
                  </Text>
                  <Text style={[styles.rushMissing, { color: CoC.red }]}>
                    -{player.rushAnalysis.totalMissingHeroLevels}
                  </Text>
                </View>
              </View>
            </TouchableOpacity>
          ))}
      </View>

      <View style={{ height: 20 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: CoC.background,
  },
  content: {
    padding: 16,
    paddingTop: 8,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: CoC.background,
    padding: 20,
  },
  loadingText: {
    color: CoC.textSecondary,
    marginTop: 12,
    fontSize: 14,
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  errorTitle: {
    color: CoC.text,
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 8,
  },
  errorText: {
    color: CoC.textSecondary,
    fontSize: 14,
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 16,
  },
  statHalf: {
    width: '48%',
    flexGrow: 1,
  },
  sectionTitle: {
    color: CoC.text,
    fontSize: 18,
    fontWeight: '700',
    marginTop: 20,
    marginBottom: 12,
  },
  playerCardsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 16,
  },
  playerCardHalf: {
    width: '48%',
    flexGrow: 1,
  },
  card: {
    backgroundColor: CoC.card,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: CoC.cardBorder,
    marginTop: 16,
  },
  sectionTitleInCard: {
    color: CoC.text,
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
  },
  rushedRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: CoC.slate800,
  },
  rushedRank: {
    color: CoC.textMuted,
    fontSize: 14,
    width: 24,
  },
  rushedInfo: {
    flex: 1,
  },
  rushedName: {
    color: CoC.text,
    fontSize: 14,
    fontWeight: '500',
  },
  rushedMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 4,
  },
  thPill: {
    backgroundColor: CoC.primary,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  thPillText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
  },
  rushScore: {
    fontSize: 12,
    fontWeight: '600',
  },
  rushMissing: {
    fontSize: 11,
  },
});
