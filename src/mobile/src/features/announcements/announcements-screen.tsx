import { Stack } from 'expo-router';

import * as React from 'react';
import { FocusAwareStatusBar, Text, View } from '@/components/ui';

type Announcement = {
  id: string;
  sender: string;
  recipients: string;
  message: string;
  created_on: string;
  updated_on: string | null;
};

function _AnnouncementItem({ announcement }: { announcement: Announcement }) {
  return (
    <View className="border-b border-neutral-200 px-4 py-3 dark:border-neutral-700">
      <Text className="font-semibold">{announcement.sender}</Text>
      <Text className="mt-1 text-neutral-600">{announcement.message}</Text>
      <Text className="mt-1 text-xs text-neutral-400">
        {new Date(announcement.created_on).toLocaleDateString()}
      </Text>
    </View>
  );
}

export function AnnouncementsScreen() {
  return (
    <View className="flex-1">
      <Stack.Screen options={{ title: 'Announcements', headerBackTitle: 'Home' }} />
      <FocusAwareStatusBar />
      <View className="flex-1 items-center justify-center">
        <Text className="text-neutral-400">No announcements yet</Text>
      </View>
    </View>
  );
}
