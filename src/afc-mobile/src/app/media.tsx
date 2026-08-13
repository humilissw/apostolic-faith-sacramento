import { useEffect, useState } from 'react';
import { FlatList, Image, ScrollView, StyleSheet, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing } from '@/constants/theme';
import { fetchVideos, type SermonVideo } from '@/lib/api';

function VideoCard({ video }: { video: SermonVideo }) {
  return (
    <ThemedView style={styles.card} type="backgroundElement">
      <View style={styles.cardContent}>
        <ThemedText type="subtitle" style={styles.cardTitle}>
          {video.upload_name}
        </ThemedText>
        <ThemedText type="small" style={styles.cardMeta}>
          {video.speaker_name || 'Unknown Speaker'}
        </ThemedText>
        <ThemedText type="default" style={styles.cardMeta}>
          {new Date(video.media_association_date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </ThemedText>
      </View>
    </ThemedView>
  );
}

export default function MediaScreen() {
  const [videos, setVideos] = useState<SermonVideo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVideos()
      .then((res) => setVideos(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <ThemedView style={styles.center} type="backgroundElement">
        <ThemedText>Loading media...</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.screen} type="backgroundElement">
      <ThemedText type="title" style={styles.header}>
        Media
      </ThemedText>
      <ScrollView style={styles.list} contentContainerStyle={styles.listContent}>
        {videos.length === 0 ? (
          <ThemedText style={styles.empty}>No media available.</ThemedText>
        ) : (
          <FlatList
            data={videos}
            numColumns={2}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.grid}
            columnWrapperStyle={styles.gridRow}
            renderItem={({ item }) => <VideoCard video={item} />}
            scrollEnabled={false}
          />
        )}
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { textAlign: 'center', paddingVertical: Spacing.four },
  list: { flex: 1 },
  listContent: { padding: Spacing.three },
  grid: { paddingBottom: Spacing.three },
  gridRow: { justifyContent: 'space-between' },
  card: {
    flex: 1,
    maxWidth: '48%',
    borderRadius: Spacing.two,
    padding: Spacing.two,
    gap: Spacing.one,
    marginBottom: Spacing.two,
  },
  cardContent: { gap: Spacing.half },
  cardTitle: { fontWeight: '600' },
  cardMeta: { opacity: 0.7 },
  empty: { textAlign: 'center', paddingVertical: Spacing.four, opacity: 0.7 },
});
