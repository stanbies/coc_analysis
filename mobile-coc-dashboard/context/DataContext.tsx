import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { DashboardData, Player } from '@/types';

interface DataContextType {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  selectedPlayer: Player | null;
  setSelectedPlayer: (player: Player | null) => void;
}

const DataContext = createContext<DataContextType>({
  data: null,
  loading: true,
  error: null,
  selectedPlayer: null,
  setSelectedPlayer: () => {},
});

export function useData() {
  return useContext(DataContext);
}

export function DataProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);

  useEffect(() => {
    try {
      // Load bundled JSON data
      const jsonData = require('@/assets/data/clan_data.json');
      setData(jsonData);
    } catch (err) {
      setError('Could not load clan data. Make sure clan_data.json is in assets/data/.');
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <DataContext.Provider value={{ data, loading, error, selectedPlayer, setSelectedPlayer }}>
      {children}
    </DataContext.Provider>
  );
}
