import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { CoC } from '@/constants/theme';
import { Statistics } from '@/types';

interface RushAnalysisChartProps {
  statistics: Statistics;
}

const rushColors: Record<string, string> = {
  'Maxed': '#22c55e',
  'Slightly Behind': '#84cc16',
  'Moderately Rushed': '#eab308',
  'Rushed': '#f97316',
  'Severely Rushed': '#ef4444',
  'Other': '#64748b',
};

const sortOrder = ['Maxed', 'Slightly Behind', 'Moderately Rushed', 'Rushed', 'Severely Rushed', 'Other'];

export default function RushAnalysisChart({ statistics }: RushAnalysisChartProps) {
  const rushData = statistics.rushDistribution;
  const total = Object.values(rushData).reduce((sum, val) => sum + val, 0);

  const sortedEntries = Object.entries(rushData).sort((a, b) => {
    return sortOrder.indexOf(a[0]) - sortOrder.indexOf(b[0]);
  });

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔍 Rush Analysis Distribution</Text>

      <View style={styles.summaryRow}>
        <View style={styles.summaryItem}>
          <Text style={[styles.summaryValue, { color: CoC.primary }]}>{statistics.rushedCount}</Text>
          <Text style={styles.summaryLabel}>Rushed Players</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={[styles.summaryValue, { color: CoC.cyan }]}>{statistics.averageRushScore.toFixed(1)}</Text>
          <Text style={styles.summaryLabel}>Avg Rush Score</Text>
        </View>
      </View>

      {/* Stacked bar */}
      <View style={styles.stackedBar}>
        {sortedEntries.map(([status, count]) => {
          const percentage = (count / total) * 100;
          if (percentage === 0) return null;
          return (
            <View
              key={status}
              style={[
                styles.barSegment,
                {
                  flex: percentage,
                  backgroundColor: rushColors[status] || '#64748b',
                },
              ]}
            />
          );
        })}
      </View>

      {/* Legend */}
      <View style={styles.legend}>
        {sortedEntries.map(([status, count]) => {
          const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : '0';
          return (
            <View key={status} style={styles.legendItem}>
              <View style={[styles.legendDot, { backgroundColor: rushColors[status] || '#64748b' }]} />
              <Text style={styles.legendText}>
                {status}: <Text style={styles.legendCount}>{count}</Text>
                <Text style={styles.legendPercent}> ({percentage}%)</Text>
              </Text>
            </View>
          );
        })}
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
  summaryRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 16,
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: 24,
    fontWeight: '700',
  },
  summaryLabel: {
    color: CoC.textSecondary,
    fontSize: 10,
    marginTop: 2,
  },
  stackedBar: {
    flexDirection: 'row',
    height: 28,
    borderRadius: 14,
    overflow: 'hidden',
    marginBottom: 14,
  },
  barSegment: {
    height: '100%',
  },
  legend: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    width: '45%',
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  legendText: {
    color: CoC.textSecondary,
    fontSize: 11,
  },
  legendCount: {
    color: CoC.text,
    fontWeight: '600',
  },
  legendPercent: {
    color: CoC.textMuted,
  },
});
