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
import { useIntegrations } from './api';

function IntegrationItem({ integration }: { integration: { name: string; type: string; is_active: boolean; last_synced_at: string | null } }) {
  return (
    <View className="border-b border-neutral-200 px-4 py-3 dark:border-neutral-700">
      <Text className="font-semibold">{integration.name}</Text>
      <Text className="mt-1 text-neutral-600">{integration.type}</Text>
      <Text className="mt-1 text-xs text-neutral-400">
        {integration.is_active ? 'Connected' : 'Inactive'}
        {integration.last_synced_at && ` - Synced ${new Date(integration.last_synced_at).toLocaleDateString()}`}
      </Text>
    </View>
  );
}

export function IntegrationsScreen() {
  const { data, isPending, isError } = useIntegrations();

  if (isPending) {
    return (
      <View className="flex-1 justify-center">
        <Stack.Screen options={{ title: 'Integrations', headerBackTitle: 'Home' }} />
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (isError) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        <Stack.Screen options={{ title: 'Integrations', headerBackTitle: 'Home' }} />
        <Text className="text-center text-red-500">Failed to load integrations</Text>
        <View className="mt-4">
          <Button
            label="Retry"
            onPress={() => {}}
          />
        </View>
      </View>
    );
  }

  return (
    <View className="flex-1">
      <Stack.Screen options={{ title: 'Integrations', headerBackTitle: 'Home' }} />
      <FocusAwareStatusBar />
      {data && data.length > 0
        ? (
            <FlashList
              data={data}
              renderItem={({ item }) => <IntegrationItem integration={item} />}
              keyExtractor={item => item.id}
            />
          )
        : (
            <View className="flex-1 items-center justify-center">
              <EmptyList />
              <Text className="mt-2 text-neutral-400">No integrations configured</Text>
            </View>
          )}
    </View>
  );
}
