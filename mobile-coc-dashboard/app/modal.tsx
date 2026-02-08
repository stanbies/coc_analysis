import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { CoC, getRushColor, getRoleLabel } from '@/constants/theme';
import { useData } from '@/context/DataContext';

export default function PlayerModalScreen() {
  const { selectedPlayer: player } = useData();
  const router = useRouter();

  if (!player) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyText}>No player selected</Text>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backBtnText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const rushColor = getRushColor(player.rushAnalysis.status);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.playerName}>{player.name}</Text>
          <Text style={styles.playerTag}>{player.tag}</Text>
          <Text style={styles.playerRole}>{getRoleLabel(player.role)}</Text>
        </View>
        <View style={styles.headerRight}>
          <View style={styles.thBadgeLarge}>
            <Text style={styles.thBadgeText}>TH{player.townHallLevel}</Text>
          </View>
          <Text style={styles.levelText}>Level {player.expLevel}</Text>
        </View>
      </View>

      {/* Stats Grid */}
      <View style={styles.statsGrid}>
        <View style={styles.statBox}>
          <Text style={[styles.statValue, { color: CoC.yellow }]}>🏆 {player.trophies.toLocaleString()}</Text>
          <Text style={styles.statLabel}>Current Trophies</Text>
          <Text style={styles.statSub}>Best: {player.bestTrophies.toLocaleString()}</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={[styles.statValue, { color: CoC.purple }]}>⭐ {player.warStars.toLocaleString()}</Text>
          <Text style={styles.statLabel}>War Stars</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={[styles.statValue, { color: CoC.green }]}>⚔️ {player.attackWins.toLocaleString()}</Text>
          <Text style={styles.statLabel}>Attack Wins</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={[styles.statValue, { color: CoC.blue }]}>🛡️ {player.defenseWins.toLocaleString()}</Text>
          <Text style={styles.statLabel}>Defense Wins</Text>
        </View>
      </View>

      {/* Donations */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📦 Donations</Text>
        <View style={styles.donationRow}>
          <Text style={[styles.donationText, { color: CoC.green }]}>Donated: {player.donations.toLocaleString()}</Text>
          <Text style={[styles.donationText, { color: CoC.red }]}>Received: {player.donationsReceived.toLocaleString()}</Text>
        </View>
        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              {
                width: `${Math.min(100, (player.donations / Math.max(1, player.donations + player.donationsReceived)) * 100)}%`,
              },
            ]}
          />
        </View>
        <Text style={styles.ratioText}>
          Ratio: {player.donationsReceived > 0 ? (player.donations / player.donationsReceived).toFixed(2) : player.donations}
        </Text>
      </View>

      {/* Rush Analysis */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>🔍 Rush Analysis</Text>
          <View style={[styles.rushBadge, { backgroundColor: rushColor }]}>
            <Text style={styles.rushBadgeText}>
              {player.rushAnalysis.status.replace(/[✅🟢🟡🟠🔴]\s?/g, '')}
            </Text>
          </View>
        </View>

        <View style={styles.rushStatsRow}>
          <View style={styles.rushStatItem}>
            <Text style={[styles.rushStatValue, { color: CoC.primary }]}>{player.rushAnalysis.rushScore.toFixed(1)}</Text>
            <Text style={styles.rushStatLabel}>Rush Score</Text>
          </View>
          <View style={styles.rushStatItem}>
            <Text style={[styles.rushStatValue, { color: CoC.red }]}>-{player.rushAnalysis.totalMissingHeroLevels}</Text>
            <Text style={styles.rushStatLabel}>Missing Hero Lvls</Text>
          </View>
          <View style={styles.rushStatItem}>
            <Text style={[styles.rushStatValue, { color: CoC.yellow }]}>{player.rushAnalysis.rushPercentage.toFixed(1)}%</Text>
            <Text style={styles.rushStatLabel}>Behind Target</Text>
          </View>
        </View>

        {player.rushAnalysis.rushedHeroes.length > 0 && (
          <View style={styles.rushedHeroesContainer}>
            <Text style={styles.rushedHeroesLabel}>Rushed Heroes:</Text>
            <View style={styles.rushedHeroesList}>
              {player.rushAnalysis.rushedHeroes.map((hero, i) => (
                <View key={i} style={styles.rushedHeroPill}>
                  <Text style={styles.rushedHeroText}>
                    {hero.name}: {hero.current}/{hero.target} (-{hero.missing})
                  </Text>
                </View>
              ))}
            </View>
          </View>
        )}
      </View>

      {/* Heroes */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🦸 Heroes</Text>
        <View style={styles.heroesGrid}>
          {player.heroes.map((hero, i) => (
            <View key={i} style={styles.heroCard}>
              <Text style={styles.heroName} numberOfLines={1}>{hero.name}</Text>
              <View style={styles.heroLevelRow}>
                <Text style={[styles.heroLevel, { color: CoC.cyan }]}>{hero.level}</Text>
                <Text style={styles.heroMaxLevel}>/ {hero.maxLevel}</Text>
              </View>
              <View style={styles.progressBarSmall}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${(hero.level / hero.maxLevel) * 100}%` },
                  ]}
                />
              </View>
            </View>
          ))}
        </View>
      </View>

      {/* War Performance */}
      {player.warStats.totalAttacks > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⚔️ War Performance</Text>
          <View style={styles.warStatsGrid}>
            <View style={styles.warStatItem}>
              <Text style={styles.warStatValue}>{player.warStats.totalAttacks}</Text>
              <Text style={styles.warStatLabel}>Total Attacks</Text>
            </View>
            <View style={styles.warStatItem}>
              <Text style={[styles.warStatValue, { color: CoC.yellow }]}>{player.warStats.totalStars}</Text>
              <Text style={styles.warStatLabel}>Total Stars</Text>
            </View>
            <View style={styles.warStatItem}>
              <Text style={[styles.warStatValue, { color: CoC.green }]}>{player.warStats.threeStars}</Text>
              <Text style={styles.warStatLabel}>3-Stars</Text>
            </View>
            <View style={styles.warStatItem}>
              <Text style={[styles.warStatValue, { color: CoC.cyan }]}>
                {(player.warStats.totalStars / player.warStats.totalAttacks).toFixed(2)}
              </Text>
              <Text style={styles.warStatLabel}>Avg Stars</Text>
            </View>
          </View>
        </View>
      )}

      {/* Capital Contributions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏛️ Clan Capital</Text>
        <Text style={styles.capitalValue}>
          {player.clanCapitalContributions.toLocaleString()}
          <Text style={styles.capitalLabel}>  Gold Contributed</Text>
        </Text>
      </View>

      <View style={{ height: 30 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: CoC.slate900,
  },
  content: {
    paddingBottom: 20,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: CoC.slate900,
  },
  emptyText: {
    color: CoC.textSecondary,
    fontSize: 16,
    marginBottom: 16,
  },
  backBtn: {
    backgroundColor: CoC.primary,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  backBtnText: {
    color: '#fff',
    fontWeight: '600',
  },
  header: {
    backgroundColor: CoC.primary,
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  headerLeft: {
    flex: 1,
  },
  playerName: {
    color: '#fff',
    fontSize: 22,
    fontWeight: '700',
  },
  playerTag: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 13,
    marginTop: 2,
  },
  playerRole: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
    marginTop: 4,
  },
  headerRight: {
    alignItems: 'flex-end',
  },
  thBadgeLarge: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 12,
  },
  thBadgeText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
  },
  levelText: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 11,
    marginTop: 4,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    padding: 16,
  },
  statBox: {
    width: '48%',
    flexGrow: 1,
    backgroundColor: CoC.slate800,
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: '700',
  },
  statLabel: {
    color: CoC.textSecondary,
    fontSize: 10,
    marginTop: 4,
  },
  statSub: {
    color: CoC.textMuted,
    fontSize: 9,
    marginTop: 2,
  },
  section: {
    backgroundColor: CoC.slate800,
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginTop: 12,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    color: CoC.text,
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
  },
  donationRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  donationText: {
    fontSize: 12,
    fontWeight: '500',
  },
  progressBar: {
    height: 10,
    backgroundColor: 'rgba(71,85,105,0.5)',
    borderRadius: 5,
    overflow: 'hidden',
  },
  progressBarSmall: {
    height: 6,
    backgroundColor: 'rgba(71,85,105,0.5)',
    borderRadius: 3,
    overflow: 'hidden',
    marginTop: 6,
  },
  progressFill: {
    height: '100%',
    backgroundColor: CoC.primary,
    borderRadius: 5,
  },
  ratioText: {
    color: CoC.textSecondary,
    fontSize: 10,
    marginTop: 4,
  },
  rushBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
  },
  rushBadgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  rushStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 12,
  },
  rushStatItem: {
    alignItems: 'center',
  },
  rushStatValue: {
    fontSize: 20,
    fontWeight: '700',
  },
  rushStatLabel: {
    color: CoC.textSecondary,
    fontSize: 10,
    marginTop: 2,
  },
  rushedHeroesContainer: {
    marginTop: 8,
  },
  rushedHeroesLabel: {
    color: CoC.textSecondary,
    fontSize: 12,
    marginBottom: 6,
  },
  rushedHeroesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  rushedHeroPill: {
    backgroundColor: 'rgba(239,68,68,0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  rushedHeroText: {
    color: CoC.redLight,
    fontSize: 10,
  },
  heroesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  heroCard: {
    width: '48%',
    flexGrow: 1,
    backgroundColor: 'rgba(51,65,85,0.5)',
    borderRadius: 10,
    padding: 10,
  },
  heroName: {
    color: CoC.text,
    fontSize: 12,
    fontWeight: '500',
  },
  heroLevelRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginTop: 4,
  },
  heroLevel: {
    fontSize: 18,
    fontWeight: '700',
  },
  heroMaxLevel: {
    color: CoC.textSecondary,
    fontSize: 11,
    marginLeft: 4,
  },
  warStatsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  warStatItem: {
    width: '48%',
    flexGrow: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  warStatValue: {
    color: CoC.text,
    fontSize: 18,
    fontWeight: '700',
  },
  warStatLabel: {
    color: CoC.textSecondary,
    fontSize: 10,
    marginTop: 2,
  },
  capitalValue: {
    color: CoC.amber,
    fontSize: 22,
    fontWeight: '700',
  },
  capitalLabel: {
    color: CoC.textSecondary,
    fontSize: 13,
    fontWeight: '400',
  },
});
