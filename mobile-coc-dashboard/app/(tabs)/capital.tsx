import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { CoC } from '@/constants/theme';
import { useData } from '@/context/DataContext';
import StatCard from '@/components/StatCard';
import CapitalRaidsCard from '@/components/CapitalRaidsCard';

export default function CapitalScreen() {
  const { data, loading, error, setSelectedPlayer } = useData();
  const router = useRouter();

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={CoC.primary} />
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>No data available</Text>
      </View>
    );
  }

  const { clan, players, statistics, capitalRaids } = data;

  const handlePlayerPress = (player: typeof players[0]) => {
    setSelectedPlayer(player);
    router.push('/modal');
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <View style={styles.statsGrid}>
        <View style={styles.statHalf}>
          <StatCard
            title="Capital Points"
            value={clan.clanCapitalPoints?.toLocaleString() || 0}
            icon="🏛️"
          />
        </View>
        <View style={styles.statHalf}>
          <StatCard
            title="Capital Hall"
            value={clan.clanCapital?.capitalHallLevel || 0}
            icon="🏰"
          />
        </View>
        <View style={styles.statHalf}>
          <StatCard
            title="Districts"
            value={clan.clanCapital?.districts?.length || 0}
            icon="🏘️"
          />
        </View>
        <View style={styles.statHalf}>
          <StatCard
            title="Total Contributions"
            value={statistics.totalCapitalContributions.toLocaleString()}
            icon="💰"
          />
        </View>
      </View>

      <CapitalRaidsCard capitalRaids={capitalRaids} />

      {/* Top Contributors */}
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>🏆 Top Capital Contributors</Text>
        {players
          .sort((a, b) => b.clanCapitalContributions - a.clanCapitalContributions)
          .slice(0, 10)
          .map((player, i) => (
            <TouchableOpacity
              key={player.tag}
              style={styles.contributorRow}
              onPress={() => handlePlayerPress(player)}
              activeOpacity={0.7}
            >
              <View style={styles.contributorLeft}>
                <View style={[
                  styles.rankBadge,
                  i === 0 ? styles.rank1 : i === 1 ? styles.rank2 : i === 2 ? styles.rank3 : styles.rankDefault,
                ]}>
                  <Text style={[
                    styles.rankText,
                    (i === 0 || i === 1) ? { color: '#000' } : { color: '#fff' },
                  ]}>{i + 1}</Text>
                </View>
                <View>
                  <Text style={styles.contributorName}>{player.name}</Text>
                  <Text style={styles.contributorTh}>TH{player.townHallLevel}</Text>
                </View>
              </View>
              <Text style={styles.contributorAmount}>
                {player.clanCapitalContributions.toLocaleString()}
              </Text>
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
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: CoC.background,
  },
  errorText: {
    color: CoC.textSecondary,
    fontSize: 14,
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
  card: {
    backgroundColor: CoC.card,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: CoC.cardBorder,
    marginTop: 16,
  },
  sectionTitle: {
    color: CoC.text,
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
  },
  contributorRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'rgba(30,41,59,0.5)',
    borderRadius: 10,
    padding: 12,
    marginBottom: 6,
  },
  contributorLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  rankBadge: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  rank1: { backgroundColor: '#eab308' },
  rank2: { backgroundColor: '#94a3b8' },
  rank3: { backgroundColor: '#d97706' },
  rankDefault: { backgroundColor: CoC.slate700 },
  rankText: {
    fontSize: 12,
    fontWeight: '700',
  },
  contributorName: {
    color: CoC.text,
    fontSize: 14,
    fontWeight: '500',
  },
  contributorTh: {
    color: CoC.textSecondary,
    fontSize: 10,
    marginTop: 2,
  },
  contributorAmount: {
    color: CoC.amber,
    fontSize: 15,
    fontWeight: '700',
  },
});
