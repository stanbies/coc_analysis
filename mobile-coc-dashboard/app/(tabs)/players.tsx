import React, { useState, useMemo } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { CoC, getRushColor, getRoleIcon } from '@/constants/theme';
import { useData } from '@/context/DataContext';
import { Player } from '@/types';

type SortField = 'name' | 'townHallLevel' | 'trophies' | 'warStars' | 'donations' | 'rushScore' | 'heroLevels';
type SortDirection = 'asc' | 'desc';

export default function PlayersScreen() {
  const { data, loading, error, setSelectedPlayer } = useData();
  const router = useRouter();
  const [sortField, setSortField] = useState<SortField>('townHallLevel');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [filter, setFilter] = useState('');
  const [rushFilter, setRushFilter] = useState<'all' | 'rushed' | 'notRushed'>('all');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const filteredPlayers = useMemo(() => {
    if (!data) return [];
    return data.players
      .filter(p => {
        const matchesSearch = p.name.toLowerCase().includes(filter.toLowerCase()) ||
          p.tag.toLowerCase().includes(filter.toLowerCase());
        const matchesRush = rushFilter === 'all' ||
          (rushFilter === 'rushed' && p.rushAnalysis.isRushed) ||
          (rushFilter === 'notRushed' && !p.rushAnalysis.isRushed);
        return matchesSearch && matchesRush;
      })
      .sort((a, b) => {
        let aVal: number | string;
        let bVal: number | string;
        switch (sortField) {
          case 'name': aVal = a.name.toLowerCase(); bVal = b.name.toLowerCase(); break;
          case 'townHallLevel': aVal = a.townHallLevel; bVal = b.townHallLevel; break;
          case 'trophies': aVal = a.trophies; bVal = b.trophies; break;
          case 'warStars': aVal = a.warStars; bVal = b.warStars; break;
          case 'donations': aVal = a.donations; bVal = b.donations; break;
          case 'rushScore': aVal = a.rushAnalysis.rushScore; bVal = b.rushAnalysis.rushScore; break;
          case 'heroLevels': aVal = a.heroes.reduce((s, h) => s + h.level, 0); bVal = b.heroes.reduce((s, h) => s + h.level, 0); break;
          default: aVal = 0; bVal = 0;
        }
        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        }
        return sortDirection === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
      });
  }, [data, filter, rushFilter, sortField, sortDirection]);

  const handlePlayerPress = (player: Player) => {
    setSelectedPlayer(player);
    router.push('/modal');
  };

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

  const SortButton = ({ field, label }: { field: SortField; label: string }) => (
    <TouchableOpacity
      style={[styles.sortBtn, sortField === field && styles.sortBtnActive]}
      onPress={() => handleSort(field)}
    >
      <Text style={[styles.sortBtnText, sortField === field && styles.sortBtnTextActive]}>
        {label} {sortField === field ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
      </Text>
    </TouchableOpacity>
  );

  const renderPlayer = ({ item: player, index }: { item: Player; index: number }) => {
    const totalHeroLevels = player.heroes.reduce((sum, h) => sum + h.level, 0);
    const rushColor = getRushColor(player.rushAnalysis.status);

    return (
      <TouchableOpacity
        style={styles.playerRow}
        onPress={() => handlePlayerPress(player)}
        activeOpacity={0.7}
      >
        <Text style={styles.rank}>{index + 1}</Text>
        <View style={styles.playerInfo}>
          <View style={styles.playerNameRow}>
            <Text style={styles.roleIcon}>{getRoleIcon(player.role)}</Text>
            <Text style={styles.playerName} numberOfLines={1}>{player.name}</Text>
          </View>
          <View style={styles.playerStats}>
            <View style={styles.thBadge}>
              <Text style={styles.thText}>{player.townHallLevel}</Text>
            </View>
            <Text style={[styles.statText, { color: CoC.yellow }]}>🏆{player.trophies.toLocaleString()}</Text>
            <Text style={[styles.statText, { color: CoC.purple }]}>⭐{player.warStars}</Text>
            <Text style={[styles.statText, { color: CoC.cyan }]}>🦸{totalHeroLevels}</Text>
          </View>
        </View>
        <View style={styles.playerRight}>
          <Text style={[styles.rushScoreText, { color: CoC.primary }]}>
            {player.rushAnalysis.rushScore.toFixed(1)}
          </Text>
          <View style={[styles.rushBadge, { backgroundColor: rushColor }]}>
            <Text style={styles.rushBadgeText}>
              {player.rushAnalysis.status.replace(/[✅🟢🟡🟠🔴]\s?/g, '').substring(0, 8)}
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <Text style={styles.title}>👥 All Members ({filteredPlayers.length})</Text>
        <TextInput
          style={styles.searchInput}
          placeholder="Search players..."
          placeholderTextColor={CoC.textMuted}
          value={filter}
          onChangeText={setFilter}
        />
        <View style={styles.filterRow}>
          {(['all', 'rushed', 'notRushed'] as const).map(f => (
            <TouchableOpacity
              key={f}
              style={[styles.filterBtn, rushFilter === f && styles.filterBtnActive]}
              onPress={() => setRushFilter(f)}
            >
              <Text style={[styles.filterBtnText, rushFilter === f && styles.filterBtnTextActive]}>
                {f === 'all' ? 'All' : f === 'rushed' ? 'Rushed' : 'Not Rushed'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
        <View style={styles.sortRow}>
          <SortButton field="townHallLevel" label="TH" />
          <SortButton field="trophies" label="Trophies" />
          <SortButton field="warStars" label="Stars" />
          <SortButton field="heroLevels" label="Heroes" />
          <SortButton field="rushScore" label="Rush" />
        </View>
      </View>

      <FlatList
        data={filteredPlayers}
        keyExtractor={item => item.tag}
        renderItem={renderPlayer}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: CoC.background,
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
  header: {
    padding: 16,
    paddingBottom: 8,
  },
  title: {
    color: CoC.text,
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 10,
  },
  searchInput: {
    backgroundColor: CoC.slate800,
    borderWidth: 1,
    borderColor: CoC.slate700,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    color: CoC.text,
    fontSize: 14,
    marginBottom: 10,
  },
  filterRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10,
  },
  filterBtn: {
    backgroundColor: CoC.slate800,
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: CoC.slate700,
  },
  filterBtnActive: {
    backgroundColor: CoC.primary,
    borderColor: CoC.primary,
  },
  filterBtnText: {
    color: CoC.textSecondary,
    fontSize: 12,
    fontWeight: '500',
  },
  filterBtnTextActive: {
    color: '#fff',
  },
  sortRow: {
    flexDirection: 'row',
    gap: 6,
    flexWrap: 'wrap',
  },
  sortBtn: {
    backgroundColor: CoC.slate800,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 6,
  },
  sortBtnActive: {
    backgroundColor: 'rgba(249,115,22,0.2)',
  },
  sortBtnText: {
    color: CoC.textSecondary,
    fontSize: 11,
    fontWeight: '500',
  },
  sortBtnTextActive: {
    color: CoC.primary,
  },
  list: {
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
  playerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: CoC.card,
    borderRadius: 10,
    padding: 12,
    marginBottom: 6,
    borderWidth: 1,
    borderColor: CoC.cardBorder,
  },
  rank: {
    color: CoC.textMuted,
    fontSize: 13,
    width: 22,
    fontWeight: '600',
  },
  playerInfo: {
    flex: 1,
    marginLeft: 4,
  },
  playerNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  roleIcon: {
    fontSize: 14,
  },
  playerName: {
    color: CoC.text,
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
  },
  playerStats: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 4,
  },
  thBadge: {
    backgroundColor: CoC.primary,
    paddingHorizontal: 6,
    paddingVertical: 1,
    borderRadius: 4,
  },
  thText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
  },
  statText: {
    fontSize: 10,
    fontWeight: '600',
  },
  playerRight: {
    alignItems: 'flex-end',
    marginLeft: 8,
  },
  rushScoreText: {
    fontSize: 13,
    fontWeight: '700',
  },
  rushBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginTop: 4,
  },
  rushBadgeText: {
    color: '#fff',
    fontSize: 9,
    fontWeight: '600',
  },
});
