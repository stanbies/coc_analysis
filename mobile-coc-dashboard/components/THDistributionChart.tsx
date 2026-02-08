import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { CoC, THColors } from '@/constants/theme';
import { Statistics } from '@/types';

interface THDistributionChartProps {
  statistics: Statistics;
}

export default function THDistributionChart({ statistics }: THDistributionChartProps) {
  const thData = statistics.thDistribution;
  const maxCount = Math.max(...Object.values(thData), 1);

  const sortedEntries = Object.entries(thData)
    .map(([th, count]) => ({ th: parseInt(th), count }))
    .sort((a, b) => b.th - a.th);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🏠 Town Hall Distribution</Text>

      <View style={styles.barsContainer}>
        {sortedEntries.map(({ th, count }) => {
          const percentage = (count / maxCount) * 100;
          const color = THColors[th] || '#64748b';

          return (
            <View key={th} style={styles.barRow}>
              <Text style={styles.thLabel}>TH{th}</Text>
              <View style={styles.barBackground}>
                <View
                  style={[
                    styles.barFill,
                    {
                      width: `${Math.max(percentage, count > 0 ? 10 : 0)}%`,
                      backgroundColor: color,
                    },
                  ]}
                >
                  <Text style={styles.barCount}>{count}</Text>
                </View>
              </View>
            </View>
          );
        })}
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerLabel}>Total Members:</Text>
        <Text style={styles.footerValue}>
          {Object.values(thData).reduce((sum, val) => sum + val, 0)}
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
    borderWidth: 1,
    borderColor: CoC.cardBorder,
  },
  title: {
    color: CoC.text,
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 14,
  },
  barsContainer: {
    gap: 8,
  },
  barRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  thLabel: {
    color: CoC.text,
    fontSize: 12,
    fontWeight: '500',
    width: 36,
    textAlign: 'right',
  },
  barBackground: {
    flex: 1,
    height: 28,
    backgroundColor: CoC.slate800,
    borderRadius: 8,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'flex-end',
    paddingRight: 8,
  },
  barCount: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '700',
  },
  footer: {
    marginTop: 14,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: CoC.slate700,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  footerLabel: {
    color: CoC.textSecondary,
    fontSize: 13,
  },
  footerValue: {
    color: CoC.text,
    fontSize: 13,
    fontWeight: '600',
  },
});
