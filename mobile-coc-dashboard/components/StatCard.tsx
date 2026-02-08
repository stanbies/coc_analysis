import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { CoC } from '@/constants/theme';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  subtitle?: string;
}

export default function StatCard({ title, value, icon, subtitle }: StatCardProps) {
  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <View style={styles.textContainer}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.value}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </Text>
          {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
        </View>
        <Text style={styles.icon}>{icon}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: CoC.statCard,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: CoC.statCardBorder,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  textContainer: {
    flex: 1,
  },
  title: {
    color: CoC.textSecondary,
    fontSize: 12,
    fontWeight: '500',
  },
  value: {
    color: CoC.text,
    fontSize: 22,
    fontWeight: '700',
    marginTop: 4,
  },
  subtitle: {
    color: CoC.textMuted,
    fontSize: 10,
    marginTop: 2,
  },
  icon: {
    fontSize: 28,
  },
});
