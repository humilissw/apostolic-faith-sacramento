import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';
import { useRouter } from 'expo-router';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing } from '@/constants/theme';
import { fetchVideos, type SermonVideo } from '@/lib/api';

function SermonCard({ sermon }: { sermon: SermonVideo }) {
  const router = useRouter();

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push(`/sermons/${sermon.id}` as any)}
      hitSlop={Spacing.two}
      activeOpacity={0.6}
    >
      <ThemedView style={styles.cardInner} type="backgroundElement">
        <ThemedText type="subtitle" style={styles.cardTitle}>
          {sermon.upload_name}
        </ThemedText>
        <ThemedText type="small" style={styles.cardMeta}>
          {sermon.speaker_name ? `${sermon.speaker_name} ` : ''}
          {new Date(sermon.media_association_date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </ThemedText>
        {sermon.description ? (
          <ThemedText type="default" style={styles.cardDescription}>
            {sermon.description}
          </ThemedText>
        ) : null}
      </ThemedView>
    </TouchableOpacity>
  );
}

export default function SermonsScreen() {
  const [videos, setVideos] = useState<SermonVideo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVideos()
      .then((res) => setVideos(res.data))
      .catch(() => setVideos([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <ThemedView style={styles.center} type="backgroundElement">
        <ThemedText>Loading sermons...</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.screen} type="backgroundElement">
      <ThemedView style={styles.heroSection}>
        <ThemedText type="title" style={styles.heroTitle}>
          Sermons
        </ThemedText>
      </ThemedView>
      <ScrollView style={styles.list} contentContainerStyle={styles.listContent}>
        {videos.length === 0 ? (
          <ThemedText type="default" style={styles.empty}>
            No sermons available.
          </ThemedText>
        ) : (
          videos.map((v) => <SermonCard key={v.id} sermon={v} />)
        )}
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  heroSection: { alignItems: 'center', paddingVertical: Spacing.five },
  heroTitle: { textAlign: 'center' },
  list: { flex: 1 },
  listContent: { padding: Spacing.three, gap: Spacing.two },
  card: { borderRadius: Spacing.two },
  cardInner: {
    padding: Spacing.three,
    gap: Spacing.one,
  },
  cardTitle: { fontWeight: '600' },
  cardMeta: { opacity: 0.7 },
  cardDescription: { marginTop: Spacing.half },
  empty: { textAlign: 'center', paddingVertical: Spacing.four, opacity: 0.7 },
});
