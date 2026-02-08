import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { CoC } from '@/constants/theme';
import { CapitalRaid } from '@/types';

interface CapitalRaidsCardProps {
  capitalRaids: CapitalRaid[];
}

export default function CapitalRaidsCard({ capitalRaids }: CapitalRaidsCardProps) {
  if (!capitalRaids || capitalRaids.length === 0) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>🏛️ Capital Raids</Text>
        <Text style={styles.emptyText}>No capital raid data available.</Text>
      </View>
    );
  }

  const latestRaid = capitalRaids[0];
  const topRaiders = [...(latestRaid.members || [])]
    .sort((a, b) => b.capitalResourcesLooted - a.capitalResourcesLooted)
    .slice(0, 10);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🏛️ Capital Raids</Text>

      <View style={styles.statsGrid}>
        <View style={styles.statBox}>
          <Text style={[styles.statValue, { color: CoC.amber }]}>
            {latestRaid.capitalTotalLoot?.toLocaleString() || 0}
          </Text>
          <Text style={styles.statLabel}>Total Loot</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={[styles.statValue, { color: CoC.green }]}>
            {latestRaid.raidsCompleted || 0}
          </Text>
          <Text style={styles.statLabel}>Raids Done</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={[styles.statValue, { color: CoC.cyan }]}>
            {latestRaid.totalAttacks || 0}
          </Text>
          <Text style={styles.statLabel}>Attacks</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={[styles.statValue, { color: CoC.purple }]}>
            {latestRaid.enemyDistrictsDestroyed || 0}
          </Text>
          <Text style={styles.statLabel}>Districts</Text>
        </View>
      </View>

      {topRaiders.length > 0 && (
        <View style={styles.raidersSection}>
          <Text style={styles.raidersTitle}>Top Raiders (Latest Weekend)</Text>
          {topRaiders.map((member, i) => (
            <View key={member.tag} style={styles.raiderRow}>
              <View style={styles.raiderLeft}>
                <View style={[
                  styles.rankBadge,
                  i === 0 ? styles.rank1 : i === 1 ? styles.rank2 : i === 2 ? styles.rank3 : styles.rankDefault,
                ]}>
                  <Text style={[
                    styles.rankText,
                    (i === 0 || i === 1) ? { color: '#000' } : { color: '#fff' },
                  ]}>{i + 1}</Text>
                </View>
                <Text style={styles.raiderName} numberOfLines={1}>{member.name}</Text>
              </View>
              <View style={styles.raiderRight}>
                <Text style={styles.attacksText}>
                  {member.attacks}/{member.attackLimit + member.bonusAttackLimit}
                </Text>
                <Text style={styles.lootText}>
                  {member.capitalResourcesLooted.toLocaleString()}
                </Text>
              </View>
            </View>
          ))}
        </View>
      )}

      <View style={styles.rewardsRow}>
        <View>
          <Text style={styles.rewardLabel}>Offensive Reward</Text>
          <Text style={[styles.rewardValue, { color: CoC.green }]}>{latestRaid.offensiveReward || 0}</Text>
        </View>
        <View style={{ alignItems: 'flex-end' }}>
          <Text style={styles.rewardLabel}>Defensive Reward</Text>
          <Text style={[styles.rewardValue, { color: CoC.blue }]}>{latestRaid.defensiveReward || 0}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: CoC.card,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: CoC.cardBorder,
  },
  title: {
    color: CoC.text,
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 14,
  },
  emptyText: {
    color: CoC.textSecondary,
    fontSize: 14,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  statBox: {
    flex: 1,
    backgroundColor: CoC.slate800,
    borderRadius: 10,
    padding: 10,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '700',
  },
  statLabel: {
    color: CoC.textSecondary,
    fontSize: 9,
    marginTop: 2,
  },
  raidersSection: {
    marginBottom: 12,
  },
  raidersTitle: {
    color: CoC.textSecondary,
    fontSize: 12,
    fontWeight: '500',
    marginBottom: 8,
  },
  raiderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'rgba(30,41,59,0.5)',
    borderRadius: 8,
    padding: 8,
    marginBottom: 4,
  },
  raiderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flex: 1,
  },
  rankBadge: {
    width: 22,
    height: 22,
    borderRadius: 11,
    justifyContent: 'center',
    alignItems: 'center',
  },
  rank1: { backgroundColor: '#eab308' },
  rank2: { backgroundColor: '#94a3b8' },
  rank3: { backgroundColor: '#d97706' },
  rankDefault: { backgroundColor: CoC.slate700 },
  rankText: {
    fontSize: 10,
    fontWeight: '700',
  },
  raiderName: {
    color: CoC.text,
    fontSize: 13,
    flex: 1,
  },
  raiderRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  attacksText: {
    color: CoC.textSecondary,
    fontSize: 10,
  },
  lootText: {
    color: CoC.amber,
    fontSize: 13,
    fontWeight: '600',
  },
  rewardsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: CoC.slate700,
  },
  rewardLabel: {
    color: CoC.textSecondary,
    fontSize: 11,
  },
  rewardValue: {
    fontSize: 14,
    fontWeight: '600',
  },
});
