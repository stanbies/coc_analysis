import { DarkTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';

import { DataProvider } from '@/context/DataContext';
import { CoC } from '@/constants/theme';

const CoCDarkTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: CoC.primary,
    background: CoC.background,
    card: CoC.slate900,
    text: CoC.text,
    border: CoC.slate700,
    notification: CoC.primary,
  },
};

export const unstable_settings = {
  anchor: '(tabs)',
};

export default function RootLayout() {
  return (
    <DataProvider>
      <ThemeProvider value={CoCDarkTheme}>
        <Stack>
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen
            name="modal"
            options={{
              presentation: 'modal',
              title: 'Player Details',
              headerStyle: { backgroundColor: CoC.primary },
              headerTintColor: '#fff',
              headerTitleStyle: { fontWeight: '700' },
            }}
          />
        </Stack>
        <StatusBar style="light" />
      </ThemeProvider>
    </DataProvider>
  );
}
