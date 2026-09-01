"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import Image from "next/image";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

interface VideoUpload {
  id: string;
  upload_location: string;
  upload_name: string;
  speaker_name: string | null;
  media_association_date: string;
  created_on: string;
  updated_on: string | null;
  owner_id: string;
  reference_text: string | null;
  description: string | null;
}

interface VideosResponse {
  data: VideoUpload[];
  count: number;
}

export default function Media() {
  const [videos, setVideos] = useState<VideoUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchVideos() {
      try {
        const res = await fetch(`${API_BASE}${API_V1}/video-uploads/`);
        if (!res.ok) throw new Error(`Response: ${res.status}`);
        const json: VideosResponse = await res.json();
        if (!cancelled) setVideos(json.data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchVideos();
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="">
      <div className="flex flex-col justify-center bg-white">
        <div className="flex justify-center items-center h-50 bg-[url('../public/media.jpg')] bg-cover bg-center md:h-100 lg:h-100">
          <h1 className="text-white text-5xl md:text-6xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
            Media
          </h1>
        </div>
        <div className="flex justify-center pt-20">
          <h1 className="text-4xl md:text-6xl text-center tracking-wider">
            Latest Services
          </h1>
        </div>
        <div className="flex justify-center pt-15">
          {videos.length > 0 ? (
            <Link
              target="_blank"
              rel="noopener noreferrer"
              href={videos[0].upload_location.startsWith("http") ? videos[0].upload_location : `${API_BASE}${API_V1}${videos[0].upload_location}`}
            >
              <div className="rounded-xl shadow-xl/20">
                <div className="flex xs:h-100 xs:w-60 md:h-75 md:w-150 lg:h-100 lg:w-200">
                  <div className="flex flex-col md:flex-row items-center">
                    <Image
                      src="/sacAFC.jpg"
                      width={500}
                      height={500}
                      alt="Picture of the Apostolic Faith Church"
                      className="xs:h-50 md:h-75 xs:rounded-t-xl md:rounded-l-xl 2xl:h-100"
                    />
                    <div className="flex flex-col px-5 pt-3 w-full font-medium font-noto-sans">
                      <h1 className="xs:text-xl md:text-4xl">
                        {videos[0].upload_name || "Untitled"}
                      </h1>
                      <h1 className="text-black/40 font-normal">
                        {videos[0].speaker_name || "Unknown"}
                      </h1>
                      <h1 className="text-black/40 font-normal">
                        {new Date(videos[0].media_association_date).toLocaleDateString("en-US")}
                      </h1>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ) : (
            <p className="text-gray-500 py-10">No services available.</p>
          )}
        </div>

        <div className="flex flex-wrap gap-x-5 gap-y-5 justify-center py-15 sm:px-10 md:px-20 lg:px-40 xl:px-80">
          {videos.slice(1).map((v) => (
            <div key={v.id}>
              <Link
                href={v.upload_location.startsWith("http") ? v.upload_location : `${API_BASE}${API_V1}${v.upload_location}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className="rounded-xl shadow-xl/10">
                  <div className="flex xs:h-100 xs:w-60 md:h-60 md:w-140">
                    <div className="flex flex-col md:flex-row items-center">
                      <Image
                        src="/sacAFC.jpg"
                        width={300}
                        height={300}
                        alt="Picture of the Apostolic Faith Church"
                        className="h-50 md:h-60 rounded-t-xl md:rounded-l-xl"
                      />
                      <div className="flex flex-col px-5 pt-3 w-full font-medium font-noto-sans">
                        <h1 className="text-xl">{v.upload_name || "Untitled"}</h1>
                        <h1 className="text-black/40 font-normal">
                          {v.speaker_name || "Unknown"}
                        </h1>
                        <h1 className="text-black/40 font-normal">
                          {new Date(v.media_association_date).toLocaleDateString("en-US")}
                        </h1>
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
