import { FlashList } from '@shopify/flash-list';

import { Stack } from 'expo-router';

import * as React from 'react';
import {
  ActivityIndicator,
  EmptyList,
  FocusAwareStatusBar,
  Text,
  View,
} from '@/components/ui';
import { usePaymentHistory } from './api';

function formatCurrency(amountCents: number, currency: string): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency.toUpperCase(),
  }).format(amountCents / 100);
}

function PaymentItem({ payment }: { payment: { amount_cents: number; currency: string; status: string; created_on: string } }) {
  return (
    <View className="border-b border-neutral-200 px-4 py-3 dark:border-neutral-700">
      <Text className="font-semibold">{formatCurrency(payment.amount_cents, payment.currency)}</Text>
      <Text className="mt-1 text-neutral-600 capitalize">{payment.status}</Text>
      <Text className="mt-1 text-xs text-neutral-400">
        {new Date(payment.created_on).toLocaleDateString()}
      </Text>
    </View>
  );
}

export function PaymentsScreen() {
  const { data, isPending } = usePaymentHistory({ variables: { limit: 100 } });

  if (isPending) {
    return (
      <View className="flex-1 justify-center">
        <Stack.Screen options={{ title: 'Payments', headerBackTitle: 'Home' }} />
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View className="flex-1">
      <Stack.Screen options={{ title: 'Payments', headerBackTitle: 'Home' }} />
      <FocusAwareStatusBar />
      {data && data.length > 0
        ? (
            <FlashList
              data={data}
              renderItem={({ item }) => <PaymentItem payment={item} />}
              keyExtractor={item => item.id}
            />
          )
        : (
            <View className="flex-1 items-center justify-center">
              <EmptyList />
              <Text className="mt-2 text-neutral-400">No payments yet</Text>
            </View>
          )}
    </View>
  );
}
