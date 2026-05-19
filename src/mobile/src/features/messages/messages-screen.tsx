import { Stack } from 'expo-router';

import * as React from 'react';

import { FocusAwareStatusBar, Text, View } from '@/components/ui';

export function MessagesScreen() {
  return (
    <View className="flex-1">
      <Stack.Screen options={{ title: 'Messages', headerBackTitle: 'Home' }} />
      <FocusAwareStatusBar />
      <View className="flex-1 items-center justify-center">
        <Text className="text-neutral-400">No messages yet</Text>
      </View>
    </View>
  );
}
