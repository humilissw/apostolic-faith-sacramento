import { FlashList } from '@shopify/flash-list';

import { Stack } from 'expo-router';

import * as React from 'react';
import {
  ActivityIndicator,
  Button,
  EmptyList,
  FocusAwareStatusBar,
  Text,
  View,
} from '@/components/ui';
import { useMyCalendar } from './api';

function AssignmentItem({ assignment }: { assignment: { event_date: string; type: string; role: string; notes: string | null } }) {
  return (
    <View className="border-b border-neutral-200 px-4 py-3 dark:border-neutral-700">
      <Text className="font-semibold">{assignment.event_date}</Text>
      <Text className="mt-1 text-neutral-600">
        {assignment.type}
        {' '}
        -
        {' '}
        {assignment.role}
      </Text>
      {assignment.notes && (
        <Text className="mt-1 text-xs text-neutral-400 italic">{assignment.notes}</Text>
      )}
    </View>
  );
}

export function ScheduleScreen() {
  const today = new Date();
  const endDate = new Date(today);
  endDate.setDate(today.getDate() + 7);

  const { data, isPending } = useMyCalendar({
    variables: {
      startDate: today.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0],
    },
  });

  if (isPending) {
    return (
      <View className="flex-1 justify-center">
        <Stack.Screen options={{ title: 'Schedule', headerBackTitle: 'Home' }} />
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View className="flex-1">
      <Stack.Screen options={{ title: 'Schedule', headerBackTitle: 'Home' }} />
      <FocusAwareStatusBar />
      <View className="px-4 pt-2">
        <Text className="mb-2 text-sm text-neutral-500">Next 7 days</Text>
      </View>
      {data && data.length > 0
        ? (
            <FlashList
              data={data}
              renderItem={({ item }) => <AssignmentItem assignment={item} />}
              keyExtractor={item => item.id}
            />
          )
        : (
            <View className="flex-1 items-center justify-center">
              <EmptyList />
              <Text className="mt-2 text-neutral-400">No assignments this week</Text>
              <View className="mt-4">
                <Button
                  label="Request Time Off"
                  onPress={() => {}}
                />
              </View>
            </View>
          )}
    </View>
  );
}
