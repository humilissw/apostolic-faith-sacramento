"use client"

import { useEffect, useState } from "react";

import {
    fetchAllArchivedMedia,
  type ArchivedMediaResponse,
} from "@/lib/api";

// const tracks = [
//   { name: "Song 1", mp3: "/audio/song1.mp3", ogg: "/audio/song1.ogg" },
//   { name: "Song 2", mp3: "/audio/song2.mp3", ogg: "/audio/song2.ogg" },
// ];

export default function ArchivedMediaPage() {

      const [media, setMedia] = useState<ArchivedMediaResponse[]>([]);
      const [loading, setLoading] = useState(true);
      const [error, setError] = useState<string | null>(null);
    //   const [deletingId, setDeletingId] = useState<string | null>(null);
    //   const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
    //   const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
    
      useEffect(() => {
        let cancelled = false;
        async function load() {
          try {
            const timeout = new Promise((_, rej) => setTimeout(() => rej(new Error("Request timed out. Is the API running?")), 15000));
            const res = await Promise.race([fetchAllArchivedMedia(), timeout]);
            const data = res as Awaited<ReturnType<typeof fetchAllArchivedMedia>>;
            if (!cancelled) setMedia(data.data);
          } catch (err) {
            if (!cancelled) {
                setError(err instanceof Error ? err.message : "Failed to load");
            }
          } finally {
            if (!cancelled) setLoading(false);
          }
        }
        load();
        return () => { cancelled = true; };
      }, []);


  return (
    <div className="min-h-screen bg-gray-50 p-8">
        hello
      <div className="mx-auto max-w-2xl">
        <h1 className="mb-6 text-2xl font-bold text-gray-900">
          Archived Media
        </h1>

        <div className="space-y-4">
          {media.length === 0 ? (
            <p className="text-muted-foreground">No media available</p>
          ) :
          
          (media.map((media) => (
            <div
              key={media.id}
              className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
            >
              <p className="mb-2 font-medium text-gray-700">Media</p>
              <audio controls className="w-full">
                <source src={media.file_location} type="audio/mpeg" />
                {/* <source src={media.ogg} type="audio/ogg" /> */}
                Your browser does not support the audio element.
              </audio>
            </div>
          )))}
        </div>
      </div>
    </div>
  );
}