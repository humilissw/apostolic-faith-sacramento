import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing } from '@/constants/theme';
import { fetchDonationConfigs, type DonationConfig } from '@/lib/api';

function DonationCard({ config }: { config: DonationConfig }) {
  const dollars = config.amount_cents / 100;
  return (
    <ThemedView style={styles.card} type="backgroundElement">
      <ThemedText type="title" style={styles.amount}>
        ${dollars.toFixed(2)}
      </ThemedText>
      <ThemedText type="default">{config.label}</ThemedText>
      <ThemedText type="small" style={styles.freq}>
        {config.frequency === 'recurring' ? 'Monthly' : 'One-time'}
      </ThemedText>
    </ThemedView>
  );
}

export default function DonateScreen() {
  const [configs, setConfigs] = useState<DonationConfig[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDonationConfigs()
      .then(setConfigs)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <ThemedView style={styles.center} type="backgroundElement">
        <ThemedText>Loading donation options...</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.screen} type="backgroundElement">
      <ThemedText type="title" style={styles.header}>
        Support Our Church
      </ThemedText>
      <ThemedText type="default" style={styles.subtitle}>
        Your generous donations help us spread the Gospel and serve our community.
      </ThemedText>
      <ScrollView style={styles.list} contentContainerStyle={styles.listContent}>
        {configs.length === 0 ? (
          <ThemedText style={styles.empty}>No donation options available.</ThemedText>
        ) : (
          configs.map((c) => <DonationCard key={c.id} config={c} />)
        )}
      </ScrollView>
      <ThemedView style={styles.footer} type="backgroundElement">
        <ThemedText type="small" style={styles.footerText}>
          Secure payment processing via Stripe
        </ThemedText>
      </ThemedView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { textAlign: 'center', paddingVertical: Spacing.four },
  subtitle: { textAlign: 'center', paddingHorizontal: Spacing.four, lineHeight: 22 },
  list: { flex: 1 },
  listContent: { padding: Spacing.three, gap: Spacing.two },
  card: {
    borderRadius: Spacing.two,
    padding: Spacing.three,
    gap: Spacing.one,
    alignItems: 'center',
  },
  amount: { fontSize: 32 },
  freq: { opacity: 0.7 },
  footer: { padding: Spacing.three, alignItems: 'center' },
  footerText: { opacity: 0.7 },
  empty: { textAlign: 'center', paddingVertical: Spacing.four, opacity: 0.7 },
});
