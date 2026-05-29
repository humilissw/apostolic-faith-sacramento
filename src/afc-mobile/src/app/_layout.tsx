import { DarkTheme, DefaultTheme, ThemeProvider } from 'expo-router';
import { withLayoutContext } from 'expo-router';
import { useColorScheme } from 'react-native';

import { AnimatedSplashOverlay } from '@/components/animated-icon';

import "../../global.css"

const DrawerNavigator = (
  require('expo-router/build/react-navigation/drawer').createDrawerNavigator()
).Navigator;

const ExpoRouterDrawer = withLayoutContext(DrawerNavigator);

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? DarkTheme : DefaultTheme;

  return (
    <ThemeProvider value={theme}>
      <AnimatedSplashOverlay />
      <ExpoRouterDrawer
        initialRouteName="index"
        drawerType="front"
        screenOptions={{
          headerSize: {
            home: 44,
            explore: 44,
            sermons: 44,
            doctrines: 44,
            media: 44,
            'live-service': 44,
            donate: 44,
            contact: 44,
          },
          labels: {
            home: 'Home',
            explore: 'Explore',
            sermons: 'Sermons',
            doctrines: 'Our Beliefs',
            media: 'Media',
            'live-service': 'Live Service',
            donate: 'Donate',
            contact: 'Contact',
          },
          icons: {
            home: require('@/assets/images/tabIcons/home.png'),
            explore: require('@/assets/images/tabIcons/explore.png'),
            sermons: require('@/assets/images/tabIcons/explore.png'),
            doctrines: require('@/assets/images/tabIcons/explore.png'),
            media: require('@/assets/images/tabIcons/explore.png'),
            'live-service': require('@/assets/images/tabIcons/explore.png'),
            donate: require('@/assets/images/tabIcons/explore.png'),
            contact: require('@/assets/images/tabIcons/explore.png'),
          },
        }}
      >
        <ExpoRouterDrawer.Screen name="index" />
        <ExpoRouterDrawer.Screen name="explore" />
        <ExpoRouterDrawer.Screen name="sermons" />
        <ExpoRouterDrawer.Screen name="doctrines" />
        <ExpoRouterDrawer.Screen name="media" />
        <ExpoRouterDrawer.Screen name="live-service" />
        <ExpoRouterDrawer.Screen name="donate" />
        <ExpoRouterDrawer.Screen name="contact" />
      </ExpoRouterDrawer>
    </ThemeProvider>
  );
}
