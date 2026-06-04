import { DarkTheme, DefaultTheme, ThemeProvider } from 'expo-router';
import { withLayoutContext } from 'expo-router';
import { useColorScheme } from 'react-native';
import { AnimatedSplashOverlay } from '@/components/animated-icon';
import "../../global.css"
import { Colors } from '@/constants/theme';


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
          headerTitleAlign: "left",
          headerTitleStyle: {
            fontSize: 24,
            fontWeight: "bold",
          },
          headerStyle: {
            height: 110,
            backgroundColor: "#e8d187"
          },
          headerSize: {
            home: 44,
            //explore: 44,
            sermons: 44,
            doctrines: 44,
            media: 44,
            'live-service': 44,
            donate: 44,
            contact: 44,
          },
          labels: {
            home: 'Home',
            //explore: 'Explore',
            sermons: 'Sermons',
            doctrines: 'Our Beliefs',
            media: 'Media',
            'live-service': 'Live Service',
            donate: 'Donate',
            contact: 'Contact',
          },
          icons: {
            home: require('@/assets/images/tabIcons/home.png'),
            //explore: require('@/assets/images/tabIcons/explore.png'),
            sermons: require('@/assets/images/tabIcons/explore.png'),
            doctrines: require('@/assets/images/tabIcons/explore.png'),
            media: require('@/assets/images/tabIcons/explore.png'),
            'live-service': require('@/assets/images/tabIcons/explore.png'),
            donate: require('@/assets/images/tabIcons/explore.png'),
            contact: require('@/assets/images/tabIcons/explore.png'),
          },
        }}
      >
        <ExpoRouterDrawer.Screen name="index" options={{ 
          title: "Home", 
          headerTitleAlign: "left",
          headerTitleStyle: {
            fontSize: 24,
            fontWeight: "bold",
          },
          headerStyle: {
            height: 110,
          }
          }}/>
        {/* <ExpoRouterDrawer.Screen name="explore" options={{ title: "Explore" }}/> */}
        <ExpoRouterDrawer.Screen name="sermons" options={{ title: "Sermons" }}/>
        <ExpoRouterDrawer.Screen name="doctrines" options={{ title: "Our Beliefs" }}/>
        <ExpoRouterDrawer.Screen name="media" options={{ title: "Media" }}/>
        <ExpoRouterDrawer.Screen name="live-service" options={{ title: "Live Service" }}/>
        <ExpoRouterDrawer.Screen name="donate" options={{ title: "Donate" }}/>
        <ExpoRouterDrawer.Screen name="contact" options={{ title: "Contact" }}/>
      </ExpoRouterDrawer>
    </ThemeProvider>
  );
}
