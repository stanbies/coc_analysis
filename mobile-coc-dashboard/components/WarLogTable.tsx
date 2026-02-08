import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { CoC } from '@/constants/theme';
import { WarLogEntry } from '@/types';

interface WarLogTableProps {
  warLog: WarLogEntry[];
}

function getResultIcon(result: string): string {
  switch (result) {
    case 'win': return '✅';
    case 'lose': return '❌';
    case 'tie': return '➖';
    default: return '❓';
  }
}

function getResultColor(result: string): string {
  switch (result) {
    case 'win': return CoC.green;
    case 'lose': return CoC.red;
    case 'tie': return CoC.yellow;
    default: return CoC.textSecondary;
  }
}

export default function WarLogTable({ warLog }: WarLogTableProps) {
  if (!warLog || warLog.length === 0) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>📜 War Log</Text>
        <Text style={styles.emptyText}>No war log data available or war log is private.</Text>
      </View>
    );
  }

  const wins = warLog.filter(w => w.result === 'win').length;
  const losses = warLog.filter(w => w.result === 'lose').length;
  const ties = warLog.filter(w => w.result === 'tie').length;

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>📜 War Log</Text>
        <View style={styles.summaryRow}>
          <Text style={[styles.summaryText, { color: CoC.green }]}>✅ {wins}W</Text>
          <Text style={[styles.summaryText, { color: CoC.red }]}>❌ {losses}L</Text>
          <Text style={[styles.summaryText, { color: CoC.yellow }]}>➖ {ties}T</Text>
        </View>
      </View>

      {warLog.slice(0, 20).map((war, i) => (
        <View key={i} style={styles.warRow}>
          <View style={styles.resultCol}>
            <Text style={[styles.resultText, { color: getResultColor(war.result) }]}>
              {getResultIcon(war.result)} {war.result?.toUpperCase()}
            </Text>
          </View>
          <View style={styles.opponentCol}>
            <Text style={styles.opponentName} numberOfLines={1}>{war.opponent.name}</Text>
            <Text style={styles.sizeText}>{war.teamSize}v{war.teamSize}</Text>
          </View>
          <View style={styles.scoreCol}>
            <Text style={styles.starsText}>
              <Text style={{ color: CoC.yellow }}>{war.clan.stars}</Text>
              <Text style={{ color: CoC.textMuted }}> - </Text>
              <Text style={{ color: CoC.textSecondary }}>{war.opponent.stars}</Text>
            </Text>
            <Text style={styles.destructionText}>
              <Text style={{ color: CoC.cyan }}>{war.clan.destructionPercentage?.toFixed(1)}%</Text>
              <Text style={{ color: CoC.textMuted }}> - </Text>
              <Text style={{ color: CoC.textSecondary }}>{war.opponent.destructionPercentage?.toFixed(1)}%</Text>
            </Text>
          </View>
        </View>
      ))}
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
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    color: CoC.text,
    fontSize: 18,
    fontWeight: '700',
  },
  summaryRow: {
    flexDirection: 'row',
    gap: 10,
  },
  summaryText: {
    fontSize: 12,
    fontWeight: '600',
  },
  emptyText: {
    color: CoC.textSecondary,
    fontSize: 14,
    marginTop: 8,
  },
  warRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: CoC.slate800,
  },
  resultCol: {
    width: 70,
  },
  resultText: {
    fontSize: 11,
    fontWeight: '600',
  },
  opponentCol: {
    flex: 1,
    paddingHorizontal: 8,
  },
  opponentName: {
    color: CoC.text,
    fontSize: 13,
    fontWeight: '500',
  },
  sizeText: {
    color: CoC.textSecondary,
    fontSize: 10,
    marginTop: 2,
  },
  scoreCol: {
    alignItems: 'flex-end',
  },
  starsText: {
    fontSize: 12,
    fontWeight: '600',
  },
  destructionText: {
    fontSize: 10,
    marginTop: 2,
  },
});
