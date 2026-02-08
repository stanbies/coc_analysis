import { Tabs } from 'expo-router';
import React from 'react';
import { Text } from 'react-native';

import { HapticTab } from '@/components/haptic-tab';
import { CoC } from '@/constants/theme';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: CoC.primary,
        tabBarInactiveTintColor: CoC.textMuted,
        tabBarStyle: {
          backgroundColor: CoC.slate900,
          borderTopColor: CoC.slate700,
          borderTopWidth: 1,
        },
        headerShown: false,
        tabBarButton: HapticTab,
      }}>
      <Tabs.Screen
        name="overview"
        options={{
          title: 'Overview',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>📊</Text>,
        }}
      />
      <Tabs.Screen
        name="players"
        options={{
          title: 'Players',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>👥</Text>,
        }}
      />
      <Tabs.Screen
        name="wars"
        options={{
          title: 'Wars',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>⚔️</Text>,
        }}
      />
      <Tabs.Screen
        name="capital"
        options={{
          title: 'Capital',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>🏛️</Text>,
        }}
      />
      {/* Hide old boilerplate tabs */}
      <Tabs.Screen name="index" options={{ href: null }} />
      <Tabs.Screen name="explore" options={{ href: null }} />
    </Tabs>
  );
}
