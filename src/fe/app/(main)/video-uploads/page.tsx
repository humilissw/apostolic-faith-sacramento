"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { AnimatedSheet } from "@/components/animated-sheet";
import UploadForm from "@/components/upload-form";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

interface VideoUpload {
  id: string;
  upload_location: string;
  upload_name: string;
  description: string | null;
  reference_text: string | null;
  speaker_name: string | null;
  media_association_date: string;
  created_on: string;
  updated_on: string | null;
  download_url: string;
}

interface VideoUploadsResponse {
  data: VideoUpload[];
  count: number;
}

export default function VideoUploadsPage() {
  const [videos, setVideos] = useState<VideoUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function fetchVideos() {
      try {
        const res = await fetch(`${API_BASE}${API_V1}/video-uploads/`);
        if (!res.ok) throw new Error(`Failed to load: ${res.status}`);
        const json: VideoUploadsResponse = await res.json();
        if (!cancelled) setVideos(json.data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unknown error");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchVideos();
    return () => {
      cancelled = true;
    };
  }, []);

  function handleUploadSuccess() {
    setOpen(false);
    fetch(`${API_BASE}${API_V1}/video-uploads/`)
      .then((res) => res.json())
      .then((json: VideoUploadsResponse) => setVideos(json.data))
      .catch(() => setError("Failed to refresh after upload"));
  }

  if (loading)
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Loading...</p>
      </div>
    );
  if (error)
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p className="text-red-600">{error}</p>
      </div>
    );

  return (
    <div className="">
      <div className="flex flex-col justify-center bg-white">
        <div className="flex justify-center items-center h-50 bg-[url('../public/media.jpg')] bg-cover bg-center md:h-100 lg:h-100">
          <h1 className="text-white text-5xl md:text-6xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
            Video Uploads
          </h1>
        </div>

        <div className="flex justify-center px-6 py-8 gap-8">
          <AnimatedSheet
            open={open}
            onOpenChange={setOpen}
            title="Upload a Video"
            className="max-w-lg"
            triggerContent={
              <Button className="font-noto-sans bg-black text-white hover:bg-gray-700 text-lg px-8 py-6">
                Upload a Video
              </Button>
            }
          >
            <div className="mt-4 pb-6 px-2">
              <UploadForm onSuccess={handleUploadSuccess} />
            </div>
          </AnimatedSheet>
        </div>

        {videos.length === 0 ? (
          <p className="flex justify-center text-gray-500 py-10">No videos uploaded yet.</p>
        ) : (
          <div className="flex flex-wrap gap-x-5 gap-y-5 justify-center py-15 sm:px-10 md:px-20 lg:px-40 xl:px-80">
            {videos.map((v) => (
              <div key={v.id}>
                <Link href={v.download_url.startsWith("http") ? v.download_url : `${API_BASE}${API_V1}${v.download_url}`} target="_blank" rel="noopener noreferrer">
                  <div className="rounded-xl shadow-xl/10">
                    <div className="flex xs:h-100 xs:w-60 md:h-60 md:w-140">
                      <div className="flex flex-col md:flex-row items-center">
                        <Image
                          src="/sacAFC.jpg"
                          width={300}
                          height={300}
                          alt="Apostolic Faith Church"
                          className="h-50 md:h-60 rounded-t-xl md:rounded-l-xl"
                        />
                        <div className="flex flex-col px-5 pt-3 w-full font-medium font-noto-sans">
                          <h1 className="text-xl">{v.upload_name || "Untitled"}</h1>
                          <h1 className="text-black/40 font-normal">{v.speaker_name || "Unknown"}</h1>
                          <h1 className="text-black/40 font-normal">
                            {new Date(v.created_on).toLocaleDateString("en-US")}
                          </h1>
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
