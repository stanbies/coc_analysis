import React from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { CoC } from '@/constants/theme';
import { useData } from '@/context/DataContext';
import StatCard from '@/components/StatCard';
import WarLogTable from '@/components/WarLogTable';

export default function WarsScreen() {
  const { data, loading, error } = useData();

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

  const { clan, warLog } = data;
  const totalWars = clan.warWins + clan.warTies + clan.warLosses;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <View style={styles.statsGrid}>
        <View style={styles.statHalf}>
          <StatCard title="Total Wars" value={totalWars} icon="⚔️" />
        </View>
        <View style={styles.statHalf}>
          <StatCard title="Wins" value={clan.warWins} icon="✅" />
        </View>
        <View style={styles.statHalf}>
          <StatCard title="Losses" value={clan.warLosses} icon="❌" />
        </View>
        <View style={styles.statHalf}>
          <StatCard title="Win Streak" value={clan.warWinStreak} icon="🔥" />
        </View>
      </View>

      <WarLogTable warLog={warLog} />
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
});
