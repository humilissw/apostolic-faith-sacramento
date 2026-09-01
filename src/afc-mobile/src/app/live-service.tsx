import { StyleSheet } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing } from '@/constants/theme';

export default function LiveServiceScreen() {
  return (
    <ThemedView style={styles.screen} type="backgroundElement">
      <ThemedView style={styles.content}>
        <ThemedText type="title" style={styles.header}>
          Live Service
        </ThemedText>
        <ThemedText type="default" style={styles.body}>
          Join us for live streaming every Sunday.
        </ThemedText>
        <ThemedText type="subtitle" style={styles.schedule}>
          Sunday Service
        </ThemedText>
        <ThemedText type="default" style={styles.time}>
          10:00 AM
        </ThemedText>
        <ThemedText type="small" style={styles.address}>
          7842 Elmont Ave, Elverta, CA 95626
        </ThemedText>
      </ThemedView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  content: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: Spacing.three },
  header: { textAlign: 'center' },
  body: { textAlign: 'center', paddingHorizontal: Spacing.four, lineHeight: 24 },
  schedule: { marginTop: Spacing.four },
  time: { fontSize: 24, fontWeight: '600', marginVertical: Spacing.two },
  address: { opacity: 0.7 },
});
