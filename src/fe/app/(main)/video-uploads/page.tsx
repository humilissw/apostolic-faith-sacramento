'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://localhost:8000/';
const API_V1 = 'api/v1';

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

interface SermonCardData {
  videoUri: string;
  sermonTitle: string;
  speaker: string;
  createDate: string;
}

export default function VideoUploadsPage() {
  const [videos, setVideos] = useState<VideoUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
          setError(err instanceof Error ? err.message : 'Unknown error');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchVideos();
    return () => { cancelled = true; };
  }, []);

  const cards: SermonCardData[] = videos.map((v) => ({
    videoUri: `${API_BASE}${API_V1}${v.download_url}`,
    sermonTitle: v.upload_name || 'Untitled',
    speaker: v.speaker_name || 'Unknown',
    createDate: v.created_on,
  }));

  if (loading) return <div className="flex justify-center items-center min-h-dvh"><p>Loading...</p></div>;
  if (error) return <div className="flex justify-center items-center min-h-dvh"><p className="text-red-600">{error}</p></div>;

  return (
    <div className="">
      <div className="flex flex-col justify-center bg-white">
        <div className="flex justify-center items-center h-50 bg-[url('../public/media.jpg')] bg-cover bg-center md:h-100 lg:h-100">
          <h1 className="text-white text-5xl md:text-6xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
            Video Uploads
          </h1>
        </div>
        <div className="flex justify-center pt-20">
          <h1 className="text-4xl md:text-6xl text-center tracking-wider">Latest Services</h1>
        </div>
        <div className="flex justify-center pt-15">
          {cards.slice(0, 1).map((data, index) => (
            <div key={index}>
              {index === 0 ? (
                <Link target="_blank" key={index} href={data.videoUri}>
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
                          <h1 className="xs:text-xl md:text-4xl">{data.sermonTitle}</h1>
                          <h1 className="text-black/40 font-normal">{data.speaker}</h1>
                          <h1 className="text-black/40 font-normal">{new Date(data.createDate).toLocaleDateString('en-US')}</h1>
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ) : null}
            </div>
          ))}
        </div>

        <div className="flex flex-wrap gap-x-5 gap-y-5 justify-center py-15 sm:px-10 md:px-20 lg:px-40 xl:px-80">
          {cards.slice(1).map((data, index) => (
            <div key={index}>
              <Link href={data.videoUri} target="_blank">
                <div className="rounded-xl shadow-xl/10">
                  <div className="flex xs:h-100 xs:w-60 md:h-60 md:w-140">
                    <div className="flex flex-col md:flex-row items-center">
                      <Image
                        src="/sacAFC.jpg"
                        width={300}
                        height={300}
                        alt="Picture of the Apostolic Faith Church"
                        className="h-50 md:h-60 rounded-t-xl md:rounded-l-xl "
                      />
                      <div className="flex flex-col px-5 pt-3 w-full font-medium font-noto-sans">
                        <h1 className="text-xl">{data.sermonTitle}</h1>
                        <h1 className="text-black/40 font-normal">{data.speaker}</h1>
                        <h1 className="text-black/40 font-normal">{new Date(data.createDate).toLocaleDateString('en-US')}</h1>
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
