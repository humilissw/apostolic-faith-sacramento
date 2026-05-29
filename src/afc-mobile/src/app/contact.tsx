import { Linking, StyleSheet, TouchableOpacity, Text } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing } from '@/constants/theme';

export default function ContactScreen() {
  return (
    <ThemedView style={styles.screen} type="backgroundElement">
      <ThemedText type="title" style={styles.header}>
        Contact Us
      </ThemedText>
      <ThemedView style={styles.items} type="backgroundElement">
        <ContactRow
          label="Address"
          value="7842 Elmont Ave, Elverta, CA 95626"
          onTap={() => Linking.openURL('https://maps.google.com/?q=7842+Elmont+Ave+Elverta+CA+95626')}
        />
        <ContactRow
          label="Phone"
          value="(530) 515-8440"
          onTap={() => Linking.openURL('tel:+15305158440')}
        />
        <ContactRow
          label="Email"
          value="info@afcsac.com"
          onTap={() => Linking.openURL('mailto:info@afcsac.com')}
        />
        <Text className="text-blue-500 text-5xl">Hello There</Text>
      </ThemedView>
    </ThemedView>
  );
}

function ContactRow({ label, value, onTap }: { label: string; value: string; onTap?: () => void }) {
  return (
    <TouchableOpacity
      style={styles.row}
      onPress={onTap}
      hitSlop={Spacing.two}
      activeOpacity={0.6}
    >
      <ThemedView style={styles.rowInner} type="backgroundElement">
        <ThemedText type="subtitle" style={styles.rowLabel}>
          {label}
        </ThemedText>
        <ThemedText type="default" style={styles.rowValue}>
          {value}
        </ThemedText>
      </ThemedView>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  header: { textAlign: 'center', paddingVertical: Spacing.four },
  items: { padding: Spacing.three, gap: Spacing.two },
  row: { marginBottom: Spacing.half },
  rowInner: { borderRadius: Spacing.two, padding: Spacing.three, gap: Spacing.half },
  rowLabel: { fontWeight: '600' },
  rowValue: { lineHeight: 22 },
});
