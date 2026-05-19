import { Stack } from 'expo-router';

import * as React from 'react';

import {
  ActivityIndicator,
  Button,
  FocusAwareStatusBar,
  ScrollView,
  Text,
  View,
} from '@/components/ui';
import { signOut } from '@/features/auth/use-auth-store';
import { useUserProfile } from './api';

export function ProfileScreen() {
  const { data, isPending, isError } = useUserProfile();

  if (isPending) {
    return (
      <View className="flex-1 justify-center">
        <Stack.Screen options={{ title: 'Profile', headerBackTitle: 'Home' }} />
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (isError) {
    return (
      <View className="flex-1 justify-center p-4">
        <Stack.Screen options={{ title: 'Profile', headerBackTitle: 'Home' }} />
        <Text className="text-center text-red-500">Failed to load profile</Text>
        <View className="mt-4">
          <Button
            label="Back to Home"
            onPress={() => signOut()}
          />
        </View>
      </View>
    );
  }

  return (
    <ScrollView className="flex-1">
      <Stack.Screen options={{ title: 'Profile', headerBackTitle: 'Home' }} />
      <FocusAwareStatusBar />
      <View className="p-4">
        <View className="mb-6 rounded-lg border border-neutral-200 p-4 dark:border-neutral-700">
          <Text className="text-lg font-bold">Account</Text>
          <Text className="mt-2 text-neutral-600">Email</Text>
          <Text className="mb-4">{data.email}</Text>
          {data.full_name && (
            <>
              <Text className="text-neutral-600">Full Name</Text>
              <Text>{data.full_name}</Text>
            </>
          )}
          <Text className="mt-2 text-neutral-600">Status</Text>
          <Text>{data.is_active ? 'Active' : 'Inactive'}</Text>
        </View>

        <View className="mb-6 rounded-lg border border-neutral-200 p-4 dark:border-neutral-700">
          <Text className="text-lg font-bold">Permissions</Text>
          <Text className="mt-1 text-neutral-600">
            {data.assigned_scopes.length > 0
              ? data.assigned_scopes.join(', ')
              : 'No special permissions'}
          </Text>
        </View>

        <View className="mb-6 rounded-lg border border-neutral-200 p-4 dark:border-neutral-700">
          <Text className="text-lg font-bold">Payment Information</Text>
          <Text className="mt-1 text-neutral-600">Manage your payment methods and donation history</Text>
          <View className="mt-2">
            <Button
              label="View Payment History"
              onPress={() => {}}
            />
          </View>
        </View>

        <View className="mb-6 rounded-lg border border-neutral-200 p-4 dark:border-neutral-700">
          <Text className="text-lg font-bold">Schedule</Text>
          <Text className="mt-1 text-neutral-600">View your assignments and request time off</Text>
          <View className="mt-2">
            <Button
              label="View Schedule"
              onPress={() => {}}
            />
          </View>
        </View>

        <View className="mb-6 rounded-lg border border-neutral-200 p-4 dark:border-neutral-700">
          <Text className="text-lg font-bold">Integrations</Text>
          <Text className="mt-1 text-neutral-600">Manage connected services and integrations</Text>
          <View className="mt-2">
            <Button
              label="Manage Integrations"
              onPress={() => {}}
            />
          </View>
        </View>

        <View className="mt-8">
          <Button
            label="Sign Out"
            variant="destructive"
            onPress={() => signOut()}
          />
        </View>
      </View>
    </ScrollView>
  );
}
