import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { CoC, getRushColor, getRoleIcon } from '@/constants/theme';
import { Player } from '@/types';

interface PlayerCardProps {
  player: Player;
  onPress?: () => void;
}

export default function PlayerCard({ player, onPress }: PlayerCardProps) {
  const rushColor = getRushColor(player.rushAnalysis.status);
  const totalHeroLevels = player.heroes.reduce((sum, h) => sum + h.level, 0);

  return (
    <TouchableOpacity style={styles.container} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.header}>
        <View style={styles.nameRow}>
          <Text style={styles.roleIcon}>{getRoleIcon(player.role)}</Text>
          <View>
            <Text style={styles.name}>{player.name}</Text>
            <Text style={styles.tag}>{player.tag}</Text>
          </View>
        </View>
        <View style={styles.thBadge}>
          <Text style={styles.thText}>TH{player.townHallLevel}</Text>
        </View>
      </View>

      <View style={styles.statsRow}>
        <View style={styles.miniStat}>
          <Text style={[styles.miniStatValue, { color: CoC.yellow }]}>🏆 {player.trophies.toLocaleString()}</Text>
          <Text style={styles.miniStatLabel}>Trophies</Text>
        </View>
        <View style={styles.miniStat}>
          <Text style={[styles.miniStatValue, { color: CoC.purple }]}>⭐ {player.warStars.toLocaleString()}</Text>
          <Text style={styles.miniStatLabel}>War Stars</Text>
        </View>
        <View style={styles.miniStat}>
          <Text style={[styles.miniStatValue, { color: CoC.cyan }]}>🦸 {totalHeroLevels}</Text>
          <Text style={styles.miniStatLabel}>Hero Lvls</Text>
        </View>
      </View>

      <View style={styles.footer}>
        <View style={styles.donationsRow}>
          <Text style={[styles.donationText, { color: CoC.green }]}>↑{player.donations}</Text>
          <Text style={styles.donationSep}>/</Text>
          <Text style={[styles.donationText, { color: CoC.red }]}>↓{player.donationsReceived}</Text>
        </View>
        <View style={[styles.rushBadge, { backgroundColor: rushColor }]}>
          <Text style={styles.rushText}>
            {player.rushAnalysis.status.replace(/[✅🟢🟡🟠🔴]\s?/g, '')}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: CoC.card,
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: CoC.cardBorder,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  roleIcon: {
    fontSize: 18,
  },
  name: {
    color: CoC.text,
    fontSize: 15,
    fontWeight: '600',
  },
  tag: {
    color: CoC.textSecondary,
    fontSize: 10,
  },
  thBadge: {
    backgroundColor: CoC.primary,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  thText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '700',
  },
  statsRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10,
  },
  miniStat: {
    flex: 1,
    backgroundColor: 'rgba(30,41,59,0.5)',
    borderRadius: 8,
    padding: 8,
    alignItems: 'center',
  },
  miniStatValue: {
    fontSize: 13,
    fontWeight: '700',
  },
  miniStatLabel: {
    color: CoC.textSecondary,
    fontSize: 9,
    marginTop: 2,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  donationsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  donationText: {
    fontSize: 12,
    fontWeight: '500',
  },
  donationSep: {
    color: CoC.textMuted,
    fontSize: 12,
  },
  rushBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
  },
  rushText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
  },
});
