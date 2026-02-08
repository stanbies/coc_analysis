import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Image } from 'expo-image';
import { CoC } from '@/constants/theme';
import { Clan } from '@/types';

interface ClanHeaderProps {
  clan: Clan;
  lastUpdated: string;
}

export default function ClanHeader({ clan, lastUpdated }: ClanHeaderProps) {
  const totalWars = clan.warWins + clan.warTies + clan.warLosses;
  const winRate = totalWars > 0 ? ((clan.warWins / totalWars) * 100).toFixed(1) : '0';

  return (
    <View style={styles.container}>
      <View style={styles.topRow}>
        {clan.badgeUrls?.large && (
          <Image source={{ uri: clan.badgeUrls.large }} style={styles.badge} />
        )}
        <View style={styles.info}>
          <Text style={styles.name}>{clan.name}</Text>
          <Text style={styles.tag}>{clan.tag}</Text>
          <View style={styles.badges}>
            <View style={[styles.pill, { backgroundColor: 'rgba(249,115,22,0.2)' }]}>
              <Text style={[styles.pillText, { color: CoC.primary }]}>Level {clan.clanLevel}</Text>
            </View>
            {clan.location && (
              <View style={[styles.pill, { backgroundColor: 'rgba(59,130,246,0.2)' }]}>
                <Text style={[styles.pillText, { color: CoC.blue }]}>📍 {clan.location.name}</Text>
              </View>
            )}
          </View>
        </View>
      </View>

      <View style={styles.statsRow}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{clan.members}/50</Text>
          <Text style={styles.statLabel}>Members</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statValue, { color: CoC.yellow }]}>{clan.clanPoints.toLocaleString()}</Text>
          <Text style={styles.statLabel}>Clan Points</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statValue, { color: CoC.green }]}>{clan.warWins}</Text>
          <Text style={styles.statLabel}>War Wins</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statValue, { color: CoC.cyan }]}>{winRate}%</Text>
          <Text style={styles.statLabel}>Win Rate</Text>
        </View>
      </View>

      {clan.description ? (
        <View style={styles.descriptionContainer}>
          <Text style={styles.description}>{clan.description}</Text>
        </View>
      ) : null}

      <View style={styles.footer}>
        <View style={styles.labelsRow}>
          {clan.labels?.map((label, i) => (
            <View key={i} style={styles.labelItem}>
              {label.iconUrls?.small && (
                <Image source={{ uri: label.iconUrls.small }} style={styles.labelIcon} />
              )}
              <Text style={styles.labelText}>{label.name}</Text>
            </View>
          ))}
        </View>
        <Text style={styles.updated}>
          Updated: {new Date(lastUpdated).toLocaleDateString()}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: CoC.card,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: CoC.primary + '40',
    shadowColor: CoC.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 5,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  badge: {
    width: 64,
    height: 64,
    borderRadius: 12,
  },
  info: {
    flex: 1,
  },
  name: {
    color: CoC.text,
    fontSize: 22,
    fontWeight: '700',
  },
  tag: {
    color: CoC.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
  badges: {
    flexDirection: 'row',
    gap: 6,
    marginTop: 6,
    flexWrap: 'wrap',
  },
  pill: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  pillText: {
    fontSize: 11,
    fontWeight: '500',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: CoC.slate700,
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    color: CoC.text,
    fontSize: 18,
    fontWeight: '700',
  },
  statLabel: {
    color: CoC.textSecondary,
    fontSize: 10,
    marginTop: 2,
  },
  descriptionContainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: CoC.slate700,
  },
  description: {
    color: CoC.textSecondary,
    fontSize: 13,
    lineHeight: 18,
  },
  footer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: CoC.slate700,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  labelsRow: {
    flexDirection: 'row',
    gap: 8,
    flex: 1,
    flexWrap: 'wrap',
  },
  labelItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  labelIcon: {
    width: 16,
    height: 16,
  },
  labelText: {
    color: CoC.textSecondary,
    fontSize: 10,
  },
  updated: {
    color: CoC.textMuted,
    fontSize: 10,
  },
});
