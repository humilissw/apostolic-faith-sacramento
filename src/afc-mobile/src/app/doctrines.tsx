import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing } from '@/constants/theme';
import { fetchDoctrines, type DoctrineItem } from '@/lib/api';

function DoctrineCard({ item }: { item: DoctrineItem }) {
  return (
    <ThemedView style={styles.card} type="backgroundElement">
      <ThemedText type="subtitle" style={styles.title}>
        {item.title}
      </ThemedText>
      <ThemedText type="default" style={styles.content}>
        {item.content}
      </ThemedText>
    </ThemedView>
  );
}

export default function DoctrinesScreen() {
  const [doctrines, setDoctrines] = useState<DoctrineItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDoctrines()
      .then(setDoctrines)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <ThemedView style={styles.center} type="backgroundElement">
        <ThemedText>Loading beliefs...</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.screen} type="backgroundElement">
      <ThemedText type="title" style={styles.header}>
        Our Beliefs
      </ThemedText>
      <ScrollView style={styles.list} contentContainerStyle={styles.listContent}>
        {doctrines.map((d) => (
          <DoctrineCard key={d.id} item={d} />
        ))}
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { textAlign: 'center', paddingVertical: Spacing.four },
  list: { flex: 1 },
  listContent: { padding: Spacing.three, gap: Spacing.two },
  card: { borderRadius: Spacing.two, padding: Spacing.three, gap: Spacing.two },
  title: { fontWeight: '600' },
  content: { lineHeight: 24 },
});
