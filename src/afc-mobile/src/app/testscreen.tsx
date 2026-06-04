import { useColorScheme } from 'nativewind';
import { Pressable, Text, View } from 'react-native';

export default function SomeScreen() {
  const { colorScheme, setColorScheme } = useColorScheme();

  return (
    <Pressable onPress={() => setColorScheme(colorScheme === 'dark' ? 'light' : 'dark')}>
      <Text>Current: {colorScheme} - tap to toggle</Text>
      <View className='bg-background'>
        <Text className='text-foreground'>Some content here...</Text>
    </View>
    </Pressable>

  );
}